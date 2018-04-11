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
import Util

from Option import Option
from Admin import Admin
from Setting import Setting

import logging

logger = logging.getLogger(__name__)

Util.setup_logging()

# webpack = Webpack()


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

setting = Setting()
option = Option(setting)
admin = Admin()

logger.info('准备启动系统1。。。')


@socketio.on('connect', namespace='/echo')
def test_connect():
    emit('my event', {'data': 'Connected', 'count': 0})
    print("recv socketio connect")


@socketio.on('my event', namespace='/echo')
def test_message(message):
    # emit('my event', {'data': message['data']})
    print("recv socketio message")


@app.route('/test', methods=['GET'])
def test():
    # emit('event-trade', {'data': 'test'},broadcast=True)
    socketio.emit('trade', {'custom': 'aaa'}, namespace='/echo')
    return "success"


# 询价
# 请求格式：
# [{"stock":"000001.SZ","period":6,"strikePercent":1.05}]
# curl -i -H "Content-Type: application/json" -X POST -d '[{"stock":"000001.SZ","period":6,"strikePercent":1.05,"amount":20}]' http://192.168.1.71:5000/option
#
@app.route('/enquiry', methods=['POST'])
def enquiry():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
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
        custom = req.get('custom')

        # 匿名用户以ip代替客户名
        if custom == None:
            custom = request.remote_addr

        data = option.getEnquiry(custom, stock, period, strikePercent, amount)
        if data[0] == 0:
            enquiry = data[1]
            tms = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result['data'] = (
                {"No": enquiry[0], "stock": stock, "period": period, "strikePct": strikePercent, "cost": enquiry[6],
                 "time": tms})
        else:
            result['errCode'] = data[0]
            result['errMsg'] = data[1]

    except Exception as ex:
        logger.error(ex)
        result['errCode'] = -1
        result['errMsg'] = 'Enquiry Exception'

    # 返回询价结果
    logger.info(f'返回响应 {result}')
    return jsonify(result)


@app.route('/trade', methods=['POST'])
def trade():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
    result = {
        "errCode": 0,
        "errMsg": "success",
    }
    try:
        req = request.json

        enquiryNo = req['enquiryNo']
        custom = req['custom']
        amount = float(req['amount'])

        data = option.trade(custom, enquiryNo, amount)
        if data[0] == 0:
            tms = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result['data'] = (
                {"tradeNo": data[1], "tms": tms})

            socketio.emit('trade', {'custom': custom, 'tradeNo': data[1]}, namespace='/echo')
        else:
            result['errCode'] = data[0]
            result['errMsg'] = data[1]

    except Exception as ex:
        logger.error(ex)
        result['errCode'] = -1
        result['errMsg'] = 'Trade Exception'

    # 返回交易结果
    logger.info(f'返回响应 {result}')
    return jsonify(result)


@app.route('/tradeQry', methods=['POST'])
def tradeQry():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
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
            trade = data[1]
            result['data'] = (
                {"status": trade[12], "tradeTms": trade[15], "tradePrice": trade[13], "tradeAmount": trade[14]})
        else:
            result['errCode'] = data[0]
            result['errMsg'] = data[1]

    except Exception as ex:
        logger.error(ex)
        result['errCode'] = -1
        result['errMsg'] = 'TradeQry Exception'

    # 返回交易结果
    logger.info(f'返回响应 {result}')
    return jsonify(result)


@app.route('/trade/listpage', methods=['GET'])
def tradeListPage():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')

    page = int(request.values.get('page'))
    size = int(request.values.get('pageSize'))
    filters = json.loads(request.values.get('filters'))
    ret = admin.getPagedTrade(page, size, filters)
    jsonData = []
    for trade in ret[1]:
        data = {
            'tradeNo': trade[0],
            'tradingDay': trade[1],
            'custom': trade[2],
            'code': trade[3],
            'period': trade[4],
            'strikePct': trade[5],
            'amount': trade[6],
            'cost': trade[7],
            'volume': trade[9],
            'dueDate': trade[10],
            'insertTms': trade[11].strftime('%Y-%m-%d %H:%M:%S'),
            'status': trade[12],
            'tradePrice': trade[13],
            'tradeAmount': trade[14],
            'tradeTms': trade[15] if trade[15] == None else trade[15].strftime('%Y-%m-%d %H:%M:%S'),
            'tradeMsg': trade[16]

        }

        jsonData.append(data)

    result = {'total': ret[0], 'trades': jsonData}

    return jsonify(result)


@app.route('/enquiry/listpage', methods=['GET'])
def enquiryListPage():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')

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
            'cost': enquiry[6],
            'tms': enquiry[7].strftime('%Y-%m-%d %H:%M:%S'),

        }
        jsonData.append(data)

    result = {'total': ret[0], 'enquirys': jsonData}

    return jsonify(result)


@app.route('/custom/list', methods=['GET'])
def customList():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')

    page = int(request.values.get('page'))
    size = int(request.values.get('pageSize'))
    ret = admin.getPagedCustom(page, size)
    jsonData = []
    for custom in ret[1]:
        data = {
            'Id': custom[0],
            'Name': custom[1],
            'Type': custom[3],
        }

        jsonData.append(data)

    result = {'total': ret[0], 'customs': jsonData}

    return jsonify(result)


@app.route('/editTrade', methods=['POST'])
def editTrade():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
    result = {
        "errCode": 0,
        "errMsg": "success",
    }

    data = request.json['params']
    try:
        admin.updateTrade(int(data['tradeNo']), data['status'], data['tradePrice'], data['tradeAmount'],
                          f"{data['tradeDate']} {data['tradeTime']}", data['tradeMsg'])



    except Exception as ex:
        result = {
            "errCode": -1,
            "errMsg": "update Error",
        }
        logger.error(ex)
    return jsonify(result)
    pass


@app.route('/custom/edit', methods=['POST'])
def editCustom():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
    result = {
        "errCode": 0,
        "errMsg": "success",
    }

    data = request.json['params']
    try:
        admin.updateCustom(data['Id'], data['Name'],data['Type'])

    except Exception as ex:
        logger.error(ex)
        result = {
            "errCode": -1,
            "errMsg": str(ex),
        }
    return jsonify(result)


@app.route('/custom/del', methods=['POST'])
def delCustom():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
    result = {
        "errCode": 0,
        "errMsg": "success",
    }

    data = request.json['params']
    try:
        admin.delCustom(data['Id'])

    except Exception as ex:
        logger.error(ex)
        result = {
            "errCode": -1,
            "errMsg": str(ex),
        }
    return jsonify(result)


@app.route('/editSetting', methods=['POST'])
def updateSetting():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
    result = {
        "errCode": 0,
        "errMsg": "success",
    }

    data = request.json['params']
    try:
        admin.updateSetting(data['name'], data['value'])
        setting.loadSetting()

    except Exception as ex:
        logger.error(ex)
        result = {
            "errCode": -1,
            "errMsg": "update Error",
        }
    return jsonify(result)


@app.route('/setting/list', methods=['GET'])
def getSettings():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
    datas = admin.getSettings()
    settings = []
    for data in datas:
        settings.append({'name': data[1], 'value': data[2]})

    result = {'settings': settings}
    return jsonify(result)


@app.route('/adminlogin', methods=['POST'])
def adminlogin():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
    param = request.json['params']

    user = param['username']
    pwd = param['password']
    data = admin.validUser(user, pwd)
    result = {"code": data[0], "msg": data[1], 'user': user}
    return jsonify(result)


@app.route('/updatePwd', methods=['POST'])
def changePwd():
    logger.info(f'收到来自{request.remote_addr}的请求 {request.url}  {request.data}')
    param = request.json['params']
    user = param['user']
    pwd = param['pwd']
    try:
        admin.updatePwd(user, pwd)
        result = {'code': 0, 'msg': ''}
    except Exception as ex:
        logger.error(ex)
        result = {'code': -1, 'msg': 'change pwd exception'}

    return jsonify(result)


if __name__ == "__main__":
    # 生产模式关闭debug
    # app.run(host='0.0.0.0', debug=True)
    socketio.run(app, host='0.0.0.0', port=5000)
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    #
    # server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    # print('server start')
    # server.serve_forever()
