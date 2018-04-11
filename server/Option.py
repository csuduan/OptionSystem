import os

from Dos import OptionDos
from RiskCtrl import DayFlowCtrl
import Util

#os.environ['R_HOME'] = 'C:\Program Files\R\R-3.3.3'
#os.environ['R_USER'] = 'C:\Program Files\Anaconda3\Lib\site-packages\rpy2'
import rpy2.robjects as robjects
import time
import math
import logging


class Option(object):
    '''
    期权操作
    '''

    def __init__(self,setting):
        #OptionSystemR初始化
        self.r = robjects.r
        self.r.source("./OptionSystem.R")
        self.dos=OptionDos()
        self.setting=setting
        self.dayFlowCtrl=DayFlowCtrl(setting)
        pass

    def getEnquiry(self,custom,stock,period,strikePercent,amount):
        date = time.strftime("%Y%m%d", time.localtime())
        tm = time.strftime("%H:%M", time.localtime())
        tmPeiod = time.strftime("%p", time.localtime())



        if tm < self.setting.getValue('enquiryStart') or tm > self.setting.getValue('enquiryEnd'):
            return  (-1,"Not trading time,Please try again later")

        if amount<float(self.setting.getValue('minAmount')) or amount>float(self.setting.getValue('maxAmount')):
            return (-1,"amount must between "+self.setting.getValue('minAmount')+'-' +self.setting.getValue('maxAmount') )

        #流控检测
        if self.dayFlowCtrl.CheckFlowCtrl(custom,date)==False:
            return (-1,'reach max DayFlow')

        #涨跌幅过大，重新计算报价
        price=Util.getStockPrice(stock)
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
        logging.info(f'计算报价开始 {code} {period} {strikePercent}')
        try:
            result = self.r.BidPrice(code,amount, period, strikePercent)
            if result[0] == 0:
                date = time.strftime("%Y%m%d", time.localtime())
                tmPeiod = time.strftime("%p", time.localtime())
                self.dos.AddEnquiry(code, period, strikePercent, date, tmPeiod, round(result[1]+0.00005,4))
                logging.info(f'计算并保持报价成功 {code} {period} {strikePercent} 期权费:{result[1]}  时间:{tms}')
                result=(0,"")

        except Exception as ex:
            logging.error(ex)
            result=(-2,"BidPrice Exception,Please Contact Us!")
            logging.error(f'计算报价失败 {code} {period} {strikePercent} {ex}')

        return result

    def trade(self, customID, enquiryNo, amount):

        custom=self.dos.GetCustom(customID)
        if custom==None:
            return (-1, "custom not registed!")

        data = self.dos.GetEnquiryByNo(enquiryNo)
        if data == None or data == []:
            return  (-1, "can not find enquiry Record!")

        date = time.strftime("%Y%m%d", time.localtime())
        tm = time.strftime("%H:%M", time.localtime())
        tmPeiod = time.strftime("%p", time.localtime())


        if tm < self.setting.getValue('tradeStart') or tm > self.setting.getValue('tradeEnd'):
            return  (-1," Forbid  trade,Now")

        if amount < float(self.setting.getValue('minAmount')) or amount > float(self.setting.getValue('maxAmount')):
            return (-1, "amount must between " + self.setting.getValue('minAmount') + '-' + self.setting.getValue('maxAmount'))


        enquiryTradingDay=data[1]
        enquiryTmPeroid=data[2]
        code=data[3]
        period=data[4]
        strikePct=data[5]
        cost=data[6]


        date = time.strftime("%Y%m%d", time.localtime())
        tmPeriod = time.strftime("%p", time.localtime())

        if date!=enquiryTradingDay  or tmPeriod!=enquiryTmPeroid:
            return (-1, "last enquiry timeout!")


        try:
            result=self.r.HedgeTra(code,amount,period,strikePct)
            volume=result[1]
            dueDate=result[2]

        except Exception as ex:
            logging.error(ex)
            return (-2,"HedgeTra Exception,Please Contact Us!")

        #交易信息入库
        tradeNo=self.dos.AddTrade(date, customID, code, period, strikePct, amount, cost, enquiryNo, volume, dueDate)

        #发送邮件通知
        msg= f''' 
           tradeNo       tradingDay   code        period    strikePct    Amount      custom     volume      dueDate
           {tradeNo}            {date}    {code}    {period}         {strikePct}        {amount}万      {customID}   {volume}  {dueDate}
         '''

        try:

            emailReceiver=self.setting.getValue('emailReceiver')
            if(emailReceiver!=None and emailReceiver!=''):
                receiver=emailReceiver.split(',')
                Util.SendEmail(msg,receiver)
        except Exception as ex:
            logging.error('send email error',ex)


        return (0,tradeNo)


    def tradeQry(self,custom,tradeNo):
        data = self.dos.GetTrade(tradeNo,custom)


        if data == None or data == []:
            return  (-1, "can not find trade Record!")

        if data[2] != custom:
            return (-1, "custom not match!")

        return (0,data)






