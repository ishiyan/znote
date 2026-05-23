void run() 
{
  BarPeriod = 1440;
  StartDate = 20230301;
  EndDate = 20240201;
  assetAdd("ES","YAHOO:ES=F");
  asset("ES");
  UltimateBands(20,1);
  plot("UltBands1",rRealUpperBand,BAND1,BLUE);
  plot("UltBands2",rRealLowerBand,BAND2,BLUE|TRANSP);
}
