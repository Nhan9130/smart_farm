import time
import logging
import random
from config import Config

# Thiết lập logging
logger = logging.getLogger(__name__)

# Kiểm tra xem có thể sử dụng phần cứng thật không
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    HARDWARE_AVAILABLE = True
    logger.info("Đã nhập thành công thư viện phần cứng")
except ImportError:
    HARDWARE_AVAILABLE = False
    logger.warning("Không thể nhập thư viện phần cứng, sẽ sử dụng chế độ mô phỏng")

class SensorManager:
    """
    Lớp quản lý các cảm biến thông qua module ADS1115
    - Cảm biến pH: kết nối với kênh A0 của ADS1115
    - Cảm biến độ ẩm đất: kết nối với kênh A1 của ADS1115
    - Cảm biến mưa: kết nối với kênh A2 của ADS1115
    """
    
    def __init__(self, use_hardware=True):
        """Khởi tạo kết nối với ADS1115"""
        self.use_hardware = use_hardware and HARDWARE_AVAILABLE
        
        if self.use_hardware:
            try:
                # Khởi tạo I2C và ADS1115
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.ads = ADS.ADS1115(self.i2c, address=Config.ADS_ADDRESS)
                self.ads.gain = Config.ADS_GAIN
                
                # Thiết lập các kênh analog
                self.ph_chan = AnalogIn(self.ads, ADS.P0)
                self.soil_chan = AnalogIn(self.ads, ADS.P1)
                self.rain_chan = AnalogIn(self.ads, ADS.P2)
                
                logger.info("Đã khởi tạo kết nối thành công với ADS1115")
            except Exception as e:
                logger.error(f"Lỗi khi khởi tạo ADS1115: {e}")
                self.use_hardware = False
        
        if not self.use_hardware:
            # Khởi tạo giá trị giả lập
            self.rain_value = 20.0
            self.soil_moisture = 50.0
            self.ph_value = 6.5
            logger.info("Sử dụng chế độ mô phỏng cảm biến")
    
    def test_connection(self):
        """Kiểm tra kết nối với ADS1115"""
        if self.use_hardware:
            try:
                # Thử đọc một giá trị
                value = self.ph_chan.value
                return True
            except Exception as e:
                logger.error(f"Lỗi khi kiểm tra kết nối ADS1115: {e}")
                return False
        return True  # Trả về True trong chế độ mô phỏng
    
    def read_ph_sensor(self):
        """
        Đọc giá trị từ cảm biến pH (kênh A0)
        Trả về giá trị pH từ 0-14
        """
        if self.use_hardware:
            try:
                # Đọc giá trị từ cảm biến pH
                voltage = self.ph_chan.voltage
                
                # Chuyển đổi sang thang đo pH (0-14)
                # Công thức này cần hiệu chỉnh theo cảm biến thực tế
                ph_value = 3.5 * voltage
                
                # Giới hạn giá trị pH trong khoảng 0-14
                ph_value = max(0, min(14, ph_value))
                
                logger.debug(f"Đọc cảm biến pH: voltage={voltage:.2f}V, pH={ph_value:.2f}")
                return ph_value
            except Exception as e:
                logger.error(f"Lỗi khi đọc cảm biến pH: {e}")
                if hasattr(self, 'ph_value'):
                    return self.ph_value
                return 7.0  # Trả về giá trị trung tính nếu có lỗi
        else:
            # Mô phỏng giá trị pH biến động nhẹ
            self.ph_value += random.uniform(-0.2, 0.2)
            self.ph_value = max(0, min(14, self.ph_value))
            return self.ph_value
    
    def read_soil_moisture_sensor(self):
        """
        Đọc giá trị từ cảm biến độ ẩm đất (kênh A1)
        Trả về giá trị phần trăm (0-100%)
        """
        if self.use_hardware:
            try:
                # Đọc giá trị từ cảm biến độ ẩm đất
                raw_value = self.soil_chan.value
                
                # Chuyển đổi sang phần trăm độ ẩm (0-100%)
                # Giá trị này cần hiệu chỉnh theo cảm biến thực tế
                min_value = 1000    # Giá trị khi đất khô hoàn toàn
                max_value = 18000   # Giá trị khi đất ẩm hoàn toàn
                
                moisture_percent = (raw_value - min_value) / (max_value - min_value) * 100
                moisture_percent = max(0, min(100, moisture_percent))
                
                logger.debug(f"Đọc cảm biến độ ẩm đất: raw={raw_value}, moisture={moisture_percent:.2f}%")
                return moisture_percent
            except Exception as e:
                logger.error(f"Lỗi khi đọc cảm biến độ ẩm đất: {e}")
                if hasattr(self, 'soil_moisture'):
                    return self.soil_moisture
                return 50.0  # Trả về giá trị trung bình nếu có lỗi
        else:
            # Mô phỏng độ ẩm đất giảm dần theo thời gian
            decrease = random.uniform(0, 2) if self.soil_moisture > 50 else random.uniform(0, 0.5)
            self.soil_moisture -= decrease
            self.soil_moisture = max(0, min(100, self.soil_moisture))
            return self.soil_moisture
    
    def read_rain_sensor(self):
        """
        Đọc giá trị từ cảm biến mưa (kênh A2)
        Trả về giá trị phần trăm (0-100%)
        0% là không mưa, 100% là mưa lớn
        """
        if self.use_hardware:
            try:
                # Đọc giá trị từ cảm biến mưa
                raw_value = self.rain_chan.value
                
                # Chuyển đổi sang phần trăm mưa (0-100%)
                # Giá trị này cần hiệu chỉnh theo cảm biến thực tế
                min_value = 1000    # Giá trị khi không mưa
                max_value = 20000   # Giá trị khi mưa lớn
                
                rain_percent = (raw_value - min_value) / (max_value - min_value) * 100
                rain_percent = max(0, min(100, rain_percent))
                
                logger.debug(f"Đọc cảm biến mưa: raw={raw_value}, rain={rain_percent:.2f}%")
                return rain_percent
            except Exception as e:
                logger.error(f"Lỗi khi đọc cảm biến mưa: {e}")
                if hasattr(self, 'rain_value'):
                    return self.rain_value
                return 0.0  # Trả về 0% (không mưa) nếu có lỗi
        else:
            # Mô phỏng giá trị mưa thay đổi ngẫu nhiên
            self.rain_value += random.uniform(-10, 10)
            self.rain_value = max(0, min(100, self.rain_value))
            return self.rain_value
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        logger.info("Dọn dẹp tài nguyên cảm biến")