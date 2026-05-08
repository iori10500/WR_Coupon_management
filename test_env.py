import sys
print(f'Python版本: {sys.version}')

try:
    import flask
    print('✅ Flask已安装')
except ImportError:
    print('❌ Flask未安装')

try:
    import sqlalchemy
    print('✅ SQLAlchemy已安装')
except ImportError:
    print('❌ SQLAlchemy未安装')

try:
    import pandas
    print('✅ pandas已安装')
except ImportError:
    print('❌ pandas未安装')

print('\n当前目录内容:')
import os
print(os.listdir('.'))