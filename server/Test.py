import requests
import urllib3

code ='000001.SZ'
instrument = code.split('.')[0]
exchange = code.split('.')[1]
#header={'User-Agent': 'curl/7.51.0'}

url = f"http://hq.sinajs.cn/list={exchange.lower()}{instrument}"
print(url)
#response = requests.get(url)



http=urllib3.PoolManager()
resp=http.request('GET',url)
msg = str(resp.data).split(',')
print(msg)





# x = os.popen('Rscript Option-Price.R aa').readlines()
# print(x)
