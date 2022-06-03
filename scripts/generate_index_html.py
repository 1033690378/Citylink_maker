import sys

sys.path.insert(0, '../')
sys.path.insert(0, '../apps')

import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'Citylink_maker.settings'

import django

django.setup()

from goods.crons import generate_static_index

# 用脚本来生成静态的文件
if __name__ == '__main__':
    generate_static_index()

"""
导入包的顺序不能乱，不能放在在一起，不然会冲突报错。
"""
