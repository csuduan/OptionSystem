library(quantmod)
library(fOptions)
library(RODBC)
server= "R630"
user  = "yanmi"
passwd= "yanmi"
DataBase<-"DBSELF"
DataBase3<-"U_yanmi"


args=commandArgs(T)
#stock=args[1]
#T=args[2]

stock='600681.SH'
T=6.12/12
###### DATA ######
sqlStr<-paste0("SELECT [S_INFO_WindCode],[TRADE_DT],[S_DQ_OPEN],[S_DQ_CLOSE],[S_DQ_PCTCHANGE],[S_DQ_ADJPRECLOSE],[S_DQ_ADJOPEN],[S_DQ_ADJCLOSE],[S_DQ_VOLUME],[S_DQ_AMOUNT]",
              " FROM [WIND].[db_datareader].[ASHAREEODPRICES]",
              " WHERE S_INFO_WINDCODE='",stock,"' AND TRADE_DT>20130101 ",
              " ORDER BY TRADE_DT ASC")
localdb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
StockInfo <- sqlQuery(localdb, sqlStr)
close(localdb)
StockInfo[,"OverNight"]<-StockInfo[,"S_DQ_ADJOPEN"]/StockInfo[,"S_DQ_ADJPRECLOSE"]-1
StockInfo[,"Daily"]<-StockInfo[,"S_DQ_ADJCLOSE"]/StockInfo[,"S_DQ_ADJOPEN"]-1
StockInfo[,"absOverNight"]<-abs(StockInfo[,"S_DQ_ADJOPEN"]/StockInfo[,"S_DQ_ADJPRECLOSE"]-1)
StockInfo[,"absDaily"]<-abs(StockInfo[,"S_DQ_ADJCLOSE"]/StockInfo[,"S_DQ_ADJOPEN"]-1)

############# SIGMA ################
start<-which(StockInfo[,"TRADE_DT"]==20180206)
info<-StockInfo[(start-119):start,]
S=info[1,"S_DQ_CLOSE"]
K=info[1,"S_DQ_CLOSE"]
X=K
T<-6.12/12

### realized vol ###
N1=120
stockM<-StockInfo[(start-N1+1):start,]
stockM[,"XI"]<-log(stockM[,"S_DQ_ADJCLOSE"]/stockM[,"S_DQ_ADJPRECLOSE"])
XH<-sum(stockM[,"XI"])/N1
V1<-sqrt(sum((stockM[,"XI"]-XH)^2)/(N1-1))
sigma=V1*1.33*sqrt(252)
s=sigma
############## OPTION PRICE #############
OptionP<-GBSOption(S=info[1,"S_DQ_CLOSE"],X=info[1,"S_DQ_CLOSE"]*1.0,Time=T,r=0.04,b=0,sigma=s)
A<-OptionP@price
B<-A/stockM[nrow(stockM),"S_DQ_CLOSE"]

norm <- function(x) sqrt(x%*%x)

#cat(B)
