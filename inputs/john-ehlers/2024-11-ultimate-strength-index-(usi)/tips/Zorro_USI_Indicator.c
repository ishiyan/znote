var UltimateStrength (int Length)
{
  vars SU = series(max(0,priceC(0) - priceC(1)));
  var USU = UltimateSmooth(series(SMA(SU,4)),Length);
  vars SD = series(max(0,priceC(1) - priceC(0)));
  var USD = UltimateSmooth(series(SMA(SD,4)),Length);
  return (USU-USD)/fix0(USU+USD);
}
