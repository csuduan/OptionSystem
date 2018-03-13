#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by duanqing 2018/2/6

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import subprocess
import datetime
import time
import pymssql
import os
import asyncio
import threading
import json

from Option import  Option
from Admin  import  Admin



#webpack = Webpack()


# Flask初始化
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# def webpack():
#     print('webpack...')
#     os.system('webpack  --config ../webpack.config.js  --watch')
#
#
# t=threading.Thread(target=webpack)
# t.start()


option=Option()




admin=Admin()



@socketio.on('connect', namespace='/echo')
def test_connect():
    emit('my event', {'data': 'Connected', 'count': 0})
    print("recv socketio connect")
@socketio.on('my event', namespace='/echo')
def test_message(message):
    #emit('my event', {'data': message['data']})
    print("recv socketio message")



@app.route('/test', methods=['GET'])
def test():
    #emit('event-trade', {'data': 'test'},broadcast=True)
    socketio.emit('trade', {'custom': 'aaa'}, namespace='/echo')
    return "success"

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

            socketio.emit('trade', {'custom':custom ,'tradeNo':data[1]}, namespace='/echo')
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


@app.route('/trade/listpage', methods=['GET'])
def tradeListPage():
    print('/trade/listpage')

    page=int(request.values.get('page'))
    size=int(request.values.get('pageSize'))
    filters=json.loads(request.values.get('filters'))
    ret=admin.getPagedTrade(page,size,filters)
    jsonData=[]
    for trade in ret[1]:

        data={
            'tradeNo': trade[0],
            'tradingDay': trade[1],
            'custom': trade[2],
            'code': trade[3],
            'period': trade[4],
            'strikePct': trade[5],
            'amount': trade[6],
            'cost':trade[7],
            'insertTms': trade[9].strftime( '%Y-%m-%d %H:%M:%S' ) ,
            'status': trade[10],
            'tradePrice': trade[11],
            'tradeAmount': trade[12],
            'tradeTms':trade[13] if trade[13]==None else trade[13].strftime( '%Y-%m-%d %H:%M:%S' ),
            'tradeMsg':trade[14]

        }

        jsonData.append(data)

    result={'total':ret[0],'trades':jsonData}

    return jsonify(result)

@app.route('/enquiry/listpage', methods=['GET'])
def enquiryListPage():
    print('/enquiry/listpage')

    page = int(request.values.get('page'))
    size = int(request.values.get('pageSize'))
    ret = admin.getPagedEnquiry(page, size)
    jsonData = []
    for enquiry in ret[1]:
        data = {
            'enquiryNo': enquiry[0],
            'tradingDay': enquiry[1],
            'tmPeriod': enquiry[2],
            'code': enquiry[3],
            'period': enquiry[4],
            'strikePct': enquiry[5],
            'maxAmount': enquiry[6],
            'cost': enquiry[7],
            'tms': enquiry[8].strftime('%Y-%m-%d %H:%M:%S'),


        }
        jsonData.append(data)

    result = {'total': ret[0], 'enquirys': jsonData}

    return jsonify(result)


@app.route('/editTrade', methods=['POST'])
def editTrade():
    result = {
        "errCode": 0,
        "errMsg": "success",
    }

    data=request.json['params']
    try:
        admin.updateTrade(int(data['tradeNo']),data['status'],data['tradePrice'],data['tradeAmount'],f"{data['tradeDate']} {data['tradeTime']}",data['tradeMsg'])



    except Exception as ex:
        result = {
            "errCode": -1,
            "errMsg": "update Error",
        }
    return jsonify(result)
    pass







if __name__ == "__main__":
    # 生产模式关闭debug
    #app.run(host='0.0.0.0', debug=True)
    socketio.run(app, host='0.0.0.0', port=5000)
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    #
    # server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    # print('server start')
    # server.serve_forever()
