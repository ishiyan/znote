var UltimateSmoother (var *Data, int Length)
{
  var f = (1.414*PI) / Length;
  var a1 = exp(-f);
  var c2 = 2*a1*cos(f);
  var c3 = -a1*a1;
  var c1 = (1+c2-c3)/4;
  vars US = series(*Data,4);
  return US[0] = (1-c1)*Data[0] + (2*c1-c2)*Data[1] - (c1+c3)*Data[2]
   + c2*US[1] + c3*US[2];
}
