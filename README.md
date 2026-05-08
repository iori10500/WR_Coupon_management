# 云端房券管理系统

基于 Flask + SQLite 的房券管理系统，支持房券的录入、查询、筛选、核销和统计。

## 功能特性

- 房券管理：新增、编辑、删除、核销
- 搜索筛选：按酒店、券码、活动、获得者、状态筛选
- 图片上传：支持房券图片上传和展示
- 统计分析：实时统计房券状态（未使用/已使用/已过期）
- 响应式设计：支持桌面端和移动端访问

## 技术栈

- **后端**：Flask + SQLAlchemy + SQLite
- **前端**：原生 HTML/JS + Tailwind CSS
- **图标**：Font Awesome 4.7

## 项目结构

```
cloud_coupon_manager/
├── api/
│   ├── app.py           # Flask 应用入口
│   ├── routes.py        # API 路由
│   └── models.py       # 数据库模型
├── templates/
│   └── index.html      # 前端页面
├── static/
│   └── uploads/       # 房券图片上传目录
├── venv/             # Python 虚拟环境
└── coupon_data.db    # SQLite 数据库文件
```

## 安装和运行

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install flask flask-sqlalchemy flask-cors
```

### 3. 初始化数据库

数据库会在首次运行时自动创建。

### 4. 启动服务

```bash
cd api
python app.py
```

服务将运行在 http://127.0.0.1:5001

## API 文档

### 房券接口

- `GET /api/coupons` - 获取所有房券
- `GET /api/coupons/<id>` - 获取单张房券
- `POST /api/coupons` - 新增房券
- `PUT /api/coupons/<id>` - 更新房券
- `DELETE /api/coupons/<id>` - 删除房券
- `PUT /api/coupons/<id>/use` - 核销房券

### 其他接口

- `GET /api/statistics` - 获取统计数据
- `POST /api/coupons/filter` - 筛选房券
- `POST /api/upload` - 上传图片

## 数据库字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| hotel | String(100) | 酒店名称 |
| room | String(100) | 房型 |
| price | Float | 价值 |
| expire | String(20) | 有效期 (YYYY-MM-DD) |
| code | String(50) | 券码（唯一） |
| activity | String(200) | 活动名称 |
| status | String(20) | 状态（未使用/已使用/已过期） |
| recipient | String(100) | 获得者 |
| nights | Integer | 入住晚数 |
| remark | String(500) | 备注 |
| image_url | String(500) | 图片地址 |
| wr_hotel_id | String(50) | WR 酒店ID（预留） |
| wr_hotel_chain | String(10) | WR 酒店Chain（预留） |
| wr_hotel_code | String(10) | WR 酒店Code（预留） |

## 开发者

- 房券管理系统由 WR 平台运营团队维护