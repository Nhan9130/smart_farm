import os
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO
import threading
import time
import random
from datetime import datetime
from models import db, SensorData, MotorState, AnimalDetection, setup_db
from utils.helpers import get_latest_data, get_historical_data
from config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Khởi tạo Flask app
app = Flask(__name__, template_folder='templates')
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET", "smart_agriculture_secret")

# Khởi tạo SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Khởi tạo database
setup_db(app)
from hardware.sensors import SensorManager
from hardware.motors import MotorController
from hardware.camera import Camera
from utils.camera_detection import AnimalDetector

sensor_manager = SensorManager(use_hardware=True)
motor_controller = MotorController(use_hardware=True)
camera = Camera(use_hardware=True)
animal_detector = AnimalDetector()

# Biến toàn cục để lưu trạng thái tự động
auto_mode = True
running = True

def sensor_loop():
    """Hàm đọc dữ liệu từ cảm biến và điều khiển động cơ trong chế độ tự động"""
    global running, auto_mode
    
    logger.info("Bắt đầu vòng lặp đọc cảm biến")
    
    while running:
        try:
            if sensor_manager:
                # Đọc dữ liệu từ cảm biến
                rain_value = sensor_manager.read_rain_sensor()
                soil_moisture = sensor_manager.read_soil_moisture_sensor()
                ph_value = sensor_manager.read_ph_sensor()
                
                # Lưu vào database
                sensor_data = SensorData()
                sensor_data.rain_percent = rain_value
                sensor_data.soil_moisture_percent = soil_moisture
                sensor_data.ph_value = ph_value
                with app.app_context():
                    db.session.add(sensor_data)
                    db.session.commit()
                
                # Gửi dữ liệu qua WebSocket
                socketio.emit('sensor_data', {
                    'rain': rain_value,
                    'soil_moisture': soil_moisture,
                    'ph': ph_value,
                    'timestamp': time.strftime('%H:%M:%S')
                })
                
                # Điều khiển tự động
                if auto_mode and motor_controller:
                    # Nếu trời mưa (giá trị > 40%), bật động cơ mái che
                    if rain_value > 40:
                        motor_controller.activate_cover_motor()
                    else:
                        motor_controller.stop_cover_motor()
                    
                    # Nếu đất khô (độ ẩm < 30%), bật động cơ tưới nước
                    if soil_moisture < 30:
                        motor_controller.activate_water_motor()
                    else:
                        motor_controller.stop_water_motor()
                    
                    # Lưu trạng thái động cơ vào database
                    with app.app_context():
                        motor_state = MotorState()
                        motor_state.cover_motor_active = motor_controller.cover_motor_active
                        motor_state.water_motor_active = motor_controller.water_motor_active
                        db.session.add(motor_state)
                        db.session.commit()
                    
                    # Gửi trạng thái động cơ qua WebSocket
                    socketio.emit('motor_state', {
                        'cover_motor': motor_controller.cover_motor_active,
                        'water_motor': motor_controller.water_motor_active
                    })
            
            # Chờ 1 giây trước khi đọc lại
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp cảm biến: {e}")
            time.sleep(5)  # Tạm dừng nếu có lỗi

# Camera processing loop
def camera_loop():
    """Hàm xử lý dữ liệu hình ảnh từ camera để phát hiện gia súc"""
    global running
    
    logger.info("Bắt đầu vòng lặp xử lý camera")
    
    while running:
        try:
            if camera and animal_detector:
                # Chụp ảnh từ camera
                frame = camera.capture_frame()
                
                # Phát hiện gia súc
                has_animals, animals_count, processed_image = animal_detector.detect_animals(frame)
                
                # Gửi kết quả qua WebSocket
                socketio.emit('camera_data', {
                    'has_animals': has_animals,
                    'animals_count': animals_count,
                    'timestamp': time.strftime('%H:%M:%S')
                })
                
                # Lưu hình ảnh đã xử lý vào bộ nhớ đệm để hiển thị
                camera.set_last_processed_frame(processed_image)
                
                # Lưu kết quả phát hiện vào database
                with app.app_context():
                    detection = AnimalDetection()
                    detection.detected = has_animals
                    detection.count = animals_count
                    detection.confidence = 0.8 if has_animals else 0.2  # Giá trị mẫu
                    db.session.add(detection)
                    db.session.commit()
            
            # Chờ 2 giây trước khi xử lý tiếp 
            # (để giảm tải cho Raspberry Pi)
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp camera: {e}")
            time.sleep(5)  # Tạm dừng nếu có lỗi

# Bắt đầu các thread xử lý background
sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
camera_thread = threading.Thread(target=camera_loop, daemon=True)

# Khởi động các thread nền
with app.app_context():
    try:
        # Đối với Flask 2.0+, before_first_request không còn được sử dụng
        sensor_thread.start()
        camera_thread.start()
        logger.info("Đã khởi động các thread nền")
    except RuntimeError as e:
        logger.error(f"Lỗi khi khởi động thread: {e}")

# Routes
@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Trang hiển thị dữ liệu từ cảm biến"""
    latest_data = get_latest_data()
    return render_template('dashboard.html', latest_data=latest_data)

@app.route('/camera')
def camera_view():
    """Trang hiển thị hình ảnh từ camera"""
    return render_template('camera.html')

@app.route('/controls')
def controls():
    """Trang điều khiển thủ công"""
    motor_state = None
    if motor_controller:
        motor_state = {
            'cover_motor': motor_controller.cover_motor_active,
            'water_motor': motor_controller.water_motor_active,
            'auto_mode': auto_mode
        }
    return render_template('controls.html', motor_state=motor_state)

@app.route('/settings')
def settings():
    """Trang cài đặt hệ thống"""
    return render_template('settings.html')

# API Routes
@app.route('/api/sensor-data')
def api_sensor_data():
    """API trả về dữ liệu cảm biến lịch sử"""
    days = request.args.get('days', 1, type=int)
    data = get_historical_data(days)
    return jsonify(data)

@app.route('/api/latest-data')
def api_latest_data():
    """API trả về dữ liệu cảm biến mới nhất"""
    data = get_latest_data()
    return jsonify(data)

@app.route('/api/motor/cover', methods=['POST'])
def api_control_cover_motor():
    """API điều khiển động cơ mái che"""
    global auto_mode
    
    if not motor_controller:
        return jsonify({'success': False, 'message': 'Không thể kết nối với bộ điều khiển động cơ'})
    
    action = request.json.get('action')
    
    if action == 'activate':
        motor_controller.activate_cover_motor()
        auto_mode = False
        flash('Đã kích hoạt động cơ mái che', 'success')
    elif action == 'stop':
        motor_controller.stop_cover_motor()
        auto_mode = False
        flash('Đã dừng động cơ mái che', 'success')
    
    return jsonify({
        'success': True, 
        'cover_motor': motor_controller.cover_motor_active,
        'auto_mode': auto_mode
    })

@app.route('/api/motor/water', methods=['POST'])
def api_control_water_motor():
    """API điều khiển động cơ tưới nước"""
    global auto_mode
    
    if not motor_controller:
        return jsonify({'success': False, 'message': 'Không thể kết nối với bộ điều khiển động cơ'})
    
    action = request.json.get('action')
    
    if action == 'activate':
        motor_controller.activate_water_motor()
        auto_mode = False
        flash('Đã kích hoạt động cơ tưới nước', 'success')
    elif action == 'stop':
        motor_controller.stop_water_motor()
        auto_mode = False
        flash('Đã dừng động cơ tưới nước', 'success')
    
    return jsonify({
        'success': True, 
        'water_motor': motor_controller.water_motor_active,
        'auto_mode': auto_mode
    })

@app.route('/api/mode', methods=['POST'])
def api_set_mode():
    """API điều chỉnh chế độ tự động/thủ công"""
    global auto_mode
    
    mode = request.json.get('mode')
    
    if mode == 'auto':
        auto_mode = True
        flash('Đã chuyển sang chế độ tự động', 'success')
    elif mode == 'manual':
        auto_mode = False
        flash('Đã chuyển sang chế độ thủ công', 'success')
    
    return jsonify({'success': True, 'auto_mode': auto_mode})

@app.route('/api/camera/stream')
def api_camera_stream():
    """API để lấy hình ảnh từ camera"""
    if not camera:
        return jsonify({'success': False, 'message': 'Không thể kết nối với camera'})
    
    # Trả về hình ảnh đã xử lý dưới dạng base64
    image_data = camera.get_last_processed_frame_base64()
    return jsonify({'success': True, 'image': image_data})

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Xử lý khi client kết nối WebSocket"""
    logger.debug('Client connected to WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    """Xử lý khi client ngắt kết nối WebSocket"""
    logger.debug('Client disconnected from WebSocket')

@app.teardown_appcontext
def shutdown_app(exception=None):
    """Xử lý khi ứng dụng đóng"""
    global running
    running = False
    logger.info("Đóng ứng dụng...")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
