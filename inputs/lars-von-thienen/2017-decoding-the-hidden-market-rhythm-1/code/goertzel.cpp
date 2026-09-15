// 
// Copyright (C) 2017 CC BY, www.whentotrade.com / Lars von Thienen
// Book: Decoding The Hidden Market Rhythm - Part 1 (2017)
// Chapter 3: Cycle Scanner Framework
// Link: https://www.amazon.com/dp/1974658244
//
// License: 
// This work is licensed under a Creative Commons Attribution 4.0 International License.
// You are free to share the material in any medium or format and remix, transform, and build upon the material for any purpose, 
// even commercially. You must give appropriate credit to the authors book and website, provide a link to the license, and indicate 
// if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. 
//

// Internal Goertzel DFT
void DFT(double *testdata, int data_length, float testcycle_length, double *amp2, double *phase2, double *minoffset)
{
    double real=0;
    double imag=0;
    double r1, i1;
    double SN, CN;
    double test_freq;

    double coeff;
    double Q0;
    double Q1;
    double Q2;
    double omega;
    double sine;
    double cosine;

    double temp;

    int i;

    // Convert wave length in frequency
    //F_TargetSweep = 1 / P_TargetSweep;
    test_freq = 1 / testcycle_length;

    // Calculate coefficients
    omega=2.0 * PI * test_freq;
    sine = sin(omega);
    cosine = cos(omega);
    coeff = (double)2.0 * cosine;

    // Value reset
    Q1 = 0;
    Q2 = 0;

    // Read all the supporting points
    for(i = 0 ; i < data_length ; i++)
    {
      //Q0 = coeff * Q1 - Q2 + Stuetzstelle[i];
      Q0 = coeff * Q1 - Q2 + testdata[i];
      Q2 = Q1;
      Q1 = Q0;
    }

    // Calc Real- and Imaginaer part 
    r1 = (Q1 - Q2 * cosine);
    i1 = (Q2 * sine);

    CN = cos((data_length-1)*omega);
    SN = sin((data_length-1)*omega);

    real=  r1*CN + i1*SN;
    imag = i1*CN - r1*SN;

    // Amplitude and phase from the real and the imaginary part
    //OLD: *amp2=sqrt((real * real) + (imag * imag));
    *amp2=((2.0*sqrt(real*real + imag*imag)) / data_length);
    //OLD:  *phase2=(double)(atan((double)imag/(double)real));
    *phase2=PI/2+atan2(imag,real);

    //Magnitude and amplitude from simplified calculation
    //*mag=Q1 * Q1 + Q2 * Q2 - Q1 * Q2 * coeff; // Magnitude Squared
    //*amp1=sqrt(*mag) * ((double)2 / (double)data_length);

    // Calculate the next data point that has the min.
    temp = *phase2 / (2 * PI);
    *minoffset  =  testcycle_length * ((( PI + (PI/(double)2)) / (2 * PI)) -  temp);//phase2);
}