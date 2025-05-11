import logging
import base64
import os
import cv2
import numpy as np
import time
from config import Config

# Thiết lập logging
logger = logging.getLogger(__name__)

# Kiểm tra xem thư viện picamera2 có khả dụng không
try:
    from picamera2 import Picamera2
    CAMERA_AVAILABLE = True
    logger.info("Đã nhập thành công thư viện picamera2")
except ImportError:
    logger.warning("Không thể nhập thư viện picamera2, sẽ sử dụng chế độ mô phỏng")

class Camera:
    """
    Lớp quản lý Raspberry Pi Camera
    Hỗ trợ chức năng chụp ảnh và xử lý video stream
    """
class Camera:
    def __init__(self, use_hardware=True):
        self.use_hardware = use_hardware and CAMERA_AVAILABLE
        self.last_processed_frame = None
        self.image_path = 'static/img/camera-placeholder.jpg'

        if self.use_hardware:
            try:
                # Khởi tạo Picamera2
                self.camera = Picamera2()
                self.camera.start()
                logger.info("Đã khởi tạo thành công camera")
            except Exception as e:
                logger.error(f"Lỗi khi khởi tạo camera: {e}")

                
                # Cấu hình camera
                self.config = self.camera.create_still_configuration(
                    main={"size": Config.CAMERA_RESOLUTION},
                    lores={"size": (320, 240)},
                    display="lores"
                )
                self.camera.configure(self.config)
                
                # Bắt đầu camera
                self.camera.start()
                
                # Chờ camera khởi động
                time.sleep(2)
                
                logger.info("Đã khởi tạo thành công camera")
            except Exception as e:
                logger.error(f"Lỗi khi khởi tạo camera: {e}")

        if not self.use_hardware:
            # Tạo thư mục để lưu ảnh placeholder nếu chưa tồn tại
            os.makedirs(os.path.dirname(self.image_path), exist_ok=True)
            
            # Tạo ảnh placeholder nếu chưa có
            if not os.path.exists(self.image_path):
                blank_image = np.zeros((480, 640, 3), dtype=np.uint8)
                
                # Vẽ text "Camera không khả dụng" vào ảnh
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(blank_image, 'Camera khong kha dung', (150, 240), 
                           font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Lưu ảnh
                cv2.imwrite(self.image_path, blank_image)
            
            logger.info("Sử dụng chế độ mô phỏng camera")
    
    def capture_frame(self):
        """Chụp một khung hình từ camera và trả về dạng numpy array"""
        if self.use_hardware:
            try:
                # Chụp frame từ camera
                frame = self.camera.capture_array()
                
                # Chuyển đổi sang BGR nếu cần thiết (picamera2 trả về hình RGB)
                if frame.shape[2] == 3:  # Nếu là hình màu
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                return frame
            except Exception as e:
                logger.error(f"Lỗi khi chụp ảnh từ camera: {e}")
        
        # Trong trường hợp lỗi hoặc mô phỏng, đọc ảnh placeholder
        try:
            return cv2.imread(self.image_path)
        except:
            # Nếu đọc file thất bại, trả về một ảnh trống
            return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def set_last_processed_frame(self, frame):
        """Lưu khung hình đã xử lý gần nhất"""
        self.last_processed_frame = frame
    
    def get_last_processed_frame(self):
        """Lấy khung hình đã xử lý gần nhất"""
        if self.last_processed_frame is not None:
            return self.last_processed_frame
        return self.capture_frame()
    
    def get_last_processed_frame_base64(self):
        """Trả về khung hình đã xử lý gần nhất dưới dạng chuỗi base64"""
        try:
            frame = self.get_last_processed_frame()
            _, buffer = cv2.imencode('.jpg', frame)
            img_str = base64.b64encode(buffer).decode('utf-8')
            return img_str
        except Exception as e:
            logger.error(f"Lỗi khi chuyển đổi frame sang base64: {e}")
            
            # Tạo một ảnh lỗi
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, 'Loi camera', (240, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            _, buffer = cv2.imencode('.jpg', blank)
            return base64.b64encode(buffer).decode('utf-8')
    
    def cleanup(self):
        """Dọn dẹp tài nguyên camera"""
        if self.use_hardware:
            try:
                self.camera.stop()
            except Exception as e:
                logger.error(f"Lỗi khi dọn dẹp camera: {e}")
        
        logger.info("Dọn dẹp tài nguyên camera")