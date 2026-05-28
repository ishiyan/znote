var HighPass3(vars Data,int Period)
{
  var a1 = exp(-1.414*PI / Period);
  var c2 = 2*a1*cos(1.414*PI/2 / Period);
  var c3 = -a1*a1;
  var c1 = (1.+c2-c3) / 4;
  vars HP = series(0,3);
  return HP[0] = c1*(Data[0]-2*Data[1]+Data[2])
    + c2*HP[1] + c3*HP[2];
}

var UltimateOsc(vars Data,int Edge,int Width)
{
  vars Signals = series(HighPass3(Data,Width*Edge)-HighPass3(Data,Edge));
  var RMS = sqrt(SumSq(Signals,100)/100);
  return Signals[0]/fix0(RMS);
}

void run() 
{
  BarPeriod = 1440;
  StartDate = 20240101;
  EndDate = 20241231;
  asset("SPX500");
  plot("UltOsc", UltimateOsc(seriesC(),20,2),LINE,RED);
}
