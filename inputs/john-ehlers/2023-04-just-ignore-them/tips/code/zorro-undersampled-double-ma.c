// TASC APR 2023
// Hann Filter and Undersampled Double MA
// The Zorro Project
// Provided by: Petra Volkova

var Hann(vars Data,int Length)
{
  var Filt = 0, Coeff = 0;
  int i;
  for(i=1; i<=Length; i++) {
    Filt += (1-cos(2*PI*i/(Length+1)))*Data[i-1];
    Coeff += 1-cos(2*PI*i/(Length+1));
  }
  return Filt/fix0(Coeff);
}

void run() 
{
  StartDate = 20220101;
  EndDate = 20221231;
  BarPeriod = 1440;

  set(PLOTNOW);
  asset("SPY");

  vars Samples = series();
  if(Init || Bar%5 == 0)
    Samples[0] = priceC(0);
  else
    Samples[0] = Samples[1];

  plot("Hann6",Hann(Samples,6),LINE,MAGENTA);
  plot("Hann12",Hann(Samples,12),LINE,BLUE);
  plot("Hann",Hann(seriesC(),12),0,DARKGREEN);
}
