import requests
import json
import re
import datetime
from lxml import etree


def bond_crawler():
    url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t=1546582559406'

    # 转债id、转债名称、价格、转股价格、转股价值、涨跌幅、溢价率、
    # 剩余年限、到期税后收益、利息、赎回价、发行日、到期日、下调、
    # 强赎触发、回售触发、回售价、PB、转债占比、转股起始日
    useful_sections = {'bond_id', 'bond_nm', 'price', 'convert_price', 'convert_value', 'increase_rt', 'premium_rt',
                       'year_left', 'ytm_rt_tax', 'cpn_desc', 'redeem_price', 'issue_dt', 'maturity_dt', 'adjust_tc',
                       'force_redeem_price', 'put_convert_price', 'put_price', 'pb', 'convert_amt_ratio', 'convert_dt'}

    r = requests.get(url).content.decode()
    j = json.loads(r)

    bond_list = j['rows']
    bond_collection = []

    for bond in bond_list:
        result = {name: bond['cell'][name] for name in useful_sections}

        # 规范格式
        result['price'] = round(float(result['price']), 2)
        result['premium_rt'] = float(result['premium_rt'][:-1])
        result['increase_rt'] = float(result['increase_rt'][:-1])
        result['force_redeem_price'] = 0 if result['force_redeem_price'] == '-' else result['force_redeem_price']
        result['force_redeem_price'] = float(result['force_redeem_price'])
        result['put_convert_price'] = 0 if result['put_convert_price'] == '-' else result['put_convert_price']
        result['put_convert_price'] = float(result['put_convert_price'])
        result['pb'] = float(result['pb'])
        result['convert_amt_ratio'] = float(result['convert_amt_ratio'][:-1])
        result['convert_price'] = float(result['convert_price'])

        # 计算出总年数
        result['tt_year'] = float(result['maturity_dt'][:4]) - float(result['issue_dt'][:4])

        # 计算第一、二条安全线（到期价值）
        int_list = re.findall('\d{1}\.\d{1,2}|\d{1}', result['cpn_desc'])
        if len(int_list) == 1:
            int_list = int_list * int(result['tt_year'])
        int_list = [float(n) for n in int_list]
        result['fir_line'] = round((float(result['redeem_price']) + 0.8 * sum(int_list[:-1]))/((1+0.04)**float(result['year_left'])), 2)
        result['sec_line'] = round((float(result['redeem_price']) + 0.8 * sum(int_list[:-1]))/((1+0.03)**float(result['year_left'])), 2)

        # 计算转股日期与现在日期
        result['convert_day'] = (datetime.datetime.strptime(result['convert_dt'], '%Y-%m-%d') - datetime.datetime.now()).days

        bond_collection.append(result)
    return bond_collection


def index_crawler():
    today = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    url = 'http://www.csindex.com.cn/zh-CN/downloads/industry-price-earnings-ratio?date={}&type=zz1'.format(today)
    # url = 'http://www.csindex.com.cn/zh-CN/downloads/industry-price-earnings-ratio?date=2019-03-01&type=zz1'
    r = requests.get(url).content.decode()
    tree = etree.HTML(r)
    index_list = []

    name = tree.xpath('/html/body/div[3]/div/div/div[1]/div[2]/div[2]/div[1]/table/tbody/tr/td/div/table/tbody/tr/td/div/a/span//text()')
    pe = tree.xpath('/html/body/div[3]/div/div/div[1]/div[2]/div[2]/div[1]/table/tbody/tr/td/div/table/tbody/tr/td[3]/div//text()')
    month_average = tree.xpath('/html/body/div[3]/div/div/div[1]/div[2]/div[2]/div[1]/table/tbody/tr/td/div/table/tbody/tr/td[8]/div//text()')
    year_average = tree.xpath('/html/body/div[3]/div/div/div[1]/div[2]/div[2]/div[1]/table/tbody/tr/td/div/table/tbody/tr/td[9]/div//text()')
    pe = [float(p.strip()) for p in pe]
    month_average = [float(m.strip()) for m in month_average]
    year_average = [float(y.strip()) for y in year_average]

    for i in range(len(name)):
        month_invest_or_not = 0
        year_invest_or_not = 0
        month_compare = pe[i] - month_average[i]
        year_compare = pe[i] - year_average[i]

        if month_compare < 0:
            month_invest_or_not = 1

        if year_compare < 0:
            year_invest_or_not = 1

        index_list.append([name[i], pe[i], month_average[i], year_average[i], month_invest_or_not, year_invest_or_not])

    return index_list
