Name: Ehlers Filters
Formula:
ti:= 15;
pr:= MP();
coef:= Abs(pr - Ref(pr,-5));

Sum(coef*pr,ti)/Sum(coef,ti)

Name: Distant Coefficient Ehlers Filter
Formula:
ti:= 15;
pr:= MP();
coef:=Sum(Power(Ref(LastValue(pr+PREV-PREV)-pr,-1),2),ti);

Sum(coef*pr,ti)/Sum(coef,ti)