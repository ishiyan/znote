var CyberOsc(vars Data,int HPLength,int LPLength)
{
  vars HP = series(HighPass3(Data,HPLength));
  vars LP = series(Smooth(HP,LPLength));
  var RMS = sqrt(SumSq(LP,100)/100);
  return LP[0]/fix0(RMS);
}
