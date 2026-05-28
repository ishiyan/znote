Name:  FRAMA
Formula:
y:=Input("sample time periods",1,20,8);
y2:=2*y;
n1:=(HHV(H,y)-LLV(L,y))/y;
n2:=Ref((HHV(H,y)-LLV(L,y))/y,-y);
n3:=(HHV(H,y2)-LLV(L,y2))/y2;
x:=(Log(n1+n2)-Log(n3))/Log(2);
xt:=Exp(-4.6*(x-1));
x1:=If(xt<0.1,0.1,If(xt>1,1,xt));
x2:=1-x1;
If(Cum(1)=y2,
(MP() * x1) + (Ref(MP(),-1) * x2),
(MP() * x1) + (PREV * x2))