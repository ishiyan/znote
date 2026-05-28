var PMA(vars Data,int Length)
{
  var Sx = 0, Sy = 0, Sxx = 0, Syy = 0, Sxy = 0;
  int i;
  for(i=1; i<=Length; i++) {
    Sx += i;
    Sy += Data[i-1];
    Sxx += i*i;
    Syy += Data[i-1]*Data[i-1];
    Sxy += i*Data[i-1];
  }
  var Slope = -(Length*Sxy - Sx*Sy) / (Length*Sxx - Sx*Sx);
  return Sy/Length + Slope*Length/2;
}

void run() 
{
  BarPeriod = 1440;
  StartDate = 20231001;
  EndDate = 20241001;
  LookBack = 30;
  assetAdd("SPX","STOOQ:^SPX");
  asset("SPX");
  plot("PMA",PMA(seriesC(),LookBack),LINE,BLUE);
  plot("SMA",SMA(seriesC(),LookBack),LINE,RED);
}
