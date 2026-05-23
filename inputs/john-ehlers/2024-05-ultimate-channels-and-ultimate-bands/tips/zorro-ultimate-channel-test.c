void run() 
{
  BarPeriod = 1440;
  StartDate = 20230301;
  EndDate = 20240201;
  assetAdd("ES","YAHOO:ES=F");
  asset("ES");
  UltimateChannel(20,20,1);
  plot("UltChannel1",rRealUpperBand,BAND1,BLUE);
  plot("UltChannel2",rRealLowerBand,BAND2,BLUE|TRANSP); 
}
