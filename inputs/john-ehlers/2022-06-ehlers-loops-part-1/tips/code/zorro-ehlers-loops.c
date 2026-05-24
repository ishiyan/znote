var Roofing(var *Data,int HPeriod,int LPeriod)
{
  var f = 1.414*PI/HPeriod;
  var hpa1 = exp(-f);
  var hpc2 = 2*hpa1*cos(f/2);
  var hpc3 = -hpa1*hpa1;
  var hpc1 = (1 + hpc2 - hpc3) / 4;
  f = 1.414*PI/LPeriod;
  var ssa1 = exp(-f);
  var ssc2 = 2*ssa1*cos(f/2);
  var ssc3 = -ssa1*ssa1;
  var ssc1 = 1 - ssc2 - ssc3;
  
  vars HP = series(Data[0],3);
  HP[0] = hpc1*(Data[0] - 2*Data[1] + Data[2]) + hpc2*HP[1] + hpc3*HP[2];
  vars SS = series(HP[0],3);
  SS[0] = ssc1*(HP[0] + HP[1])/2 + ssc2*SS[1] + ssc3*SS[2];
  var Scaled = EMA(SS[0]*SS[0],.0242);
  return SS[0]/sqrt(Scaled);
}

function run()
{
  StartDate = ymd(wdate(NOW)-90); // 90 days before today
  BarPeriod = 1440; 
  asset("FDX");
  var PriceRMS = Roofing(seriesC(),125,20);
  var VolRMS = Roofing(series(marketVol()),125,20);

  if(is(LOOKBACK)) return;  // don't plot the lookback period
  plotGraph("Loop",VolRMS,PriceRMS,DOT|GRAPH,BLUE);
  plotGraph("Loops",VolRMS,PriceRMS,SPLINE|GRAPH,TRANSP|GREY);
  if(is(EXITRUN)) 
    plotGraph("Last",VolRMS,PriceRMS,SQUARE|GRAPH,RED);
}
