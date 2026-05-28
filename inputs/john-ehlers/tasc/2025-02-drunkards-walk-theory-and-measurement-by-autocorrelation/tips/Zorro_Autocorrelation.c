void run() 
{
  BarPeriod = 1440;
  StartDate = 20231001;
  EndDate = 20240901;
  LookBack = 150;
  assetAdd("SPY","STOOQ:SPY.US");
  asset("SPY");
  int Lag, Length = 20;
  vars Prices = series(SmoothUltimate(seriesC(),Length));
  if(!is(LOOKBACK))
    for(Lag=1; Lag<100; Lag++) {
      int Row = dataRow(1,dataAppendRow(1,3));
      dataSet(1,Row,0,Correlation(Prices+Length,Prices+Length+Lag,Length));
      dataSet(1,Row,1,wdate());
      dataSet(1,Row,2,(var)Lag);
   }
if(is(EXITRUN))
  dataChart(1,0,CONTOUR,NULL);}
