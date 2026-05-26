InvFishStd(series)={
 MyVal1 = .1 * (rsi($1.close,5)-50)
 MyVal2 = wavg(MyVal1, 9)
 InvFish = (Exp(2*MyVal2)-1) / (Exp(2*MyVal2) + 1)
InvFish
}

CyberCycl(series, alpha=.07)={
 Cycle = 0
 Smooth = ($1.midpt + 2*$1.midpt[1] + 2*$1.midpt[2] + $1.midpt[3])/6
 Cycle=((1-0.5*alpha)^2)*(Smooth-2*Smooth[1]+Smooth[2])+2*(1-alpha)*Cycle[1]-((1-alpha)^2)*Cycle[2]
 if barcount($1) < 7 then Cycle = ($1.midpt - 2*$1.midpt[1] + $1.midpt[2])/4
 ICycle = (exp(2*Cycle)-1) / (exp(2*Cycle)+1)
ICycle
}
