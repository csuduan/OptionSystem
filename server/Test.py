import pycurl
import io
from urllib.parse import urlencode
import json

url="http://192.168.1.38:5000/enquiry"
#url='www.baidu.com'
data={"stock":"000001.SZ","period":"30","strikePercent":" 1.02","amount":20}

c = pycurl.Curl()


b = io.BytesIO()
c.setopt(c.WRITEDATA, b)
c.setopt(c.URL, url)
c.setopt(c.POST, 1)
c.setopt(c.HTTPHEADER, ['Accept: application/json','Content-Type: application/json'])
c.setopt(c.POSTFIELDS, json.dumps(data))

# c.setopt(c.FOLLOWLOCATION, 1)
# c.setopt(c.HEADER, True)

for i in range(1000) :
    c.perform()

html = b.getvalue().decode('utf8')

b.close()
c.close()

print(html)



#x = os.popen('Rscript Option-Price.R aa').readlines()
# print(x)