from django.core.serializers import get_serializer
from goods.models import Goods
from django.template import loader


# 生成静态的主页文件，这里只做了商品的数据处理
def generate_static_index():
    # 查询新品到货和热销商品
    new_goods = Goods.objects.filter(is_new=True).all()
    hot_goods = Goods.objects.filter(is_hot=True).all()

    context = {'new_goods': new_goods, 'hot_goods': hot_goods}
    template = loader.get_template('index.html')
    html_text = template.render(context=context)

    # 生成一个html文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(html_text)
