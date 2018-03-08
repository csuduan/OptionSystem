#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by duanqing 2018/2/6

from flask import Flask, jsonify, request
import subprocess
import time
import pymssql
import os
import asyncio
import threading

from Option import  Option



#webpack = Webpack()


# Flask初始化
app = Flask(__name__)

# def webpack():
#     print('webpack...')
#     os.system('webpack  --config ../webpack.config.js  --watch')
#
#
# t=threading.Thread(target=webpack)
# t.start()


option=Option()



#询价
#请求格式：
#[{"stock":"000001.SZ","period":6,"strikePercent":1.05}]
# curl -i -H "Content-Type: application/json" -X POST -d '[{"stock":"000001.SZ","period":6,"strikePercent":1.05,"amount":20}]' http://192.168.1.71:5000/option
#
@app.route('/enquiry', methods=['POST'])
def enquiry():
    result = {
        "errCode": 0,
        "errMsg": "success",
    }
    try:
        req = request.json

        stock = req['stock']
        period = req['period']
        strikePercent = float(req['strikePct'])
        amount = float(req['amount'])

        data=option.getEnquiry(stock,period,strikePercent,amount)
        if data[0]==0:
            enquiry=data[1]
            tms = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result['data'] = ({"No":enquiry[0], "stock": stock,"period":period,"strikePct":strikePercent, "cost": enquiry[7],"maxAmount":enquiry[6],"time": tms})
        else:
            result['errCode']=data[0]
            result['errMsg']=data[1]

    except Exception as ex:
         print(ex)
         result['errCode'] = -1
         result['errMsg'] = 'Enquiry Exception'

    # 返回询价结果
    return jsonify(result)

@app.route('/trade', methods=['POST'])
def trade():
    result = {
        "errCode": 0,
        "errMsg": "success",
    }
    try:
        req = request.json

        enquiryNo = req['enquiryNo']
        custom = req['custom']
        amount = float(req['amount'])

        data = option.trade(custom,enquiryNo,amount)
        if data[0] == 0:
            tms = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result['data'] = (
            {"tradeNo": data[1],"tms":tms})
        else:
            result['errCode'] = data[0]
            result['errMsg'] = data[1]

    except Exception as ex:
        print(ex)
        result['errCode'] = -1
        result['errMsg'] = 'Trade Exception'

    # 返回交易结果
    return jsonify(result)


@app.route('/tradeQry', methods=['POST'])
def tradeQry():
    result = {
        "errCode": 0,
        "errMsg": "success",
    }
    try:
        req = request.json

        no = req['tradeNo']
        custom = req['custom']


        data = option.tradeQry(custom, no)
        if data[0] == 0:
            enquiry = data[1]
            tms = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            trade=data[1]
            result['data'] = (
                {"status": trade[10],"tradeTms":trade[13],"tradePrice":trade[11],"tradeAmount":trade[12]})
        else:
            result['errCode'] = data[0]
            result['errMsg'] = data[1]

    except Exception as ex:
        print(ex)
        result['errCode'] = -1
        result['errMsg'] = 'TradeQry Exception'

    # 返回交易结果
    return jsonify(result)






if __name__ == "__main__":
    # 生产模式关闭debug
    app.run(host='0.0.0.0', debug=True)
