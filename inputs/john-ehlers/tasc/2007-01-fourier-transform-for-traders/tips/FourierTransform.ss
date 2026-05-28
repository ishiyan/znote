Here is what the code looks like:
//****************************************************************
// Transformed DFT
//****************************************************************
TRANSFORMEDDFT_API int TransformedDFT(Prices *pPrices, Values *pResults,
 int nTotDays, Values *pValue1, Values *pValue2) {
 double alpha1;
 double *HP;
 double *CleanedData;
 int Period;
 int n;
 double MaxPwr;
 double Num;
 double Denom;
 double DominantCycle;
 int CurrentBar;
 double *Price;
 int Window;
 // Arrays are sized to have a maximum Period of 50 bars
 double CosinePart[51];
 double SinePart[51];
 double Pwr[51];
 double DB[51];
 Window = (int) pValue2->dValue;
 if(Window < 8) Window = 8;
 if(Window > 50) Window = 50;
 Price = (double *) malloc(sizeof(double) * nTotDays);
 ZeroMemory(Price, sizeof(double) * nTotDays);
 HP = (double *) malloc(sizeof(double) * nTotDays);
 ZeroMemory(HP, sizeof(double) * nTotDays);
 CleanedData = (double *) malloc(sizeof(double) * nTotDays);
 ZeroMemory(CleanedData, sizeof(double) * nTotDays);
 for(CurrentBar=0; CurrentBar<nTotDays; CurrentBar++) {
  ZeroMemory(CosinePart, sizeof(CosinePart));
  ZeroMemory(SinePart, sizeof(SinePart));
  ZeroMemory(Pwr, sizeof(Pwr));
  ZeroMemory(DB, sizeof(DB));
  Price[CurrentBar] = pValue1[CurrentBar].dValue;
  // Get a detrended version of the data by High Pass Filtering with a 40 Period cutoff
  if(CurrentBar <= 5) {
   HP[CurrentBar] = Price[CurrentBar];
   CleanedData[CurrentBar] = Price[CurrentBar];
  }
  if(CurrentBar > 5) {
   alpha1 = (1 - sin(DegreesToRadians(360/40)))/cos(DegreesToRadians(360/40));
   HP[CurrentBar] = .5*(1+alpha1)*(Price[CurrentBar] - Price[CurrentBar-1])+alpha1*HP[CurrentBar-1];
   CleanedData[CurrentBar] = (HP[CurrentBar] + 2*HP[CurrentBar-1] + 3*HP[CurrentBar-2] +
    3*HP[CurrentBar-3] + 2*HP[CurrentBar-4] + HP[CurrentBar-5])/12;
  }
  // Continue if there isn't sufficient data
  if(CurrentBar-Window < 0) {
   pResults[CurrentBar].dValue = 0;
   pResults[CurrentBar].chIsValid = 0;
   continue;
  }
  // This is the DFT
  for(Period=8; Period<=50; Period++) {
   CosinePart[Period] = 0;
   SinePart[Period] = 0;
   for(n=0; n<=Window-1; n++) {
    CosinePart[Period] = CosinePart[Period] +
CleanedData[CurrentBar-n]*cos(DegreesToRadians(360*n/Period));
    SinePart[Period] = SinePart[Period] +
CleanedData[CurrentBar-n]*sin(DegreesToRadians(360*n/Period));
   }
   Pwr[Period] = CosinePart[Period]*CosinePart[Period] +
    SinePart[Period]*SinePart[Period];
  }
  // Find Maximum Power Level for Normalization
  MaxPwr = Pwr[8];
  for(Period=8; Period<=50; Period++) {
   if(Pwr[Period] > MaxPwr)
    MaxPwr = Pwr[Period];
  }
  // Normalize Power Levels and Convert to Decibels
  for(Period=8; Period<=50; Period++) {
   if(MaxPwr > 0 && Pwr[Period] > 0) {
    DB[Period] = -10*log(.01 / (1-.99*Pwr[Period]/MaxPwr))/log(10);
    if(DB[Period] > 20)
     DB[Period] = 20;
   }
  }
  // Find Dominant Cycle using CG algorithm
  Num=0;
  Denom=0;
  for(Period=8; Period<=50; Period++) {
   if(DB[Period] < 3) {
    Num = Num + Period*(3-DB[Period]);
    Denom = Denom + (3-DB[Period]);
   }
  }
  if(Denom != 0) {
   DominantCycle = Num/Denom;
   pResults[CurrentBar].dValue = DominantCycle;
  } else {
   pResults[CurrentBar].dValue = 0;
  }
  pResults[CurrentBar].chIsValid = 'Y';
 }
 free(Price);
 free(HP);
 free(CleanedData);
 return 0;
}
