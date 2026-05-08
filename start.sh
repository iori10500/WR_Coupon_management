#!/bin/bash

echo "🚀 启动云端房券管理系统..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.6+"
    exit 1
fi

# 检查依赖是否安装
echo "🔍 检查依赖包..."
pip install -r requirements.txt

# 启动Flask应用
echo "🌐 启动Flask服务器..."
echo "📱 移动端查询界面: http://0.0.0.0:5000"
echo "🔧 API接口地址: http://0.0.0.0:5000/api/"
echo "📖 使用说明: 查看 README.md 文件"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 api/app.py