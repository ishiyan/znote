void run() 
{
  BarPeriod = 1440;
  LookBack = 250;
  StartDate = 20240301;
  EndDate = 20250407;
  asset("SPX500");
  plot("CyberOsc1",CyberOsc(seriesC(),30,20),NEW|LINE,RED);
  plot("CyberOsc2",CyberOsc(seriesC(),250,20),NEW|LINE,BLUE);
}
