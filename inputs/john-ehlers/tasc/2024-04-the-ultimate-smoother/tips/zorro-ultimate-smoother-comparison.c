void run() 
{
  BarPeriod = 1440;
  StartDate = 20230201;
  EndDate = 20231201;
  assetAdd("ES","YAHOO:ES=F");
  asset("ES");
  int Length = 30;
  plot("UltSmooth", UltimateSmoother(seriesC(),Length),LINE,MAGENTA);
  plot("Smooth",Smooth(seriesC(),Length),LINE,RED);
  plot("EMA",EMA(seriesC(),3./Length),LINE,BLUE);
}