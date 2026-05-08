from flask import request, jsonify, render_template, send_from_directory
from app import app, db
from models import Coupon
from datetime import datetime, timedelta
import os, json, random, urllib.request, urllib.parse
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
            price=data.get('price'),
            market_price=data.get('market_price'),
            internal_price=data.get('internal_price'),
            expire=data['expire'],
            code=data['code'],
            activity=data.get('activity', ''),
            status='未使用',
            recipient=data.get('recipient', ''),
            remark=data.get('remark', ''),
            nights=data.get('nights', 1),
            currency=data.get('currency', ''),
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
        if 'market_price' in data:
            coupon.market_price = data['market_price']
        if 'internal_price' in data:
            coupon.internal_price = data['internal_price']
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
        if 'currency' in data:
            coupon.currency = data['currency']
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

# 市场价自动查询
@app.route('/api/coupons/query-market-price', methods=['POST'])
def query_market_price():
    """自动查询房券市场价：随机选3个日期查WR平台取均价"""
    try:
        data = request.json
        hotel_name = data.get('hotel', '').strip()
        nights = int(data.get('nights', 1))
        expire = data.get('expire', '')
        wr_hotel_id = data.get('hotel_id', '')  # 优先使用已确认的 HotelID
        # 提取英文名备选（如 "厦门航空费尔蒙酒店 (Fairmont Xiamen)" -> "Fairmont Xiamen"）
        import re
        en_match = re.search(r'\(([^)]+)\)', hotel_name)
        search_names = [hotel_name]
        if en_match:
            search_names.append(en_match.group(1).strip())
        # 可选的检索参数
        city_id = data.get('city_id', '')
        hotel_chain = data.get('hotel_chain', '')
        hotel_code = data.get('hotel_code', '')
        brand_ids = data.get('brand_ids', '')
        
        if (not hotel_name and not wr_hotel_id) or not expire:
            return jsonify({'success': False, 'data': None, 'message': '缺少酒店名或有效期'})
        
        # 如果有已确认的 HotelID，直接跳过搜索
        hotel_id = wr_hotel_id
        found_hotel = None
        
        # 可用日期段：今天到有效期
        from datetime import datetime, timedelta
        import random
        
        today = datetime.now().date()
        try:
            expire_date = datetime.strptime(expire, '%Y-%m-%d').date()
        except:
            return jsonify({'success': False, 'data': None, 'message': '有效期格式错误'})
        
        # 可用日期范围
        start = max(today, today + timedelta(days=1))  # 至少明天
        end = expire_date - timedelta(days=nights)
        
        if start >= end:
            return jsonify({'success': False, 'data': None, 'message': f'日期范围太短: {start}~{end}'})
        
        # 生成3个随机日期
        days_range = (end - start).days
        if days_range < 3:
            sample_dates = [start + timedelta(days=i) for i in range(min(days_range + 1, 3))]
        else:
            indices = sorted(random.sample(range(days_range + 1), min(3, days_range + 1)))
            sample_dates = [start + timedelta(days=i) for i in indices]
        
        # 登录WR平台
        import subprocess, os
        skill_dir = os.path.expanduser('~/.workbuddy/skills/hotel-price-query')
        token_file = os.path.join(skill_dir, '.token')
        
        if not os.path.exists(token_file):
            return jsonify({'success': False, 'data': None, 'message': 'WR平台未登录，请告知手机号和密码'})
        
        with open(token_file) as f:
            token = f.read().strip()
        
        if not hotel_id:
            # 提取英文名备选
            import re
            en_match = re.search(r'\(([^)]+)\)', hotel_name)
            search_names = [hotel_name]
            if en_match:
                search_names.append(en_match.group(1).strip())
            
            # 搜索酒店定义
            def search_hotel(name, page=1, extra_params=''):
                url = f'https://server.wildroadgroup.com/api/v1/hotels/?page={page}&size=20&name={urllib.parse.quote(name)}{extra_params}'
                req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json;charset=UTF-8'})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return json.loads(resp.read())
            
            extra = ''
            if city_id:
                extra += f'&cityId={urllib.parse.quote(city_id)}'
            if hotel_chain:
                extra += f'&hotelChain={urllib.parse.quote(hotel_chain)}'
            if hotel_code:
                extra += f'&hotelCode={urllib.parse.quote(hotel_code)}'
            if brand_ids:
                extra += f'&brandIds={urllib.parse.quote(brand_ids)}'
            
            found_hotel = None
            # 尝试多个名称变体，最多3页
            for name in search_names:
                for page_num in range(1, 4):
                    try:
                        search_data = search_hotel(name, page_num, extra)
                        hotels = search_data.get('hotels', [])
                        if hotels:
                            found_hotel = hotels[0]
                            hotel_id = found_hotel.get('_id', '')
                            break
                        total = search_data.get('total', 0)
                        if page_num * 20 >= total:
                            break
                    except Exception:
                        break
                if hotel_id:
                    break
            
            if not hotel_id:
                return jsonify({'success': False, 'data': None, 'message': f'WR平台未找到酒店: {hotel_name}（已尝试: {", ".join(search_names)}）'})
        
        hotel_chain_found = found_hotel.get('HotelChain', '') if found_hotel else ''
        hotel_code_found = found_hotel.get('HotelCode', '') if found_hotel else ''
        if wr_hotel_id:
            print(f"[query-market-price] Using preset ID: {hotel_id}", flush=True)
        else:
            print(f"[query-market-price] Found: {hotel_id} chain={hotel_chain_found} code={hotel_code_found}", flush=True)
        
        # 查询3个日期的价格
        prices = []
        for d in sample_dates[:3]:
            check_in = d.strftime('%Y-%m-%d')
            check_out = (d + timedelta(days=nights)).strftime('%Y-%m-%d')
            rate_url = f'https://server.wildroadgroup.com/api/v1/hotels/{hotel_id}/rates?gds=WRT&checkInDate={check_in}&checkOutDate={check_out}&numberOfAdults=2&numberOfRooms=1'
            req2 = urllib.request.Request(rate_url, headers={'Authorization': f'Bearer {token}'})
            try:
                with urllib.request.urlopen(req2, timeout=15) as resp:
                    rate_data = json.loads(resp.read())
                products = rate_data.get('productsWithRates', []) or rate_data.get('data', {}).get('results', [])
                all_rates = []
                for p in products:
                    for r in p.get('rates', []):
                        # 优先取 Total（含税总价）> Base（不含税总价）> HotelRateByDate[0].Base（每晚价）
                        total_str = r.get('Total') or r.get('Base') or r.get('total') or r.get('base')
                        if not total_str:
                            hrd = r.get('HotelRateByDate', [])
                            if hrd:
                                total_str = hrd[0].get('Base', '')
                        if total_str:
                            try:
                                cleaned = re.sub(r'[A-Z]{3}', '', str(total_str)).replace(',','')
                                all_rates.append(float(cleaned))
                            except:
                                pass
                if all_rates:
                    prices.append(min(all_rates))
            except Exception as e:
                print(f"[query-market-price] Rate query failed for {check_in}: {str(e)}", flush=True)
                continue
        
        if len(prices) < 1:
            return jsonify({'success': False, 'data': None, 'message': '所有日期查询失败'})
        
        avg_price = sum(prices) / len(prices)
        
        # 从已获取的 rate 数据中检测货币
        currency = 'HKD'
        for d in sample_dates[:3]:
            check_in = d.strftime('%Y-%m-%d')
            check_out = (d + timedelta(days=nights)).strftime('%Y-%m-%d')
            rate_url = f'https://server.wildroadgroup.com/api/v1/hotels/{hotel_id}/rates?gds=WRT&checkInDate={check_in}&checkOutDate={check_out}&numberOfAdults=2&numberOfRooms=1'
            req3 = urllib.request.Request(rate_url, headers={'Authorization': f'Bearer {token}'})
            try:
                with urllib.request.urlopen(req3, timeout=15) as resp:
                    rd = json.loads(resp.read())
                for p in rd.get('productsWithRates', []):
                    for r in p.get('rates', []):
                        # 从 Total 或 Base 中提取货币前缀
                        price_str = r.get('Total') or r.get('Base') or r.get('base') or ''
                        if not price_str:
                            hrd = r.get('HotelRateByDate', [])
                            if hrd:
                                price_str = hrd[0].get('Base', '')
                        m = re.match(r'([A-Z]{3})', str(price_str))
                        if m:
                            currency = m.group(1)
                            break
                    if currency != 'HKD':
                        break
            except:
                continue
            if currency != 'HKD':
                break
        
        # 内部价：中国酒店(CNY) ×40%，其他 ×20%，取整到最近的xx88或xx99
        ratio = 0.4 if currency == 'CNY' else 0.2
        target = avg_price * ratio
        # 找最近的以88/99结尾的价格
        base = int(target / 100) * 100
        candidates = [base + 88, base + 99, base - 12, base - 1]  # 88, 99, -12(上一位88), -1(上一位99)
        candidates = [c for c in candidates if c > 0]
        internal_price = min(candidates, key=lambda x: abs(x - target))
        
        return jsonify({
            'success': True,
            'data': {
                'market_price': round(avg_price, 2),
                'internal_price': internal_price,
                'currency': currency,
                'sample_dates': [d.strftime('%Y-%m-%d') for d in sample_dates[:len(prices)]],
                'prices': prices,
                'hotel_id': hotel_id,
                'nights': nights
            },
            'message': f'市场价({currency}): {avg_price:.0f}, 内部价: {internal_price}'
        })
    except Exception as e:
        return jsonify({'success': False, 'data': None, 'message': f'查询失败: {str(e)}'})

# 汇率查询
@app.route('/api/exchange-rates', methods=['GET'])
def get_exchange_rates():
    """获取WR平台汇率数据"""
    try:
        skill_dir = os.path.expanduser('~/.workbuddy/skills/hotel-price-query')
        token_file = os.path.join(skill_dir, '.token')
        if not os.path.exists(token_file):
            return jsonify({'success': False, 'data': [], 'message': '未登录WR平台'})
        with open(token_file) as f:
            token = f.read().strip()
        
        req = urllib.request.Request('https://api.wildroadgroup.com/admin/exchangerateController/all',
                                     headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            rates = json.loads(resp.read())
        return jsonify({'success': True, 'data': rates, 'message': ''})
    except Exception as e:
        return jsonify({'success': False, 'data': [], 'message': str(e)})