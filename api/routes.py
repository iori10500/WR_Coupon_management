from flask import request, jsonify, render_template, send_from_directory
from app import app, db
from models import Coupon
from datetime import datetime
import os
import uuid

# 图片上传目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 图片上传API
@app.route('/api/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'data': None, 'message': '未找到图片文件'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'data': None, 'message': '未选择图片文件'})
        
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            image_url = f"/static/uploads/{filename}"
            return jsonify({
                'success': True,
                'data': {'image_url': image_url},
                'message': '图片上传成功'
            })
        
        return jsonify({'success': False, 'data': None, 'message': '不支持的图片格式'})
    except Exception as e:
        return jsonify({'success': False, 'data': None, 'message': f'图片上传失败: {str(e)}'})

# 获取所有房券
@app.route('/api/coupons', methods=['GET'])
def get_coupons():
    try:
        # 先更新过期状态
        Coupon.update_expired_status()
        
        coupons = Coupon.query.order_by(Coupon.id.desc()).all()
        return jsonify({
            'success': True,
            'data': [coupon.to_dict() for coupon in coupons],
            'message': '获取房券列表成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'获取房券列表失败: {str(e)}'
        })

# 获取单张房券
@app.route('/api/coupons/<int:coupon_id>', methods=['GET'])
def get_coupon(coupon_id):
    try:
        coupon = Coupon.query.get(coupon_id)
        if coupon:
            return jsonify({
                'success': True,
                'data': coupon.to_dict(),
                'message': '获取房券成功'
            })
        else:
            return jsonify({
                'success': False,
                'data': None,
                'message': '房券不存在'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'获取房券失败: {str(e)}'
        })

# 新增房券
@app.route('/api/coupons', methods=['POST'])
def add_coupon():
    try:
        data = request.json
        
        # 验证必填字段
        required_fields = ['hotel', 'expire', 'code']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'data': None,
                    'message': f'{field}不能为空'
                })
        
        # 检查券码是否已存在
        existing_coupon = Coupon.query.filter_by(code=data['code']).first()
        if existing_coupon:
            return jsonify({
                'success': False,
                'data': None,
                'message': '券码已存在'
            })
        
        # 创建新房券
        new_coupon = Coupon(
            hotel=data['hotel'],
            room=data.get('room', ''),
            price=data.get('price', 0),
            expire=data['expire'],
            code=data['code'],
            activity=data.get('activity', ''),
            status='未使用',
            recipient=data.get('recipient', ''),
            remark=data.get('remark', ''),
            nights=data.get('nights', 1),
            image_url=data.get('image_url', ''),
            wr_hotel_id=data.get('wr_hotel_id'),
            wr_hotel_chain=data.get('wr_hotel_chain'),
            wr_hotel_code=data.get('wr_hotel_code')
        )
        
        db.session.add(new_coupon)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': new_coupon.to_dict(),
            'message': '房券添加成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'data': None,
            'message': f'添加房券失败: {str(e)}'
        })

# 更新房券
@app.route('/api/coupons/<int:coupon_id>', methods=['PUT'])
def update_coupon(coupon_id):
    try:
        coupon = Coupon.query.get(coupon_id)
        if not coupon:
            return jsonify({
                'success': False,
                'data': None,
                'message': '房券不存在'
            })
        
        data = request.json
        
        # 更新字段
        if 'hotel' in data:
            coupon.hotel = data['hotel']
        if 'room' in data:
            coupon.room = data['room']
        if 'price' in data:
            coupon.price = data['price']
        if 'expire' in data:
            coupon.expire = data['expire']
        if 'code' in data and data['code'] != coupon.code:
            # 检查新券码是否已存在
            existing_coupon = Coupon.query.filter_by(code=data['code']).first()
            if existing_coupon:
                return jsonify({
                    'success': False,
                    'data': None,
                    'message': '新券码已存在'
                })
            coupon.code = data['code']
        if 'activity' in data:
            coupon.activity = data['activity']
        if 'recipient' in data:
            coupon.recipient = data['recipient']
        if 'remark' in data:
            coupon.remark = data['remark']
        if 'nights' in data:
            coupon.nights = data['nights']
        if 'image_url' in data:
            coupon.image_url = data['image_url']
        if 'wr_hotel_id' in data:
            coupon.wr_hotel_id = data['wr_hotel_id']
        if 'wr_hotel_chain' in data:
            coupon.wr_hotel_chain = data['wr_hotel_chain']
        if 'wr_hotel_code' in data:
            coupon.wr_hotel_code = data['wr_hotel_code']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': coupon.to_dict(),
            'message': '房券更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'data': None,
            'message': f'更新房券失败: {str(e)}'
        })

# 删除房券
@app.route('/api/coupons/<int:coupon_id>', methods=['DELETE'])
def delete_coupon(coupon_id):
    try:
        coupon = Coupon.query.get(coupon_id)
        if not coupon:
            return jsonify({
                'success': False,
                'data': None,
                'message': '房券不存在'
            })
        
        db.session.delete(coupon)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': None,
            'message': '房券删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'data': None,
            'message': f'删除房券失败: {str(e)}'
        })

# 核销房券
@app.route('/api/coupons/<int:coupon_id>/use', methods=['PUT'])
def use_coupon(coupon_id):
    try:
        coupon = Coupon.query.get(coupon_id)
        if not coupon:
            return jsonify({
                'success': False,
                'data': None,
                'message': '房券不存在'
            })
        
        if coupon.status == '已使用':
            return jsonify({
                'success': False,
                'data': None,
                'message': '该房券已核销'
            })
        
        if coupon.status == '已过期':
            return jsonify({
                'success': False,
                'data': None,
                'message': '过期房券无法核销'
            })
        
        coupon.status = '已使用'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': coupon.to_dict(),
            'message': '房券核销成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'data': None,
            'message': f'核销房券失败: {str(e)}'
        })

# 获取统计数据
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        # 先更新过期状态
        Coupon.update_expired_status()
        
        total = Coupon.query.count()
        unused = Coupon.query.filter_by(status='未使用').count()
        used = Coupon.query.filter_by(status='已使用').count()
        expired = Coupon.query.filter_by(status='已过期').count()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'unused': unused,
                'used': used,
                'expired': expired
            },
            'message': '获取统计数据成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'获取统计数据失败: {str(e)}'
        })

# 筛选房券
@app.route('/api/coupons/filter', methods=['POST'])
def filter_coupons():
    try:
        # 先更新过期状态
        Coupon.update_expired_status()
        
        data = request.json
        query = Coupon.query
        
        # 按状态筛选
        if 'status' in data and data['status']:
            query = query.filter_by(status=data['status'])
        
        # 按酒店筛选
        if 'hotel' in data and data['hotel']:
            query = query.filter(Coupon.hotel.like(f"%{data['hotel']}%"))
        
        # 按活动筛选
        if 'activity' in data and data['activity']:
            query = query.filter(Coupon.activity.like(f"%{data['activity']}%"))
        
        # 按券码筛选
        if 'code' in data and data['code']:
            query = query.filter(Coupon.code.like(f"%{data['code']}%"))

        # 按获得者筛选
        if 'recipient' in data and data['recipient']:
            query = query.filter(Coupon.recipient.like(f"%{data['recipient']}%"))

        # 按有效期范围筛选
        if 'expire_start' in data and data['expire_start']:
            query = query.filter(Coupon.expire >= data['expire_start'])
        if 'expire_end' in data and data['expire_end']:
            query = query.filter(Coupon.expire <= data['expire_end'])
        
        coupons = query.order_by(Coupon.id.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [coupon.to_dict() for coupon in coupons],
            'message': '筛选房券成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'筛选房券失败: {str(e)}'
        })