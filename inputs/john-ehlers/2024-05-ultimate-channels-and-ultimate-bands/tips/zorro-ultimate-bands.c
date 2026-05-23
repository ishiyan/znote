var UltimateBands(int Length,int NumSDs)
{
  var Center = UltimateSmoother(seriesC(),Length);
  vars Diffs = series(priceC()-Center);
  var SD = sqrt(SumSq(Diffs,Length)/Length);
  rRealUpperBand = Center + NumSDs*SD;
  rRealLowerBand = Center - NumSDs*SD;
  return Center; 
}
