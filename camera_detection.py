import cv2
import numpy as np
import os

class AnimalDetector:
    def __init__(self):
        # Đường dẫn đến model (nếu có)
        self.model_path = 'models/animal_detection_model.tflite'
        self.detection_threshold = 0.5
        self.has_model = os.path.exists(self.model_path)
        
        # Nếu không có model, sử dụng phương pháp phát hiện đơn giản
        self.detection_counter = 0
    
    def detect_animals(self, frame):
        if self.has_model:
            return self._model_detection(frame)
        else:
            return self._simple_detection(frame)
    
    def _simple_detection(self, frame):
        # Phương pháp phát hiện đơn giản dựa trên màu sắc và chuyển động
        # Chỉ để minh họa, trong thực tế cần thuật toán phức tạp hơn
        
        # Chuyển sang không gian màu HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Lọc các vùng có màu nâu/đen (có thể là gia súc)
        lower_brown = np.array([10, 50, 50])
        upper_brown = np.array([30, 255, 255])
        mask = cv2.inRange(hsv, lower_brown, upper_brown)
        
        # Loại bỏ nhiễu
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Tìm đường viền
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Lọc các đường viền theo kích thước
        large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 1000]
        
        # Vẽ hộp giới hạn
        processed_image = frame.copy()
        for cnt in large_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(processed_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Phát hiện gia súc nếu có đường viền lớn
        has_animals = len(large_contours) > 0
        animals_count = len(large_contours)
        
        return has_animals, animals_count, processed_image
    
    def _model_detection(self, frame):
        # Phương pháp phát hiện sử dụng TensorFlow Lite
        # Triển khai trong thực tế khi có model
        # Đây chỉ là đoạn mã giả
        
        # Trong thực tế, bạn sẽ cần:
        # 1. Tải model TensorFlow Lite
        # 2. Tiền xử lý khung hình
        # 3. Chạy model để phát hiện
        # 4. Xử lý kết quả
        
        # Phương pháp tạm thời: sử dụng phương pháp đơn giản
        return self._simple_detection(frame)