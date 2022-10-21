from pyecharts import options as opts
from pyecharts.charts import Map, Timeline
# from pyecharts import Map, Geo
import numpy as np

province_dis1 = {'宁夏': 0, '河南': 0, '北京': 0, '河北': 0, '辽宁': 612, '江西': 0, '上海': 0, '安徽': 500, '江苏': 100,
                '湖南': 500, '浙江': 553, '海南': 0, '广东': 0, '湖北': 500, '黑龙江': 200, '澳门': 0, '陕西': 0, '四川': 0,
                '内蒙古': 0, '重庆': 0, '广西': 0, '云南': 0, '贵州': 0, '吉林': 300, '山西': 0, '山东': 0, '福建': 0,
                '青海': 0, '天津': 80, '新疆': 0, '西藏': 0, '甘肃': 0, '台湾': 0}
province_dis = {'宁夏': 0, '河南': 0, '北京': 0, '河北': 0, '辽宁': 0, '江西': 0, '上海': 0, '安徽': 0, '江苏': 0,
                 '湖南': 0, '浙江': 0, '海南': 0, '广东': 0, '湖北': 0, '黑龙江': 0, '澳门': 0, '陕西': 0, '四川': 0,
                 '内蒙古': 0, '重庆': 0, '广西': 0, '云南': 0, '贵州': 0, '吉林': 0, '山西': 0, '山东': 0, '福建': 0, '青海': 0,
                 '天津': 0, '新疆': 0, '西藏': 0, '甘肃': 0, '台湾': 0}
provice = list(province_dis.keys())
values = list(province_dis.values())

values1 = list(province_dis1.values())

sum_vlaues = []
sum_vlaues.append(values), sum_vlaues.append(values1)

tl = Timeline()
for i in range(2015, 2017):
    map_min = int(np.min(sum_vlaues[i - 2015]))
    map_max = int(np.max(sum_vlaues[i - 2015]))
    china = (
        Map()
            .add("", [list(z) for z in zip(provice, sum_vlaues[i - 2015])], "china")
            .set_global_opts(title_opts=opts.TitleOpts(title=""),
                             visualmap_opts=opts.VisualMapOpts(type_='color', min_=map_min, max_=map_max))
    )
    tl.add(china, "动态分布变化")
tl.add_schema(is_auto_play=True, play_interval=1000)  # 自动播放，跳动的间隔为1000ms
tl.render(path=u'D:test01.html')