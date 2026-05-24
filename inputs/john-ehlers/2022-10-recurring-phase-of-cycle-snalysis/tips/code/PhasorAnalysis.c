// TASC November 2022
// Recurring Phase Of Cycle Analysis
// Phasor Analysis - Zorro/Lite-C implementation
// (C) 2013-2022 John F. Ehlers
// Converted by Petra Volkova, The Zorro Project

var Angle, State, DerivedPeriod;

var phasor(vars Signals,int Period)
{
//Correlate with Cosine wave having a fixed period
  var Sx = 0, Sy = 0, Sxx = 0, Sxy = 0, Syy = 0;
  int count;
  for(count = 1; count <= Period; count++) {
    var X = Signals[count - 1];
    var Y = cos(2*PI*(count - 1) / Period);
    Sx += X; Sy += Y;
    Sxx += X*X; Sxy += X*Y; Syy += Y*Y;
  }
  var Real = 0, Imag = 0;
  if((Period*Sxx - Sx*Sx > 0) && (Period*Syy - Sy*Sy > 0))
    Real = (Period*Sxy - Sx*Sy) / sqrt((Period*Sxx - Sx*Sx)*(Period*Syy - Sy*Sy));
//Correlate with a Negative Sine wave having a fixed period
  Sx = Sy = Sxx = Sxy = Syy = 0;
  for(count = 1; count <= Period; count++) {
    var X = Signals[count - 1];
    var Y = -sin(2*PI*(count - 1) / Period);
    Sx += X; Sy += Y;
    Sxx += X*X; Sxy += X*Y; Syy += Y*Y;
  }
  if((Period*Sxx - Sx*Sx > 0) && (Period*Syy - Sy*Sy > 0))
    Imag = (Period*Sxy - Sx*Sy) / sqrt((Period*Sxx - Sx*Sx)*(Period*Syy - Sy*Sy));
//Compute the angle as an arctangent function and resolve ambiguity
  Angle = 0;
  if(Real != 0) Angle = 90 - 180/PI*atan(Imag/Real);
  if(Real < 0) Angle -= 180;
//compensate for angle wraparound
  vars Angles = series(Angle,2);
  if(abs(Angles[1]) - abs(Angle - 360) < Angle - Angles[1] && Angle > 90 && Angles[1] < -90)
    Angle -= 360;
//angle cannot go backwards
  if(Angle < Angles[1] && ((Angle > -135 && Angles[1] < 135) || (Angle < -90 && Angles[1] < -9)))
    Angle = Angles[1];
  Angles[0] = Angle;
//Frequency derived from rate-change of phase
  DerivedPeriod = 0;
  vars DeltaAngles = series(Angle - Angles[1],2);
  if(DeltaAngles[0] <= 0) DeltaAngles[0] = DeltaAngles[1];
  if(DeltaAngles[0] != 0) DerivedPeriod = 360 / DeltaAngles[0];
  if(DerivedPeriod > 60) DerivedPeriod = 60;
//Trend State Variable
  State = 0;
  if(Angle - Angles[1] <= 6) {
    if(Angle >= 90 || Angle <= -90) State = 1;
    if(Angle > -90 && Angle < 90) State = -1;
  }
  return Angle;
}

void run() 
{
  set(PLOTNOW,LOGFILE);
  BarPeriod = 1440;
  StartDate = 20210401;
  EndDate = 20220701;
  assetAdd("RTX","YAHOO:RTX");
  asset("RTX");
  phasor(seriesC(),28);
  plot("Phase",Angle,NEW,RED);
  plot("DerivedPeriod",DerivedPeriod,NEW,RED);
  plot("State",State,NEW,RED);
}
