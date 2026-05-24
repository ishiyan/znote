var var MyRSI(vars Data,int Period)
{
  var CU = SumUp(Data,Period+1);
  var CD = -SumDn(Data,Period+1);
  return ifelse(CU+CD != 0,(CU-CD)/(CU+CD),0);
}

var NET(vars Data,int Period)
{
  int i,k;
  var Num = 0;
  for(i=1; i<Period; i++)
    for(k=0; k<i; k++)
        Num -= sign(Data[i]-Data[k]);
  var Denom = .5*Period*(Period-1);
  return Num/Denom;
}
