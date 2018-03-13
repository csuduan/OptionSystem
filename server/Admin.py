#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: duanqing
# @created on: 2018/3/12 10:05
# @desc  :

from Dos import OptionDos

class Admin(object):
    def __init__(self):
        self.dos=OptionDos()
        pass

    def getPagedEnquiry(self,page,pageSize):
        count=self.dos.GetEnquiryCount()
        datas=self.dos.GetPagedEnquiry(page,pageSize)
        return (count, datas)

        pass

    def getPagedTrade(self,page,pageSize,filters):
        count=self.dos.GetTradeCount(filters)
        datas=self.dos.GetPagedTrade(page,pageSize,filters)

        return  (count,datas)

    def updateTrade(self,tradeNo,tradeStatus,tradePrice,tradeAmount,tradeTms,tradeMsg):
        self.dos.UpdateTrade(tradeNo,tradeStatus,tradePrice,tradeAmount,tradeTms,tradeMsg)
        pass
