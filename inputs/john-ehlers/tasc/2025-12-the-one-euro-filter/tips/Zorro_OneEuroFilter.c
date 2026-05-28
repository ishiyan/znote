var OneEurFilter(vars Data, int PeriodMin, var Factor)
{
  vars SmoothedDX = series(Data[0],2), Smoothed = series(Data[0],2);
  var Alpha = 2*PI/(4*PI + 10);
//EMA the Delta Price
  SmoothedDX[0] = Alpha*(Data[0]-Data[1]) + (1.-Alpha)*SmoothedDX[1];
//Adjust cutoff period based on a fraction of the rate of change
  var Cutoff = PeriodMin + Factor*abs(SmoothedDX[0]);
//Compute adaptive alpha
  Alpha = 2*PI/(4*PI + Cutoff);
//Adaptive smoothing
  return Smoothed[0] = Alpha*Data[0] + (1.-Alpha)*Smoothed[1];
}
