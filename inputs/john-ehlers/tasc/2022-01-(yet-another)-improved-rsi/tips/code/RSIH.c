var RSIH(vars Data, int Length) {
   var CU = 0, CD = 0;
  int i;
  for(i=1; i<Length; i++) {
    var D = priceClose(i-1)-priceClose(i);
    var Hann = 1-cos(2*PI*i/(Length+1));
    if(D > 0) CU += Hann*D;
    else if(D < 0) CD -= Hann*D;
  }
  if(CU+CD != 0)
    return (CU-CD) / (CU+CD);
  else return 0;
}


void run() {
  StartDate = 20190901;
  EndDate = 20210701;
  BarPeriod = 1440;

  asset("SPY");
  plot("RSI",RSI(seriesC(),14),NEW|LINE,BLUE);
  plot("RSIH",RSIH(seriesC(),14),NEW|LINE,RED);
}
