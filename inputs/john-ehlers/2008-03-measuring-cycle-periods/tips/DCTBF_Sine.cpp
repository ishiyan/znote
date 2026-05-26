//************************************************************************************
// DOMINANT CYCLE-TUNED BANDPASS FILTER RESPONSE - Sine
//************************************************************************************
DCTBF_API int DCTBF_Sine(Prices *pPrices, Values *pResults, int nTotDays, Values *pValue1) {
    double alpha1;
    int CurrentBar;
    double *Price;
    double *HP;
    double *SmoothHP;
    double delta;
    double beta;
    double gamma;
    double alpha;
    int N;
    double MaxAmpl;
    double Num;
    double Denom;
    double *DC;
    double DomCyc;
    double *Value1;
    double *Value2;
    double Q[51];
    double I[51];
    double Real[51];
    double Imag[51];
    double Ampl[51];
    double OldQ[51];
    double OldI[51];
    double OlderQ[51];
    double OlderI[51];
    double OldReal[51];
    double OldImag[51];
    double OlderReal[51];
    double OlderImag[51];
    double OldAmpl[51];
    double DB[51];
    Price = (double *) malloc(sizeof(double) * nTotDays);
    ZeroMemory(Price, sizeof(double) * nTotDays);
    HP = (double *) malloc(sizeof(double) * nTotDays);
    ZeroMemory(HP, sizeof(double) * nTotDays);
    SmoothHP = (double *) malloc(sizeof(double) * nTotDays);
    ZeroMemory(SmoothHP, sizeof(double) * nTotDays);
    DC = (double *) malloc(sizeof(double) * nTotDays);
    ZeroMemory(DC, sizeof(double) * nTotDays);
    Value1 = (double *) malloc(sizeof(double) * nTotDays);
    ZeroMemory(Value1, sizeof(double) * nTotDays);
    Value2 = (double *) malloc(sizeof(double) * nTotDays);
    ZeroMemory(Value2, sizeof(double) * nTotDays);
    for(CurrentBar=0; CurrentBar= 6)
            SmoothHP[CurrentBar] = (HP[CurrentBar] + 2*HP[CurrentBar-1] + 3*HP[CurrentBar-2]
                                   + 3*HP[CurrentBar-3] + 2*HP[CurrentBar-4] + HP[CurrentBar-5]) / 12;
        if(CurrentBar  5) {
            for(N=8; N MaxAmpl)
                MaxAmpl = Ampl[N];
        }
        for(N=8; N 0)
                DB[N] = -10*log(.01 / (1 - .99*Ampl[N] / MaxAmpl)) / log(10);
            if(DB[N] > 20)
                DB[N] = 20;
        }
        Num = 0;
        Denom = 0;
        for(N=10; N 9)
            DomCyc = Median(&DC[CurrentBar], 10);
        if(DomCyc < 8)
            DomCyc = 20;
        beta = cos(DegreesToRadians(360 / DomCyc));
        gamma = 1 / cos(DegreesToRadians(720*delta / DomCyc));
        alpha = gamma - sqrt(gamma*gamma - 1);
        if(CurrentBar<2) {
            pResults[CurrentBar].dValue = 0;
            pResults[CurrentBar].chIsValid = 0;
            continue;
        }
        Value1[CurrentBar] = .5*(1 - alpha)*(SmoothHP[CurrentBar] - SmoothHP[CurrentBar-1])
                              + beta*(1 + alpha)*Value1[CurrentBar-1] - alpha*Value1[CurrentBar-2];
        Value2[CurrentBar] = (DomCyc / 6.28)*(Value1[CurrentBar] - Value1[CurrentBar-1]);
        pResults[CurrentBar].dValue = Value1[CurrentBar];
        pResults[CurrentBar].chIsValid = 'Y';
    }
    free(Price);
    free(HP);
    free(SmoothHP);
    free(DC);
    free(Value1);
    free(Value2);
    return 0;
}