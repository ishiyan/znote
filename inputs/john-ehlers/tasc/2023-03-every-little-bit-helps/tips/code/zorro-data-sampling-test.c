// TASC MAR 2023
// Every Little Bit Helps - RSI Comparison
// The Zorro Project
// Provided by: Petra Volkova

void run()
{
  BarPeriod = 15;
  StartDate = 20220629;
  EndDate = 20220712;
  asset("SPX500");

  vars OC = series((priceO()+priceC())/2);
  plot("RSI(Close)",RSI(seriesC(),14),NEW,RED);
  plot("RSI(OC)",RSI(OC,14),0,BLUE);
}
