var EO(vars Data,int Length)
{
  vars Derivs = series(priceClose(0)-priceClose(2));
  var RMS = sqrt(SumSq(Derivs,Length)/Length);
  var NDeriv = Derivs[0]/RMS;
  vars IFishs = series(FisherInv(&NDeriv));
  return Smooth(IFishs,20);
}


var HardClip(vars Data,int Length)
{
  vars Derivs = series(priceClose(0)-priceClose(2));
  var RMS = sqrt(SumSq(Derivs,Length)/Length);
  vars Clips = series(clamp(Derivs[0],-1,1));
  return FIR6(Clips);
}


void run()
{
  StartDate = 20200301;
  EndDate = 20210501;
  BarPeriod = 1440;

  assetAdd("SPY","STOOQ:*");
  asset("SPY");

  vars Signals = series(EO(seriesC(),50));
  var Threshold = 0.5;

  if(Signals[0] > Threshold && peak(Signals))
    enterShort();
  else if(Signals[0] < -Threshold && valley(Signals))
    enterLong();
}
