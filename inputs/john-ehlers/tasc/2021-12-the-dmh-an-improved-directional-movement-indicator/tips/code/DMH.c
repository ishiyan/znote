vars hann(vars Data,int Length)
{
   vars Out = series(0,Length);
   int i;
  for(i=0; i<Length; i++)
    Out[i] = Data[i] * (1-cos(2*PI*(i+1)/(Length+1)));
  return Out;
}
var DMH(int Length)
{
  var SF = 1./Length;
  vars EMAs = series(0,Length);
  EMAs[0] = SF*(PlusDM(1)-MinusDM(1))+(1.-SF)*EMAs[1];
  return Sum(hann(EMAs,Length),Length);
}
void run()
{
  StartDate = 20190901; 
  EndDate = 20210701;
  BarPeriod = 1440; 
  
  asset("SPY");
  plot("DMH",DMH(14),NEW|LINE,RED);
}
