vars triangle(vars Data, int Length)
{
  vars Out = series(0,Length);
  int i;
  for(i=0; i<Length; i++)
    Out[i] = Data[i] * ifelse(i<Length/2,i+1,Length-i);
  return Out;
}

vars hamming(vars Data, int Length, var Pedestal)
{
  vars Out = series(0,Length);
  int i;
  for(i=0; i<Length; i++)
    Out[i] = Data[i] * sin(Pedestal+(PI-2*Pedestal)*(i+1)/(Length-1));
  return Out;
}

vars hann(vars Data, int Length)
{
  vars Out = series(0,Length);
  int i;
  for(i=0; i<Length; i++)
    Out[i] = Data[i] * (1-cos(2*PI*(i+1)/(Length+1)));
  return Out;
}

void run()
{
  StartDate = 20191101;
  EndDate = 20210101;
  BarPeriod = 1440;

  assetAdd("SPY","STOOQ:*"); // load data from STOOQ
  asset("SPY");

  vars Deriv = series(priceClose() - priceOpen());
  plot("FIR_SMA",SMA(Deriv,20),NEW,RED);
  plot("Triangle",SMA(triangle(Deriv,20),20),NEW,RED);
  plot("Hamming",SMA(hamming(Deriv,20,10*PI/360),20),NEW,RED);
  plot("Hann",SMA(hann(Deriv,20),20),NEW,RED);
}

var ROC_SMA(vars Data,int Length)
{ 
  vars Filt = series(SMA(Data,Length),2);
  return Length/(2*PI)*(Filt[0]-Filt[1]);
}