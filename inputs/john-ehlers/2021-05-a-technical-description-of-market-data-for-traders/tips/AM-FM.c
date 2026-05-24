var AM(var Signal, int Period)
{
  var Envelope = MaxVal(series(abs(Signal)),4);
  return SMA(series(Envelope),Period); 
}

var FM(var Signal, int Period)
{
  var HL = clamp(10*Signal,-1,1);
  return Smooth(series(HL),Period);
}

void run() 
{
   BarPeriod = 1440;
   StartDate = 20180701;
   EndDate = 20201201;

   assetAdd("SPY","STOOQ:*"); // load price history from Stooq
   asset("SPY");

   var Deriv = priceClose()-priceOpen();
   plot("Deriv",Deriv,NEW,BLACK);
   plot("AM",AM(Deriv,8),NEW,RED);
   plot("FM",FM(Deriv,30),NEW,BLUE);
}
