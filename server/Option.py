import os

from Dos import OptionDos
from Util import getStockPrice,SendEmail

#os.environ['R_HOME'] = 'C:\Program Files\R\R-3.3.3'
#os.environ['R_USER'] = 'C:\Program Files\Anaconda3\Lib\site-packages\rpy2'
import rpy2.robjects as robjects
import time
import math


class Option(object):
    '''
    期权操作
    '''

    def __init__(self):
        #OptionSystemR初始化
        self.r = robjects.r
        self.r.source("./OptionSystem.R")
        self.dos=OptionDos()
        self.setting={}
        self.loadSetting()

    def getEnquiry(self,stock,period,strikePercent,amount):
        date = time.strftime("%Y%m%d", time.localtime())
        tm = time.strftime("%H:%M", time.localtime())
        tmPeiod = time.strftime("%p", time.localtime())
        if tm < self.setting['enquiryStart'] or tm > self.setting['enquiryEnd']:
            return  (-1,"Not trading time,Please try again later")

        #涨跌幅过大，重新计算报价
        price=getStockPrice(stock)
        if abs(price[1]-price[0])/price[0]>0.05:
            ret = self.calOptionCost(stock, period, strikePercent, amount)
            if ret[0] != 0:
                return (ret[0], ret[1])

        #数据库获取不到询价数据，则重新计算报价
        data = self.dos.GetEnquiry(stock, period, strikePercent, date, tmPeiod)
        if data == None or data==[]:
            ret = self.calOptionCost(stock, period, strikePercent, amount)
            if ret[0] == 0:
                data = self.dos.GetEnquiry(stock, period, strikePercent, date, tmPeiod)
            else:
                return (ret[0],ret[1])

        return (0,data)

    def calOptionCost(self,code,period,strikePercent,amount):
        tms = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        time.clock()
        print(f'计算报价开始 {code} {period} {strikePercent}')
        try:
            result = self.r.BidPrice(code,amount, period, strikePercent)
            if result[0] == 0:
                date = time.strftime("%Y%m%d", time.localtime())
                tmPeiod = time.strftime("%p", time.localtime())
                self.dos.AddEnquiry(code, period, strikePercent, date, tmPeiod, round(result[1]+0.005,2), result[2])
                print(f'计算并保持报价成功 {code} {period} {strikePercent} 期权费:{result[1]}  时间:{tms}')
                result=(0,"")

        except Exception as ex:
            result=(-2,"BidPrice Exception,Please Contact Us!")
            print(f'计算报价失败 {code} {period} {strikePercent} {ex}')

        return result

    def trade(self,custom,enquiryNo,amount):
        data = self.dos.GetEnquiryByNo(enquiryNo)
        if data == None or data == []:
            return  (-1, "can not find enquiry Record!")

        date = time.strftime("%Y%m%d", time.localtime())
        tm = time.strftime("%H:%M", time.localtime())
        tmPeiod = time.strftime("%p", time.localtime())
        if tm < self.setting['tradeStart'] or tm > self.setting['tradeEnd']:
            return  (-1," Forbid  trade,Now")

        code=data[3]
        period=data[4]
        strikePct=data[5]
        maxAmount=data[6]
        cost=data[7]
        enquiryTradingDay=data[1]
        enquiryTmPeroid=data[2]

        date = time.strftime("%Y%m%d", time.localtime())
        tmPeriod = time.strftime("%p", time.localtime())

        if date!=enquiryTradingDay  or tmPeriod!=enquiryTmPeroid:
            return (-1, "last enquiry timeout!")

        if amount>maxAmount:
            return (-1, "amount is too big than maxAmount !")

        #交易信息入库
        tradeNo=self.dos.AddTrade(date,custom,code,period,strikePct,amount,cost,enquiryNo)

        #发送邮件通知
        msg=f''' 
           tradeNo       tradingDay   code        period    strikePct    Amount      custom
           {tradeNo}            {date}    {code}    {period}         {strikePct}        {amount}万      {custom}
         '''
        #SendEmail(msg)

        return (0,tradeNo)


    def tradeQry(self,custom,tradeNo):
        data = self.dos.GetTrade(tradeNo,custom)


        if data == None or data == []:
            return  (-1, "can not find trade Record!")

        if data[2] != custom:
            return (-1, "custom not match!")

        return (0,data)


    def loadSetting(self):
        datas=self.dos.GetSetting()
        for data in datas:
            self.setting[data[1]]=data[2]




