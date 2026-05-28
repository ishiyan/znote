function run() 
{
   set(PARAMETERS,PLOTNOW);
   BarPeriod = 1440;
   LookBack = 40;
   NumYears = 8;
   assetAdd("SPY","STOOQ:SPY.US"); // load price history from Stooq
   asset("SPY");
   NumWFOCycles = 4;
   int Cutoff = optimize(10,5,30,5);
   int Period = optimize(14,10,25,1);
   var Threshold = optimize(9,5,15,1);
   vars Prices = series(priceClose());
   var State = CCYState(Prices, Period, Threshold);
   plot("State", State, NEW|LINE, BLUE);
   vars Signals = series(LowPass(Prices, Cutoff));
   if(State != 0) {
      if(valley(Signals))
         enterLong();
      else if(peak(Signals))
         enterShort();
   } else {
      exitLong(); 
      exitShort();
   }
}
