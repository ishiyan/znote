var void simple()
{
  int SigPeriod = optimize(8,6,14,1),
  ROCPeriod = optimize(1,1,6,1);
//Derivative of the price wave
  vars Deriv = series(priceClose(0)-priceClose(2));
//zeros at Nyquist and 2*Nyquist, i.e. Z3 = (1 + Z^-1)*(1 + Z^-2)
  vars Z3 = series(Sum(Deriv,4));
//Smooth Z3 for trading signal
  vars Signal = series(SMA(Z3,SigPeriod));
//Use Rate of Change to identify entry point
  vars Roc = series(Signal[0]-Signal[ROCPeriod]);
//If ROC Crosses Over 0 Then Buy Next Bar on Open;
//If Signal Crosses Under 0 Then Sell Next Bar on Open;
  if(crossOver(Roc,0))
    enterLong();
  else if(crossUnder(Signal,0))
  exitLong();
}

void simpleFM()
{
  int i, SigPeriod = optimize(8,6,14,1),
  ROCPeriod = optimize(1,1,6,1);
//Derivative of the price wave
  vars Deriv = series(priceClose(0)-priceClose(2));
//Normalize Degap to half RMS and hard limit at +/- 1
  var RMS = 0;
  for(i=0; i<50; i++) RMS += Deriv[i]*Deriv[i];
  vars Clip = series(clamp(2*Deriv[0]/sqrt(RMS/50),-1,1));
//zeros at Nyquist and 2*Nyquist, i.e. Z3 = (1 + Z^-1)*(1 + Z^-2)
  vars Z3 = series(Sum(Clip,4));
//Smooth Z3 for trading signal
  vars Signal = series(SMA(Z3,SigPeriod));
//Use Rate of Change to identify entry point
  vars Roc = series(Signal[0]-Signal[ROCPeriod]);
//If ROC Crosses Over 0 Then Buy Next Bar on Open;
//If Signal Crosses Under 0 Then Sell Next Bar on Open;
  if(crossOver(Roc,0))
    enterLong();
  else if(crossUnder(Signal,0))
    exitLong();
}
