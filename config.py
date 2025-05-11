import os

class Config:
    """Cấu hình cho ứng dụng Flask"""
    # Flask configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'smart_agriculture_secret')
    DEBUG = True
    
    # Instance path - make sure exists
    INSTANCE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
    if not os.path.exists(INSTANCE_PATH):
        os.makedirs(INSTANCE_PATH)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(INSTANCE_PATH, "smart_agriculture.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Chế độ phần cứng - đặt False để sử dụng mô phỏng
    HARDWARE_MODE = True
    
    # Cấu hình ADS1115
    ADS_ADDRESS = 0x48  # Địa chỉ I2C mặc định của ADS1115
    ADS_GAIN = 1        # Độ khuếch đại của ADS1115
    
    # Cấu hình GPIO cho L298N
    MOTOR_IN1_PIN = 17  # GPIO cho điều khiển động cơ mái che
    MOTOR_IN2_PIN = 18  # GPIO cho điều khiển động cơ mái che
    MOTOR_IN3_PIN = 27  # GPIO cho điều khiển động cơ tưới nước
    MOTOR_IN4_PIN = 22  # GPIO cho điều khiển động cơ tưới nước
    
    # Cấu hình ngưỡng cảm biến
    RAIN_THRESHOLD = 40.0        # Ngưỡng % để xác định trời mưa
    SOIL_MOISTURE_THRESHOLD = 30.0  # Ngưỡng % để xác định đất khô
    
    # Cấu hình camera
    CAMERA_RESOLUTION = (640, 480)  # Độ phân giải camera
    CAMERA_FRAMERATE = 24           # Số khung hình mỗi giây
    
    # Cấu hình phát hiện gia súc
    MODEL_PATH = 'models/animal_detection_model.tflite'  # Đường dẫn đến model TensorFlow Lite
    DETECTION_THRESHOLD = 0.5       # Ngưỡng tin cậy cho phát hiện gia súc
