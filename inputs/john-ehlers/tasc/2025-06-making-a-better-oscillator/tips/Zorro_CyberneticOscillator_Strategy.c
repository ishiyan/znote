function run()
{
  BarPeriod = 1440; 
  LookBack = 250; 
  StartDate = 2009; 
  EndDate = 2025;
  Fill = 2; // enter at next open
  assetList("AssetsIB"); // simulate IBKR
  asset("SPY");
  vars LP = series(Smooth(seriesC(),20));
  vars BP1 = series(HighPass3(LP,55));
  var ROC1 = BP1[0] - BP1[2];
  vars BP2 = series(HighPass3(LP,156));
  var ROC2 = BP2[0] - BP2[2];
  if(!NumOpenLong && ROC1 > 0 && ROC2 > 0)
    enterLong();
  if(NumOpenLong && (ROC1 < 0 || ROC2 < 0))
    exitLong();
}
