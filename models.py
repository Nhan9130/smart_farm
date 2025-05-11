from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SensorData(db.Model):
    """Model lưu trữ dữ liệu từ các cảm biến"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    rain_percent = db.Column(db.Float)  # Phần trăm (%) cảm biến mưa
    soil_moisture_percent = db.Column(db.Float)  # Phần trăm (%) độ ẩm đất
    ph_value = db.Column(db.Float)  # Giá trị pH (0-14)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'rain_percent': self.rain_percent,
            'soil_moisture_percent': self.soil_moisture_percent,
            'ph_value': self.ph_value
        }

class MotorState(db.Model):
    """Model lưu trữ trạng thái động cơ"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    cover_motor_active = db.Column(db.Boolean, default=False)  # Trạng thái động cơ mái che
    water_motor_active = db.Column(db.Boolean, default=False)  # Trạng thái động cơ tưới nước
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'cover_motor_active': self.cover_motor_active,
            'water_motor_active': self.water_motor_active
        }

class AnimalDetection(db.Model):
    """Model lưu trữ kết quả phát hiện gia súc"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    detected = db.Column(db.Boolean, default=False)  # Có phát hiện gia súc không
    count = db.Column(db.Integer, default=0)  # Số lượng gia súc phát hiện được
    confidence = db.Column(db.Float)  # Độ tin cậy của phát hiện
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'detected': self.detected,
            'count': self.count,
            'confidence': self.confidence
        }

class Config(db.Model):
    """Model lưu trữ cấu hình hệ thống"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(255))
    description = db.Column(db.String(255))
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description
        }

def setup_db(app):
    """Khởi tạo và thiết lập database"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Tạo cấu hình mặc định nếu chưa có
        default_configs = [
            ('rain_threshold', '40', 'Ngưỡng phần trăm (%) để xác định trời mưa'),
            ('soil_moisture_threshold', '30', 'Ngưỡng phần trăm (%) để xác định đất khô'),
            ('auto_mode', 'True', 'Chế độ tự động')
        ]
        
        for key, value, description in default_configs:
            if not Config.query.filter_by(key=key).first():
                config = Config(key=key, value=value, description=description)
                db.session.add(config)
        
        db.session.commit()