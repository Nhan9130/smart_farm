import logging
import random
from config import Config

# Thiết lập logging
logger = logging.getLogger(__name__)

# Kiểm tra xem có thể sử dụng phần cứng thật không
try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
    logger.info("Đã nhập thành công thư viện GPIO")
except ImportError:
    HARDWARE_AVAILABLE = False
    logger.warning("Không thể nhập thư viện GPIO, sẽ sử dụng chế độ mô phỏng")

class MotorController:
    """
    Lớp điều khiển động cơ thông qua module L298N
    - Động cơ mái che: kết nối với IN1/IN2 của L298N
    - Động cơ tưới nước: kết nối với IN3/IN4 của L298N
    """
    
    def __init__(self, use_hardware=True):
        """Khởi tạo GPIO và thiết lập chân điều khiển động cơ"""
        self.use_hardware = use_hardware and HARDWARE_AVAILABLE
        
        # Lấy thông số chân GPIO từ cấu hình
        self.MOTOR_IN1_PIN = Config.MOTOR_IN1_PIN
        self.MOTOR_IN2_PIN = Config.MOTOR_IN2_PIN
        self.MOTOR_IN3_PIN = Config.MOTOR_IN3_PIN
        self.MOTOR_IN4_PIN = Config.MOTOR_IN4_PIN
        
        # Thiết lập trạng thái ban đầu cho động cơ
        self.cover_motor_active = False
        self.water_motor_active = False
        
        if self.use_hardware:
            try:
                # Thiết lập chế độ GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                
                # Thiết lập các chân GPIO cho điều khiển động cơ
                GPIO.setup(self.MOTOR_IN1_PIN, GPIO.OUT)
                GPIO.setup(self.MOTOR_IN2_PIN, GPIO.OUT)
                GPIO.setup(self.MOTOR_IN3_PIN, GPIO.OUT)
                GPIO.setup(self.MOTOR_IN4_PIN, GPIO.OUT)
                
                # Khởi động với tất cả động cơ tắt
                self.stop_all_motors()
                
                logger.info("Đã khởi tạo thành công GPIO cho điều khiển động cơ")
            except Exception as e:
                logger.error(f"Lỗi khi khởi tạo GPIO: {e}")
                self.use_hardware = False
        
        if not self.use_hardware:
            logger.info("Sử dụng chế độ mô phỏng điều khiển động cơ")
    
    def activate_cover_motor(self):
        """Kích hoạt động cơ mái che"""
        if self.use_hardware:
            try:
                # Điều khiển chân GPIO để kích hoạt động cơ mái che
                # L298N cần một chân HIGH và một chân LOW để quay theo một chiều
                GPIO.output(self.MOTOR_IN1_PIN, GPIO.HIGH)
                GPIO.output(self.MOTOR_IN2_PIN, GPIO.LOW)
            except Exception as e:
                logger.error(f"Lỗi khi kích hoạt động cơ mái che: {e}")
        
        self.cover_motor_active = True
        logger.info("Kích hoạt động cơ mái che")
    
    def stop_cover_motor(self):
        """Dừng động cơ mái che"""
        if self.use_hardware:
            try:
                # Để dừng động cơ, đặt cả hai chân xuống LOW
                GPIO.output(self.MOTOR_IN1_PIN, GPIO.LOW)
                GPIO.output(self.MOTOR_IN2_PIN, GPIO.LOW)
            except Exception as e:
                logger.error(f"Lỗi khi dừng động cơ mái che: {e}")
        
        self.cover_motor_active = False
        logger.info("Dừng động cơ mái che")
    
    def activate_water_motor(self):
        """Kích hoạt động cơ tưới nước"""
        if self.use_hardware:
            try:
                # Điều khiển chân GPIO để kích hoạt động cơ tưới nước
                GPIO.output(self.MOTOR_IN3_PIN, GPIO.HIGH)
                GPIO.output(self.MOTOR_IN4_PIN, GPIO.LOW)
            except Exception as e:
                logger.error(f"Lỗi khi kích hoạt động cơ tưới nước: {e}")
        
        self.water_motor_active = True
        logger.info("Kích hoạt động cơ tưới nước")
    
    def stop_water_motor(self):
        """Dừng động cơ tưới nước"""
        if self.use_hardware:
            try:
                # Để dừng động cơ, đặt cả hai chân xuống LOW
                GPIO.output(self.MOTOR_IN3_PIN, GPIO.LOW)
                GPIO.output(self.MOTOR_IN4_PIN, GPIO.LOW)
            except Exception as e:
                logger.error(f"Lỗi khi dừng động cơ tưới nước: {e}")
        
        self.water_motor_active = False
        logger.info("Dừng động cơ tưới nước")
    
    def stop_all_motors(self):
        """Dừng tất cả động cơ"""
        self.stop_cover_motor()
        self.stop_water_motor()
    
    def get_motors_state(self):
        """Trả về trạng thái hiện tại của các động cơ"""
        return {
            "cover_motor": self.cover_motor_active,
            "water_motor": self.water_motor_active
        }
    
    def cleanup(self):
        """Dọn dẹp GPIO khi kết thúc"""
        self.stop_all_motors()
        
        if self.use_hardware:
            try:
                # Xóa thiết lập GPIO cho các chân đã sử dụng
                GPIO.cleanup([
                    self.MOTOR_IN1_PIN, 
                    self.MOTOR_IN2_PIN,
                    self.MOTOR_IN3_PIN,
                    self.MOTOR_IN4_PIN
                ])
            except Exception as e:
                logger.error(f"Lỗi khi dọn dẹp GPIO: {e}")
        
        logger.info("Dọn dẹp tài nguyên động cơ")