var CTI (vars Data, int Length)
{
  int count;
  var Sx = 0, Sy = 0, Sxx = 0, Sxy = 0, Syy = 0;
  for(count = 0; count < Length; count++) {
    var X = Data[count];
    var Y = -count;
    Sx = Sx + X;
    Sy = Sy + Y;
    Sxx = Sxx + X*X;
    Sxy = Sxy + X*Y;
    Syy = Syy + Y*Y;
  }
  if(Length*Sxx - Sx*Sx > 0 && Length*Syy - Sy*Sy > 0)
     return (Length*Sxy - Sx*Sy) / sqrt((Length*Sxx - Sx*Sx)*(Length*Syy - Sy*Sy));
   else return 0;
}

void run() 
{
   BarPeriod = 1440;
   LookBack = 40;
   StartDate = 2010;
   assetAdd("SPY","STOOQ:SPY.US"); // load SPY history from Stooq
   asset("SPY");

   vars Prices = series(priceClose());
   vars Signals = series(CTI(Prices,20));
   if(crossOver(Signals,0))
      plotPriceProfile(40,0); // plot positive price difference
   else if(crossUnder(Signals,0))
      plotPriceProfile(40,2); // plot negative price difference
}
