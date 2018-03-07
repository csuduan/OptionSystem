library(quantmod)
library(fOptions)
library(RODBC)
library(RCurl)
library(fGarch)
library(qcc)
library(lubridate)

server= "R630"
user  = "yanmi"
passwd= "yanmi"
DataBase<-"DBSELF"
DataBase3<-"U_yanmi"
lamda=0.94
r=0.04
Today<-gsub("-","",Sys.Date())

###### Input ######
Code<-c("000563.SZ")
Period<-c("1M")
StrikePercent<-c(1)
Asset<-c(200000)
  
SHSZ.DN <- "'SZSE'" 
sqlStr <- paste("SELECT TRADE_DAYS",
                "FROM [WIND].[db_datareader].[ASHARECALENDAR]",
                "WHERE TRADE_DAYS>=",20160101,
                "AND S_INFO_EXCHMARKET = ", SHSZ.DN,
                "ORDER BY TRADE_DAYS ASC")

wddb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
while (wddb < 0) {
  wddb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
}
TRADE_DT <- sqlQuery(wddb, sqlStr, as.is=TRUE)
close(wddb)

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

BidPrice<-function(Code,Asset,Period,StrikePercent)
{

l<-as.numeric(strsplit(Period,"")[[1]][1])
unit<-strsplit(Period,"")[[1]][2]
if(unit=="M"){N1=l*30}
if(unit=="W"){N1=l*7}

Error=0
############## STOCK DATA ##################
sqlStr<-paste("SELECT [S_INFO_WindCode],[TRADE_DT],[S_DQ_OPEN],[S_DQ_CLOSE],[S_DQ_PCTCHANGE],[S_DQ_ADJPRECLOSE],[S_DQ_ADJOPEN],[S_DQ_ADJCLOSE],[S_DQ_VOLUME],[S_DQ_AMOUNT],[S_DQ_ADJFACTOR]",
              " FROM [WIND].[db_datareader].[ASHAREEODPRICES]",
              " WHERE S_INFO_WINDCODE=", "'" ,Code, "'" ," AND TRADE_DT>20160101 AND TRADE_DT<",Today,
              " ORDER BY TRADE_DT ASC", sep='')
localdb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
StockInfo <- sqlQuery(localdb, sqlStr)
close(localdb)

sqlStr<-paste("SELECT[S_INFO_WINDCODE],[S_TYPE_ST],[ENTRY_DT],[REMOVE_DT],[ANN_DT]",
              "FROM [WIND].[db_datareader].[ASHAREST]",
              "where S_INFO_WINDCODE='",Code,"'",
              " ORDER BY ANN_DT DESC",sep='')
localdb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
ST <- sqlQuery(localdb, sqlStr)
close(localdb)

###### ERROR CONDITION ######
if(sum(which(TRADE_DT[,1]==Today))==0) {Error=1}

if(StockInfo[1,"TRADE_DT"]>=20170101) {Error=1}### Recent one year New Stock ###

if(sum(StockInfo[(nrow(StockInfo)-N1):nrow(StockInfo),"S_DQ_VOLUME"]==0)>0){Error=1}###Recent stop ###

if(mean(StockInfo[(nrow(StockInfo)-N1+1):nrow(StockInfo),"S_DQ_AMOUNT"])<30000){Error=1}###Low Turnover ###

if(sum(StockInfo[(nrow(StockInfo)-N1):nrow(StockInfo),"S_DQ_PCTCHANGE"]< -9.5)>=2|sum(StockInfo[(nrow(StockInfo)-N1):nrow(StockInfo),"S_DQ_PCTCHANGE"]>9.5)>2){Error=1}

if(nrow(ST)!=0) ### ST stock ###
{
  if(is.na(ST[1,"REMOVE_DT"])){Error=1}
}

if(Error==1)
{
  return(c(Error,"Please Contact Us!"))
}

############# option done ################
if(Error==0)
{
  current_price<- as.numeric(get_current_price(Code))
  final<-(nrow(StockInfo)+1)
  StockInfo[final,"TRADE_DT"]<-Today
  StockInfo[final,"S_INFO_WindCode"]<-Code
  StockInfo[final,"S_DQ_CLOSE"]<-current_price
  StockInfo[final,"S_DQ_ADJCLOSE"]<-current_price*StockInfo[(final-1),"S_DQ_ADJFACTOR"]
  StockInfo[final,"S_DQ_ADJPRECLOSE"]<-StockInfo[(final-1),"S_DQ_ADJCLOSE"]
  Strike=current_price*StrikePercent
  T<-N1/30/12
  
  ####### EWMA ######
  epi<-data.frame(matrix(NA, nrow=0, ncol=2))  
  names(epi)<-c("Number","Eps")
  
  if(nrow(StockInfo)>76)
  {
    StockInfo<-StockInfo[(nrow(StockInfo)-76):nrow(StockInfo),]
  }
  epi[1,"Number"]<-1
  epi[1,"Eps"]<-((StockInfo[2,"S_DQ_ADJCLOSE"]/StockInfo[2,"S_DQ_ADJPRECLOSE"])-1)^2
  
  for(k in 3:nrow(StockInfo))
  {
    num=k-1
    epi[num,"Number"]<-num
    epi[num,"Eps"]<-(lamda)*epi[(num-1),"Eps"]+(1-lamda)*(StockInfo[(num-1),"S_DQ_ADJCLOSE"]/StockInfo[(num-1),"S_DQ_ADJPRECLOSE"]-1)^2
  }
  sigma<-sqrt(epi[nrow(epi),"Eps"]*365)*1.1
  s=sigma
  
  CRRTree<-CRRBinomialTreeOption(TypeFlag = "ca", S = current_price, X = Strike, Time = T, r = 0.042, b = 0, sigma = s, n = N1)
  A<-CRRTree@price
  B<-A/current_price
  limit<-Asset
  return(c(Error,B,limit))
  
}
}


