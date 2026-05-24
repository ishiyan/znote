var indicator(vars Data,int Period,var Param);

var truncate(function Indicator,vars Data,int Period,var Param)
{
  indicator = Indicator;
  var *Trunc = zalloc(UnstablePeriod*sizeof(var));
  var Ret;
  int i;
  for(i = UnstablePeriod-1; i >= 0; i--) {
    SeriesBuffer = Trunc;
    Ret = indicator(Data+i,Period,Param);
    shift(Trunc,0,UnstablePeriod);
  }
  return Ret;
}

function run() 
{
   BarPeriod = 1440;
   StartDate = 20181101;

   assetAdd("SPY","STOOQ:SPY.US"); // load price history from Stooq
   asset("SPY");
   
  UnstablePeriod = 10;
  vars Prices = series(priceClose());
  var PB = BandPass(Prices, 20, 0.1);
  var Trunc = truncate(BandPass, Prices, 20, 0.1);
  plot("Bandpass",BP,NEW|LINE,RED);
  plot("Truncated",Trunc,LINE,BLUE);
}
