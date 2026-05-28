var UltimateChannel(int Length,int STRLength,int NumSTRs)
{
  var TH = max(priceC(1),priceH());
  var TL = min(priceC(1),priceL());
  var STR = UltimateSmoother(series(TH-TL),STRLength);
  var Center = UltimateSmoother(seriesC(),Length);
  rRealUpperBand = Center + NumSTRs*STR;
  rRealLowerBand = Center - NumSTRs*STR;
  return Center; 
}
