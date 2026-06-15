var MinCorr, Filt;
var AutoTune(vars Data,int Window)
{
	Filt = HighPass3(Data,Window);
	vars HP = series(Filt);
	var Corr[256];
	int Lag, J;

	for(Lag = 1; Lag <= Window; Lag++)
	{
		var Sx = 0., Sy = 0.;
		var Sxx = 0., Sxy = 0., Syy = 0.;

		for(J = 0; J < Window; J++)
		{
			var X = HP[J];
			var Y = HP[Lag + J];
			Sx  += X; Sy  += Y;
			Sxx += X*X; Sxy += X*Y; Syy += Y*Y;
		}

		var Den1 = Window*Sxx - Sx*Sx;
		var Den2 = Window*Syy - Sy*Sy;

		if(Den1 > 0. && Den2 > 0.)
			Corr[Lag] = (Window*Sxy - Sx*Sy) / sqrt(Den1*Den2);
		else
			Corr[Lag] = 0.;
	}

	MinCorr = 1.;
	var DC = Window;

	for(Lag = 1; Lag <= Window; Lag++)
		if(Corr[Lag] < MinCorr) {
			MinCorr = Corr[Lag];
			DC = 2*Lag;
		}

	vars DCs = series(DC,2);
	return DCs[0] = clamp(DC,DCs[1]-2.,DCs[1]+2.);
}

var BandPass2(vars Data, int Period, var Bandwidth)
{
	var L1 = cos(2.*PI/Period);
	var G1 = cos(Bandwidth*2.*PI/Period);
	var S1 = 1./G1 - sqrt(1./(G1*G1) - 1.);
	vars BP = series(0,3);
	return BP[0] = 0.5*(1.-S1)*(Data[0]-Data[2])
		      + L1*(1.+S1)*BP[1] - S1*BP[2];
}

function run()
{
	BarPeriod = 1440;
	StartDate = 2024;
	EndDate = 2025;
	asset("ES");

	var DC = AutoTune(seriesC(),20);
	var BP = BandPass2(seriesC(),DC,0.25);
	plot("Zero",0,NEW,BLACK);
	plot("BP",BP,LINE,BLUE);
}

function run()
{
	BarPeriod = 1440;
	StartDate = 2010;
	EndDate = 2025;
	Capital = 100000;
	asset("ES");

	set(TESTNOW,PARAMETERS);
	NumWFOCycles = 10;
	int Window = optimize("Window",26,10,30,2);
	var BW = optimize("BW",0.22,0.10,0.30,0.01);
	var Thresh = -optimize("Thresh",0.22,0.1,0.3,0.01);

	var DC = AutoTune(seriesC(),Window);
	var BP = BandPass2(seriesC(),DC,BW);
	vars ROCs = series(BP-ref(BP,2));

	Lots = 0.5*(Capital+sqrt(1.+ProfitTotal/Capital))/MarginCost;
	MaxLong = MaxShort = 1;
	if(crossOver(ROCs,0) && MinCorr < Thresh)
		enterLong();
	if(crossUnder(ROCs,0) && MinCorr < Thresh && Filt > 0)
		enterShort();
}