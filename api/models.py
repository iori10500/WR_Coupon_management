from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Coupon(db.Model):
    __tablename__ = 'coupon'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(100))
    price = db.Column(db.Float)
    expire = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD格式
    code = db.Column(db.String(50), unique=True, nullable=False)
    activity = db.Column(db.String(200))
    status = db.Column(db.String(20), default='未使用')
    recipient = db.Column(db.String(100))  # 获得者/上传用户
    remark = db.Column(db.String(500))
    nights = db.Column(db.Integer, default=1)  # 入住晚数
    image_url = db.Column(db.String(500))  # 房券图片地址
    # WR系统酒店映射字段
    wr_hotel_id = db.Column(db.String(50))  # WR酒店ID
    wr_hotel_chain = db.Column(db.String(10))  # WR酒店Chain (如 RE, SV)
    wr_hotel_code = db.Column(db.String(10))  # WR酒店Code (如 36863, 85274)

    def to_dict(self):
        return {
            'id': self.id,
            'hotel': self.hotel,
            'room': self.room,
            'price': float(self.price) if self.price else None,
            'expire': self.expire,
            'code': self.code,
            'activity': self.activity,
            'status': self.status,
            'recipient': self.recipient,
            'remark': self.remark,
            'nights': self.nights,
            'image_url': self.image_url,
            'wr_hotel_id': self.wr_hotel_id,
            'wr_hotel_chain': self.wr_hotel_chain,
            'wr_hotel_code': self.wr_hotel_code
        }
    
    @staticmethod
    def update_expired_status():
        """自动更新过期房券状态"""
        today = datetime.now().strftime("%Y-%m-%d")
        expired_coupons = Coupon.query.filter(Coupon.status == '未使用', Coupon.expire < today).all()
        for coupon in expired_coupons:
            coupon.status = '已过期'
        db.session.commit()