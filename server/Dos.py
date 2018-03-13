import pymssql


class OptionDos(object):
    '''
    期权DOS
    '''
    conn=None;
    def __init__(self):
        # Conn初始化
        self.conn = pymssql.connect("192.168.1.10", "quant", "quant", "OptionSystem", charset='cp936')

    def GetConn(self):
        #todo 连接状态检查
        return  self.conn;

    def AddEnquiry(self,code,period,strikePct,date,tmPeriod,cost,maxAmount):
        conn=self.GetConn()
        cursor = conn.cursor()
        sql=f"insert into Enquiry values('{date}','{tmPeriod}','{code}','{period}',{strikePct},{maxAmount},{cost},getdate())"
        cursor.execute(sql)
        conn.commit()


    def GetEnquiry(self,code,period,strikePct,tradingDay,tmPeriod):
        cursor = self.GetConn().cursor()
        sql = f"select * from  Enquiry where code='{code}' and period='{period}' and strikePct='{strikePct}' and TradingDay='{tradingDay}' and tmPeriod='{tmPeriod}' order by Tms desc"
        cursor.execute(sql)
        enqury = cursor.fetchone()
        return  enqury

    def GetEnquiryByNo(self,no):
        cursor = self.GetConn().cursor()
        sql = f"select * from  Enquiry where no={no}"
        cursor.execute(sql)
        enquiry = cursor.fetchone()
        return  enquiry

    def AddTrade(self,date,custom,code,period,strikePct,amount,cost,enquiryNo):
        conn = self.GetConn()
        cursor = conn.cursor()
        sql = f"insert into Trade(tradingDay,Custom,code,Period,StrikePct,Amount,cost,EnquiryNo,insertTms,Status)  values('{date}','{custom}','{code}','{period}',{strikePct},{amount},{cost},{enquiryNo},getdate(),'UnTraded')"
        cursor.execute(sql)

        cursor.execute("SELECT SCOPE_IDENTITY()")
        tradeNo = cursor.fetchone()
        conn.commit()
        return  int(tradeNo[0])

    def GetTrade(self,tradeNo,custom):
        cursor = self.GetConn().cursor()
        sql = f"select * from  Trade where No={tradeNo} and custom='{custom}'"
        cursor.execute(sql)
        trade = cursor.fetchone()
        return trade

    def GetPagedTrade(self,page,pagesize,filters):
        where='1=1 '
        for key in filters:
            if filters[key] !=None and filters[key]!='':
                where+=f" and {key} = '{filters[key]}'"


        cursor = self.GetConn().cursor()
        offset=(page-1)*pagesize
        sql = f"select * from  Trade where {where} order by no desc offset {offset} rows fetch next {pagesize} rows only  "
        cursor.execute(sql)
        trades = cursor.fetchall()
        return trades

    def GetTradeCount(self,filters):
        where = '1=1 '
        for key in filters:
            if filters[key] != None and filters[key] != '':
                where += f" and {key} = '{filters[key]}'"

        cursor = self.GetConn().cursor()
        sql = f"select count(0) from  Trade where {where}"
        cursor.execute(sql)
        tradeCount = cursor.fetchone()
        return tradeCount[0]

    def GetEnquiryCount(self):
        cursor = self.GetConn().cursor()
        sql = f"select count(0) from  enquiry "
        cursor.execute(sql)
        enquiryCount = cursor.fetchone()
        return enquiryCount[0]

    def GetPagedEnquiry(self,page,pagesize):
        cursor = self.GetConn().cursor()
        offset=(page-1)*pagesize
        sql = f"select * from   enquiry order by no desc offset {offset} rows fetch next {pagesize} rows only  "
        cursor.execute(sql)
        enquirys = cursor.fetchall()
        return enquirys

    def UpdateTrade(self,tradeNo,tradeStatus,tradePrice,tradeAmount,tradeTms,tradeMsg):
        conn = self.GetConn()
        cursor = conn.cursor()
        sql = f"update trade set status='{tradeStatus}',tradePrice='{tradePrice}',tradeAmount='{tradeAmount}',tradeTms='{tradeTms}',tradeMsg='{tradeMsg}' where no={tradeNo}  "
        cursor.execute(sql)
        conn.commit()

