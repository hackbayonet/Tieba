# -*- coding: utf-8 -*-
# Created by bayonet on 2016/5/27 9:51.

import requests
import re
from lxml import etree
import time
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
session = requests.session()

URL_BAIDU_INDEX = u'http://www.baidu.com/'
URL_BAIDU_TOKEN = 'https://passport.baidu.com/v2/api/?getapi&tpl=pp&apiver=v3&class=login'
URL_BAIDU_LOGIN = 'https://passport.baidu.com/v2/api/?login'
URL_TIEBA_ROOT = 'http://tieba.baidu.com'


def get_tieba_data(html_code):
    tieba = []
    html = etree.HTML(html_code)
    for tr in html.xpath('//table[@class="tb"]/tr'):
        url = tr.xpath('td/a/@href')[0]
        name = tr.xpath('td/a/text()')[0]
        levle = str(tr.xpath('td[2]/text()')[0]).replace('等级', '')
        exp = str(tr.xpath('td[3]/text()')[0]).replace('经验值', '')
        tieba.append({'name': name, 'levle': levle, 'exp': exp, 'url': url})
    return tieba


def get_qiandao(html_code):
    # 签到处理
    html = etree.HTML(html_code)
    sx = html.xpath('//table/tr/td[2]/a/text()')
    if sx:
        url = '{0}{1}'.format(URL_TIEBA_ROOT, html.xpath('//table/tr/td[2]/a/@href')[0])
        print '签到', 
        html = etree.HTML(session.get(url).content)
        data = html.xpath('//span[@class="light"]/text()')
        print data[0], data[1], 
    else:
        print '已签到',


if __name__ == '__main__':
    # 设置用户名、密码
    username = '你的账号'
    password = '你的密码'
    while True:
        reqReturn = session.get(URL_BAIDU_INDEX)
        tokenReturn = session.get(URL_BAIDU_TOKEN)
        matchVal = re.search('"token" : "(?P<tokenVal>.*?)"', tokenReturn.text)
        tokenVal = matchVal.group('tokenVal')
        # 构造登录请求参数，该请求数据是通过抓包获得，对应https://passport.baidu.com/v2/api/?login请求
        postData = {
            'username': username,
            'password': password,
            'u': 'https://www.baidu.com/',
            'tpl': 'pp',
            'token': tokenVal,
            'staticpage': 'https://www.baidu.com/cache/user/html/v3Jump.html',
            'isPhone': 'false',
            'charset': 'UTF-8',
            'callback': 'parent.bd__pcbs__hb4wvo'
        }
        loginRequest = session.post(URL_BAIDU_LOGIN, postData)
        error = re.findall('&error=(.*?)\'', loginRequest.content)[0]
        if ('0' != error):
            print "登陆失败！"
            # 登陆失败 等待3秒在执行
            time.sleep(3)
            continue
        html_code = session.get('http://tieba.baidu.com/mo/m?tn=bdFBW&tab=favorite').content
        tieba = get_tieba_data(html_code)
        print('---------百度贴吧自动签到程序---------')
        print('---------作者:　　 bayonet----------')
        for value in tieba:
            print "{0} >>  ".format(time.strftime('%Y-%m-%d %H:%M:%S')) ,
            url = '{0}{1}'.format(URL_TIEBA_ROOT, value.get('url'))
            html_code = session.get(url).content
            print value.get('name') + ': ',
            get_qiandao(html_code)
            print('等级:   {1}  经验: {2}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), value.get('levle'), value.get('exp')))
        break
