import sys
import os
# 将api目录加入sys.path，确保模块导入正常
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from models import db, Coupon

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'))

# 配置
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_db_path = os.path.join(_project_root, 'coupon_data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{_db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

# 初始化扩展
db.init_app(app)
CORS(app, origins=['*'])  # 允许所有跨域请求

# 创建数据库表
with app.app_context():
    db.create_all()
    # 启动时更新过期状态
    Coupon.update_expired_status()

# 导入路由
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)