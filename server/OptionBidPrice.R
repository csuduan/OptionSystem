library(quantmod)
library(fOptions)
library(RODBC)
library(RCurl)
server= "R630"
user  = "yanmi"
passwd= "yanmi"
DataBase<-"DBSELF"
DataBase3<-"U_yanmi"

###### Date ######
Today<-20180207
Yesterday<-20180206

###### Input ######
Code<-"000001.SZ"
Period<-1
StrikePercent<-1.05

get_current_price <- function(Code)
{
  instrument_id<-strsplit(Code,'\\.')[[1]][1]
  exchange_id<-strsplit(Code,'\\.')[[1]][2]
  instrument_exchange_id = paste(tolower(exchange_id), instrument_id, sep="")
  
  url_base = "http://hq.sinajs.cn/list="
  url = paste(url_base, instrument_exchange_id, sep="")
  url_encoded = URLencode(url)
  
  respond = readLines(url_encoded,encoding="GB2312")
  column_list = unlist(strsplit(respond[1],split=","))
  return(column_list[4])
} 

BidPrice<-function(Today,Code,Period,StrikePercent)
{

 ############## DATA ##################
 sqlStr<-paste("SELECT [S_INFO_WindCode],[TRADE_DT],[S_DQ_OPEN],[S_DQ_CLOSE],[S_DQ_PCTCHANGE],[S_DQ_ADJPRECLOSE],[S_DQ_ADJOPEN],[S_DQ_ADJCLOSE],[S_DQ_VOLUME],[S_DQ_AMOUNT],[S_DQ_ADJFACTOR]",
              " FROM [WIND].[db_datareader].[ASHAREEODPRICES]",
              " WHERE S_INFO_WINDCODE=", "'" ,Code, "'" ," AND TRADE_DT>20160101 ",
              " ORDER BY TRADE_DT ASC", sep='')
localdb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
StockInfo <- sqlQuery(localdb, sqlStr)
close(localdb)
StockInfo[,"OverNight"]<-StockInfo[,"S_DQ_ADJOPEN"]/StockInfo[,"S_DQ_ADJPRECLOSE"]-1
StockInfo[,"Daily"]<-StockInfo[,"S_DQ_ADJCLOSE"]/StockInfo[,"S_DQ_ADJOPEN"]-1
StockInfo[,"absOverNight"]<-abs(StockInfo[,"S_DQ_ADJOPEN"]/StockInfo[,"S_DQ_ADJPRECLOSE"]-1)
StockInfo[,"absDaily"]<-abs(StockInfo[,"S_DQ_ADJCLOSE"]/StockInfo[,"S_DQ_ADJOPEN"]-1)

############# option info ################
N1=Period

###
current_price<- as.numeric(get_current_price(Code))
  
final<-(nrow(StockInfo)+1)
StockInfo[final,"TRADE_DT"]<-Today
StockInfo[final,"S_INFO_WindCode"]<-Code
StockInfo[final,"S_DQ_CLOSE"]<-current_price
StockInfo[final,"S_DQ_ADJCLOSE"]<-current_price*StockInfo[(final-1),"S_DQ_ADJFACTOR"]
StockInfo[final,"S_DQ_ADJPRECLOSE"]<-StockInfo[(final-1),"S_DQ_ADJCLOSE"]
info<-StockInfo[(nrow(StockInfo)-N1+1):nrow(StockInfo),]
Strike=current_price*StrikePercent
T<-Period/360

############# realized vol #############

info[,"XI"]<-log(info[,"S_DQ_ADJCLOSE"]/info[,"S_DQ_ADJPRECLOSE"])
XH<-sum(info[,"XI"])/N1
V1<-sqrt(sum((info[,"XI"]-XH)^2)/(N1-1))
sigma=V1*1.3*sqrt(252)
s=sigma

############## EUROPEAN OPTION PRICE #############
OptionP<-GBSOption(S=current_price,X=Strike,Time=T,r=0.04,b=0,sigma=s)
A<-OptionP@price
B<-A/current_price
return(c(B,current_price))
}