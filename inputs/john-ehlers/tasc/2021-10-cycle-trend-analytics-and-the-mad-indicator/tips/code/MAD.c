var MAD(vars Data, int ShortPeriod, int LongPeriod) 
{ 
	return 100*(SMA(Data,ShortPeriod)/SMA(Data,LongPeriod)-1.);
}


function run()
{
   MaxBars = 200;
   asset(""); // dummy asset
   ColorUp = ColorDn = 0; // don't plot a price curve
   
   vars Sine = series(genSine(30,30));
   var Diff = SMA(Sine,5) - SMA(Sine,20);
   plot("Sine",Sine[0]-0.5,LINE,BLUE);
   plot("MAD",Diff,LINE,RED);
}


void run()
{
  StartDate = 20191201;
  EndDate = 20210701;
  BarPeriod = 1440;

  assetAdd("SPY","STOOQ:*");
  asset("SPY");
  plot("MAD",MAD(seriesC(),8,23),NEW,RED); 
}
