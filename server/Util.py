import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def getStockPrice(code):
    instrument=code.split('.')[0]
    exchange=code.split('.')[1]
    url=f"http://hq.sinajs.cn/list={exchange.lower()}{instrument}"
    response = requests.get(url)
    msg=response.text.split(',')

    return  (float(msg[1]),float(msg[3]))

def SendEmail(msg):
    receiver = ['duanq@quantinv.com']
    subject = '期权交易下达指令（测试）'
    smtpserver = 'smtp.126.com'
    username = 'quantinv@126.com'
    password = 'quantfly2016'

    msg = MIMEText(msg, 'text', 'utf-8')  # 中文需参数‘utf-8’，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')
    msg['To'] = ";".join(receiver)
    msg['From'] = username

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(username, receiver, msg.as_string())
    smtp.quit()

def notice(context,receivers):
    subject = '缺勤记录-测试（请忽略）'
    smtpserver = 'smtp.126.com'
    username = 'csuduan@126.com'
    password = 'quantfly2016'

    msg = MIMEText(context,'text','utf-8')#中文需参数‘utf-8’，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')
    msg['To']=";".join(receivers)
    msg['From']=username

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(username, receivers, msg.as_string())
    smtp.quit()
    pass
