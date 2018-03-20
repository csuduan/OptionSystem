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

Volatility<-function(Code)
{
r=0.04
lamda=0.94

SHSZ.DN <- "'SZSE'" 
sqlStr <- paste("SELECT TRADE_DAYS",
                "FROM [WIND].[db_datareader].[ASHARECALENDAR]",
                "WHERE TRADE_DAYS>=",20160101,
                "AND S_INFO_EXCHMARKET = ", SHSZ.DN,
                "ORDER BY TRADE_DAYS ASC")
wddb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
TRADE_DT <- sqlQuery(wddb, sqlStr, as.is=TRUE)
close(wddb)

Today<-gsub("-","",Sys.Date())
sqlStr<-paste("SELECT [S_INFO_WindCode],[TRADE_DT],[S_DQ_OPEN],[S_DQ_CLOSE],[S_DQ_PCTCHANGE],[S_DQ_ADJPRECLOSE],[S_DQ_ADJOPEN],[S_DQ_ADJCLOSE],[S_DQ_VOLUME],[S_DQ_AMOUNT],[S_DQ_ADJFACTOR]",
              " FROM [WIND].[db_datareader].[ASHAREEODPRICES]",
              " WHERE S_INFO_WINDCODE=", "'" ,Code, "'" ," AND TRADE_DT>20170101 AND TRADE_DT<",Today,
              " ORDER BY TRADE_DT ASC", sep='')
localdb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
StockInfo <- sqlQuery(localdb, sqlStr)
close(localdb)
current_price<- as.numeric(get_current_price(Code))
final<-(nrow(StockInfo)+1)
StockInfo[final,"TRADE_DT"]<-Today
StockInfo[final,"S_INFO_WindCode"]<-Code
StockInfo[final,"S_DQ_CLOSE"]<-current_price
StockInfo[final,"S_DQ_ADJCLOSE"]<-current_price*StockInfo[(final-1),"S_DQ_ADJFACTOR"]
StockInfo[final,"S_DQ_ADJPRECLOSE"]<-StockInfo[(final-1),"S_DQ_ADJCLOSE"]

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
return(s)
}

BidPrice<-function(Code,Asset,Period,StrikePercent)
{
Today<-gsub("-","",Sys.Date()) 
SHSZ.DN <- "'SZSE'" 
sqlStr <- paste("SELECT TRADE_DAYS",
                "FROM [WIND].[db_datareader].[ASHARECALENDAR]",
                "WHERE TRADE_DAYS>=",20160101,
                "AND S_INFO_EXCHMARKET = ", SHSZ.DN,
                "ORDER BY TRADE_DAYS ASC")
wddb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
TRADE_DT <- sqlQuery(wddb, sqlStr, as.is=TRUE)
close(wddb)
localdb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
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
StockInfo <- sqlQuery(localdb, sqlStr)

sqlStr<-paste("SELECT[S_INFO_WINDCODE],[S_TYPE_ST],[ENTRY_DT],[REMOVE_DT],[ANN_DT]",
              "FROM [WIND].[db_datareader].[ASHAREST]",
              "where S_INFO_WINDCODE='",Code,"'",
              " ORDER BY ANN_DT DESC",sep='')
ST <- sqlQuery(localdb, sqlStr)

sqlStr<-paste("SELECT[S_INFO_WINDCODE],[EX_DATE]",
              "FROM [WIND].[db_datareader].[ASHAREEXRIGHTDIVIDENDRECORD]",
              "where S_INFO_WINDCODE='",Code,"'",
              " ORDER BY EX_DATE DESC",sep='')
DIV <- sqlQuery(localdb, sqlStr)

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

if(Asset>20){Error=1}

if(StrikePercent>1.03|StrikePercent<0.97){Error=1}

if(nrow(DIV)!=0) ### 除权除息 ##
{
  if(julian(as.Date(as.character(DIV[1,"EX_DATE"]),"%Y%m%d"),origin=as.Date(as.character(Today),"%Y%m%d"))[[1]]<N1&julian(as.Date(as.character(DIV[1,"EX_DATE"]),"%Y%m%d"),origin=as.Date(as.character(Today),"%Y%m%d"))[[1]]>0)
  {
    Error=1
  }
}


close(localdb)
if(Error==1)
{
  return(c(Error,"Please Contact Us!"))
}

############# option done ################
if(Error==0)
{
  l<-as.numeric(strsplit(Period,"")[[1]][1])
  unit<-strsplit(Period,"")[[1]][2]
  if(unit=="M"){N1=l*30}
  if(unit=="W"){N1=l*7}
  current_price<- as.numeric(get_current_price(Code))
  Strike=current_price*StrikePercent
  T<-N1/30/12
  s=Volatility(Code)
  
  CRRTree<-CRRBinomialTreeOption(TypeFlag = "ca", S = current_price, X = Strike, Time = T, r = 0.042, b = 0, sigma = s, n = N1)
  A<-CRRTree@price
  B<-A/current_price
  
  limit<-Asset
  
  return(c(Error,B,limit))
  
}
}


HedgeTra<-function(Code,Asset,Period,StrikePercent)
{
  Today<-gsub("-","",Sys.Date())
  SHSZ.DN <- "'SZSE'" 
  sqlStr <- paste("SELECT TRADE_DAYS",
                  "FROM [WIND].[db_datareader].[ASHARECALENDAR]",
                  "WHERE TRADE_DAYS>=",20160101,
                  "AND S_INFO_EXCHMARKET = ", SHSZ.DN,
                  "ORDER BY TRADE_DAYS ASC")
  wddb <- odbcConnect(dsn=server, uid=user, pwd=passwd)
  TRADE_DT <- sqlQuery(wddb, sqlStr, as.is=TRUE)
  close(wddb)
  r=0.04
  
  l<-as.numeric(strsplit(Period,"")[[1]][1])
  unit<-strsplit(Period,"")[[1]][2]
  
  #### 按月算对日 ####
  if(unit=="M")
  {
    en<- as.Date("20191209","%Y%m%d")
    st<- as.Date(Today,"%Y%m%d")
    ll<-seq.Date(en, st, by="-1 day")
    Calender<-rev(ll[ll > st & ll < en])
    future<-as.numeric(Today)+l*100
    y<-year(as.Date(Today,"%Y%m%d"))
    m<-as.numeric(substr(future,5,6))
    if((as.numeric(substr(future,5,6))-12)>0)
    {
      y<-year(st)+1
      m<-as.numeric(substr(future,5,6))-12
    }
    d<-as.numeric(substr(future,7,8))
    if(m==2)
    {
      d<-as.numeric(substr(future,7,8))
      if(d>28)
      {
        if(leap_year(y))
        {
          d=28
        }
      }
    }
    future<-paste(y,"-",m,"-",d,sep='')
    fd<-ymd(future)
    if(sum(which(Calender[]==fd))==0)
    {
      d=d-1
      fd<-paste(y,"-",m,"-",d,sep='')
      fd<-ymd(fd)
      if(sum(which(Calender[]==fd))==0)
      {
        d=d-1
        fd<-paste(y,"-",m,"-",d,sep='')
        fd<-ymd(fd)
        if(sum(which(Calender[]==fd))==0)
        {
          d=d-1
          fd<-paste(y,"-",m,"-",d,sep='')
          fd<-ymd(fd)
          if(sum(which(Calender[]==fd))==0)
          {
            d=d-1
            fd<-paste(y,"-",m,"-",d,sep='')
            fd<-ymd(fd)
          }
        }
      }
    }
    SettleDay<-gsub("-","",fd)
    if(sum(which(TRADE_DT[,1]==SettleDay))==0)
    {
      SettleDay<-TRADE_DT[(which(TRADE_DT[,1]>=SettleDay)[1]-1),1]
    } 
  }
  

  #### 按周算对日 ####
  if(unit=="W")
  {
    future<-as.Date(as.character(Today),"%Y%m%d")+weeks(l)
    if(sum(TRADE_DT[,1]==gsub("-","",future))!=0)
    {
      SettleDay<-gsub("-","",future)
    }
    
    if(sum(TRADE_DT[,1]==gsub("-","",future))==0)
    {
      SettleDay<-TRADE_DT[which(TRADE_DT[,1]>gsub("-","",future))[1],1]
    }
  }

  s=Volatility(Code)
  current_price<- as.numeric(get_current_price(Code))
  Strike=current_price*StrikePercent
  TimeLeft<-julian(as.Date(as.character(SettleDay),"%Y%m%d"),origin=as.Date(as.character(Today),"%Y%m%d"))[[1]]  
  d1<-(log(current_price/Strike)+(r+s^2/2)*((TimeLeft+0.01)/365))/(2*sqrt((TimeLeft+0.01)/365)) 
  delta<-pnorm(d1)
  Number<-ceiling(Asset*10000/current_price*delta/100)*100
  return(c(Code,Number,SettleDay,TimeLeft))
  
  
}

