from crawler import bond_crawler, index_crawler
from template import bond_render, index_render
from send_email import send
import time
import os


def bond_main():
    # 持仓以及数据字段
    holding_code = ['127004']
    holding = []
    first_section_show = ['bond_id', 'bond_nm', 'price', 'fir_line', 'sec_line', 'convert_price',
                          'force_redeem_price', 'put_convert_price']
    second_section_show = ['bond_id', 'bond_nm', 'premium_rt', 'pb', 'convert_amt_ratio', 'convert_day']
    fir_sec_dt = []
    sec_sec_dt = []

    # 计算大盘数据的变量 head、total
    count = 0
    total = 0

    for d in bond_crawler():
        count += 1  # 计算总转债数量
        total += d['increase_rt']  # 加总涨跌幅，便于算平均值

        # 判断持仓
        for h in holding_code:
            if d['bond_id'] == h:
                holding.append((d['bond_nm'], d['price'], d['fir_line'], d['sec_line']))

        # 安全线部分
        if float(d['price']) < float(d['fir_line']):
            fir_sg_dt = [d[name] for name in first_section_show]
            fir_sec_dt.append(fir_sg_dt)

        # 溢价部分
        if d['premium_rt'] < 0 or d['premium_rt'] > 50 and d['pb'] > 1.8 and d['convert_amt_ratio'] > 10:
            sec_sg_dt = [d[name] for name in second_section_show]
            sec_sec_dt.append(sec_sg_dt)

    head = str(len(fir_sec_dt)) + '/' + str(count)
    total = total / count
    fir_sec_dt = sorted(fir_sec_dt, key=lambda x: x[2])
    sec_sec_dt = sorted(sec_sec_dt, key=lambda x: x[2])
    info = [head, total, holding, fir_sec_dt, sec_sec_dt]

    # 测试
    # with open(os.path.dirname(__file__) + '/templates/test.html', 'w+', encoding='utf-8') as f:
    #     f.write(charts_render(info))

    return bond_render(info)


def index_main():
    count = 0
    index_list = index_crawler()
    for i in index_list:
        count += i[5]
    info = [count, index_list]
    return index_render(info)


def main():
    while True:
        time.sleep(55)
        if time.localtime().tm_hour ==9 and time.localtime().tm_min == 0 and time.localtime().tm_wday != 6 and time.localtime().tm_wday != 0:
            month = str(time.localtime().tm_mon) + '月'
            day = str(time.localtime().tm_mday) + '日'
            send(bond_main(), month + day + '转债详情')
            send(index_main(), month + day + '指数详情')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        main()
