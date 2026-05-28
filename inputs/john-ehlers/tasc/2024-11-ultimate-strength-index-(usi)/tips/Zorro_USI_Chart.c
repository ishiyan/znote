void run() 
{
  BarPeriod = 1440;
  StartDate = 20230801;
  EndDate = 20240801;
  assetAdd("SPX","STOOQ:^SPX");
  asset("SPX");
  plot("USI(112)",UltimateStrength(112),NEW|LINE,BLUE);
  plot("USI(28)",UltimateStrength(28),NEW|LINE,BLUE);
}
