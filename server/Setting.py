#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: duanqing
# @created on: 2018/4/10 9:54
# @desc  :

from Dos import OptionDos

import logging
class Setting(object):
    def __init__(self):

        self.setting={}
        self.dos = OptionDos()
        self.loadSetting()

    def loadSetting(self):
        logging.info('装载系统设置')
        datas=self.dos.GetSetting()
        for data in datas:
            self.setting[data[1]]=data[2]

    def getValue(self,name):
        return  self.setting[name]