var correlY(var Phase); // function pointer
var cosFunc(var Phase) { return cos(2*PI*Phase); }
var sinFunc(var Phase) { return -sin(2*PI*Phase); }

var correl(vars Data, int Length, function Func)
{
   correlY = Func; 
   var Sx = 0, Sy = 0, Sxx = 0, Sxy = 0, Syy = 0;
   int count;
   for(count = 0; count < Length; count++) {
      var X = Data[count];
      var Y = correlY((var)count/Length);
      Sx += X; Sy += Y;
      Sxx += X*X; Sxy += X*Y; Syy += Y*Y;
   }
   if(Length*Sxx-Sx*Sx > 0 && Length*Syy-Sy*Sy > 0)
      return (Length*Sxy-Sx*Sy)/sqrt((Length*Sxx-Sx*Sx)*(Length*Syy-Sy*Sy));
   else return 0;
}

var CCY(vars Data, int Length) { return correl(Data,Length,cosFunc); }

var CCYROC(vars Data, int Length) { return correl(Data,Length,sinFunc); }

var CCYState(vars Data, int Length, var Threshold)
{
   vars Angles = series(0,2);
   var Real = correl(Data,Length,cosFunc);
   var Imag = correl(Data,Length,sinFunc);
//Compute the angle as an arctangent function and resolve ambiguity
   if(Imag != 0) Angles[0] = 90 + 180/PI*atan(Real/Imag);
   if(Imag > 0) Angles[0] -= 180;
//Do not allow the rate change of angle to go negative
   if(Angles[1]-Angles[0] < 270 && Angles[0] < Angles[1])
      Angles[0] = Angles[1];
//Compute market state
   if(abs(Angles[0]-Angles[1]) < Threshold)
      return ifelse(Angles[0] < 0,-1,1);
   else return 0;
}
