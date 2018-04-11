#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: duanqing
# @created on: 2018/4/9 16:24
# @desc  :
from Dos import OptionDos
class DayFlowCtrl(object):
    def __init__(self,setting):
        self.date = None
        self.setting=setting
        self.flowData={};
        self.dos=OptionDos()



    def CheckFlowCtrl(self,customId,date):
        if date!=self.date:
            self.date=date
            self.ResetFlowData()

        '''流控检测'''

        custom=self.dos.GetCustom(customId)

        dayFlow=self.setting.getValue('dayFlowAnony')
        if custom != None :
            type=custom[3]
            if type=='VIP':
                dayFlow=self.setting.getValue('dayFlowVip')
            if type=='COMMON':
                dayFlow=self.setting.getValue('dayFlowCommon')

        if self.flowData.get(customId)==None:
            self.flowData[customId]=1
        else:
            self.flowData[customId]=self.flowData[customId]+1
            if self.flowData[customId]>int(dayFlow ):
                return  False;

        return True;


    def ResetFlowData(self):
        '''重置流控数据'''
        self.flowData = {};