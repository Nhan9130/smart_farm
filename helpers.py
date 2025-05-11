import logging
from datetime import datetime, timedelta
from models import db, SensorData, MotorState, AnimalDetection

# Thiết lập logging
logger = logging.getLogger(__name__)

def get_latest_data():
    """
    Lấy dữ liệu mới nhất từ các cảm biến và trạng thái động cơ
    Trả về dưới dạng dictionary
    """
    try:
        # Lấy dữ liệu cảm biến mới nhất
        latest_sensor_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
        
        # Lấy trạng thái động cơ mới nhất
        latest_motor_state = MotorState.query.order_by(MotorState.timestamp.desc()).first()
        
        # Lấy dữ liệu phát hiện gia súc mới nhất
        latest_animal_detection = AnimalDetection.query.order_by(AnimalDetection.timestamp.desc()).first()
        
        result = {
            'sensor_data': latest_sensor_data.to_dict() if latest_sensor_data else None,
            'motor_state': latest_motor_state.to_dict() if latest_motor_state else None,
            'animal_detection': latest_animal_detection.to_dict() if latest_animal_detection else None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu mới nhất: {e}")
        return {
            'sensor_data': None,
            'motor_state': None,
            'animal_detection': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        }

def get_historical_data(days=1):
    """
    Lấy dữ liệu lịch sử từ các cảm biến trong khoảng thời gian nhất định
    
    Args:
        days (int): Số ngày dữ liệu cần lấy, mặc định là 1 ngày
        
    Returns:
        dict: Dictionary chứa dữ liệu lịch sử
    """
    try:
        # Tính toán thời điểm bắt đầu
        start_date = datetime.now() - timedelta(days=days)
        
        # Lấy dữ liệu cảm biến
        sensor_data = SensorData.query.filter(
            SensorData.timestamp >= start_date
        ).order_by(SensorData.timestamp.asc()).all()
        
        # Lấy trạng thái động cơ
        motor_states = MotorState.query.filter(
            MotorState.timestamp >= start_date
        ).order_by(MotorState.timestamp.asc()).all()
        
        # Lấy dữ liệu phát hiện gia súc
        animal_detections = AnimalDetection.query.filter(
            AnimalDetection.timestamp >= start_date
        ).order_by(AnimalDetection.timestamp.asc()).all()
        
        # Chuyển đổi kết quả sang dạng list các dictionary
        sensor_data_list = [data.to_dict() for data in sensor_data]
        motor_states_list = [state.to_dict() for state in motor_states]
        animal_detections_list = [detection.to_dict() for detection in animal_detections]
        
        # Tạo các danh sách riêng cho từng loại dữ liệu để vẽ biểu đồ
        timestamps = [data['timestamp'] for data in sensor_data_list] if sensor_data_list else []
        rain_data = [data['rain_percent'] for data in sensor_data_list] if sensor_data_list else []
        soil_moisture_data = [data['soil_moisture_percent'] for data in sensor_data_list] if sensor_data_list else []
        ph_data = [data['ph_value'] for data in sensor_data_list] if sensor_data_list else []
        
        # Tạo dữ liệu cho biểu đồ trạng thái động cơ
        motor_timestamps = [state['timestamp'] for state in motor_states_list] if motor_states_list else []
        cover_motor_states = [1 if state['cover_motor_active'] else 0 for state in motor_states_list] if motor_states_list else []
        water_motor_states = [1 if state['water_motor_active'] else 0 for state in motor_states_list] if motor_states_list else []
        
        # Tạo dữ liệu cho biểu đồ phát hiện gia súc
        detection_timestamps = [det['timestamp'] for det in animal_detections_list] if animal_detections_list else []
        detection_counts = [det['count'] for det in animal_detections_list] if animal_detections_list else []
        
        result = {
            'timestamps': timestamps,
            'rain_data': rain_data,
            'soil_moisture_data': soil_moisture_data,
            'ph_data': ph_data,
            'motor_timestamps': motor_timestamps,
            'cover_motor_states': cover_motor_states,
            'water_motor_states': water_motor_states,
            'detection_timestamps': detection_timestamps,
            'detection_counts': detection_counts,
            'sensor_data': sensor_data_list,
            'motor_states': motor_states_list,
            'animal_detections': animal_detections_list
        }
        
        return result
    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu lịch sử: {e}")
        return {
            'timestamps': [],
            'rain_data': [],
            'soil_moisture_data': [],
            'ph_data': [],
            'motor_timestamps': [],
            'cover_motor_states': [],
            'water_motor_states': [],
            'detection_timestamps': [],
            'detection_counts': [],
            'sensor_data': [],
            'motor_states': [],
            'animal_detections': [],
            'error': str(e)
        }

def format_timestamp(timestamp, format='%H:%M:%S'):
    """
    Định dạng timestamp theo định dạng mong muốn
    
    Args:
        timestamp (str): Timestamp dạng chuỗi
        format (str): Định dạng đầu ra, mặc định là giờ:phút:giây
        
    Returns:
        str: Timestamp đã định dạng
    """
    try:
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format)
    except Exception as e:
        logger.error(f"Lỗi khi định dạng timestamp: {e}")
        return timestamp