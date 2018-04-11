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

    def getPagedCustom(self,page,pageSize):
        count=self.dos.GetCustomCount()
        datas = self.dos.GetPagedCustom(page, pageSize)
        return (count, datas)



    def updateTrade(self,tradeNo,tradeStatus,tradePrice,tradeAmount,tradeTms,tradeMsg):
        self.dos.UpdateTrade(tradeNo,tradeStatus,tradePrice,tradeAmount,tradeTms,tradeMsg)
        pass

    def updateSetting(self,name,value):
        self.dos.UpdateSetting(name,value)

    def updateCustom(self,id,name,type):
        custom=self.dos.GetCustom(id)
        if custom == None:
            self.dos.AddCustom(id,name,type)
        else:
            self.dos.UpdateCustom(id,name,type)

    def delCustom(self,id):
        custom=self.dos.GetCustom(id)
        if custom != None:
            self.dos.DelCustom(id)

    def getSettings(self):
        datas=self.dos.GetSetting()
        return  datas

    def validUser(self,user,pwd):
        data=self.dos.GetUser(user)
        if data ==None:
            return (-1,"无此用户")

        if data[1]!=pwd:
            return (-2,"密码不正确");

        return (0,"")

    def updatePwd(self,user,pwd):
        self.dos.UpdatePwd(user,pwd)