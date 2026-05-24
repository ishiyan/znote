void run() 
{
   set(PARAMETERS,PLOTNOW);
   BarPeriod = 1440;
   LookBack = 40;
   NumYears = 8;
   assetAdd("SPY","STOOQ:SPY.US"); // load price history from Stooq
   asset("SPY");
   NumWFOCycles = 4;
   int Cutoff = optimize(10,4,20,2);
   vars Prices = series(priceClose());
   vars Signals = series(LowPass(Prices, Cutoff));
   if(valley(Signals))
      enterLong();
   else if(peak(Signals))
      enterShort();
}
