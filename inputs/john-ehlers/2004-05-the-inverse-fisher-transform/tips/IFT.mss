Name: Inverse Fisher Transform of RSI:
Formula:
v1:= .1*(RSI(5)-50);
v2:= Mov(v1,9,W);
.5;
-.5;
(Exp(2*v2)-1)/(Exp(2*v2)+1)

Name: Cyber Cycles with Inverse Filter Transform
Formula:
pr:= (H+L)/2;
a:= 0.07;
sp:= (pr+(2*Ref(pr,-1))+(2*Ref(pr,-2))+Ref(pr,-3))/6;
cycle:=Power(1-(.5*a),2)*(sp-(2*Ref(sp,-1))+Ref(sp,-2))+(2*(1-a))*PREV-(Power(1-a,2)*Ref(PREV,-1));
.5;
-.5;
(Exp(2*cycle)-1)/(Exp(2*cycle)+1)

Name: Cyber Cycles
Formula:
pr:= (H+L)/2;
a:= 0.07;
sp:= (pr+(2*Ref(pr,-1))+(2*Ref(pr,-2))+Ref(pr,-3))/6;
Power(1-(.5*a),2)*(sp-(2*Ref(sp,-1))+Ref(sp,-2))+(2*(1-a))*PREV-(Power(1-a,2)*Ref(PREV,-1))

Name: Normalized RSI with IFT
Formula:
plot:= RSI(5);
ph:=LastValue(Highest(plot));
pl:=LastValue(Lowest(plot));
pf:=10/(ph-pl);
v1:= ((plot-pl)*pf)-5;
v2:= Mov(v1,9,W);
.5;
-.5;
(Exp(2*v2)-1)/(Exp(2*v2)+1)
