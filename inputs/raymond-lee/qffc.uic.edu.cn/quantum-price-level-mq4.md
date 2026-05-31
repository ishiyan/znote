# Quantum Price Level Calculation (mq4 version)

- **Source:** <https://qffc.uic.edu.cn/home/content/index/pid/277/cid/6842.html>

---


## Quantum Price Level Calculation (mq4 version)


This tutorial shows how to calculate the Quantum Price Level(qpl) under MetaTrader4 platform step by step.


#### Objective   : This program calculate the N(QPR) of 8 Financial Products.


For Each Financial Product:


0) Cacluate All K values [K0 .. K20] using the following formula:

K[eL] = pow((1.1924 + 33.2383*eL + 56.2169*eL*eL)/(1 + 43.6106 *eL),p3);

1) Read the Daily Time Series and extract (Date, O, H, L, C, V) m

2) Calculate Dally Price Return r(t)

3) Calculate quantum price return wavefunction Q(r)(size 100)

4) Evalutate lambda (L) value for the wavefunction Q(r)using F.D.M. at ground state

L = abs((r0^2*Q0 - r1^2*Q1)/(r0^4*Q0 - r1^4*Q1))

5) Evaluate other related parameters: 

- sigma  (std dev of Q)

- maxQPR (max Quantum Price Return - for normalization) 

6) Once L is found, using Quartic Schrodinger Equation of Quantum Finance to find  all the 21 Quantum Price Energies (QFEL0 .. QFEL20). 

Given by:

(E(n)/(2n+1))^3 - (E(n)/(2n+1)) - K(n)^3 * L = 0

where  K(n) = ((1.1924+33.2383n+56.2169n^2)/(1+43.6106n))^(1/3)

7) Solve the 21 Cubic Eqts in (6) and extract the +ve real roots as QFEL0 .. QFEL20.

8) Cacluate QPR(n)  = QFEL(n)/QFEL(0) n = [1 .. 20]

9) Cacluate NQPR(n) = 1 + 0.21*sigma*QPR(n);

10)Save TWO Level of datafiles

1) For each financial product, save the QPL Table contains

QFEL, QPR, NQPR for the first 21 energy levels

2) For all financial product, create a QPL Summary table contains NQPR for all FP


#### Expert initialization function.


```mql4
string      QP_Directory   = "Indicators";       // data Directory

string      Prediction_Directory = "Prediction";//prediction directory

string  TP_Code[8]={ "AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCHF", "EURAUD","GBPJPY", "USDJPY"};

int maxTP = 8; // the num of product

int maxTS = 2048;//1024; //max no of Time Series Record // change to 2048

double all_NQPL[8][21]; 

string Predicted_value[8];

int read_data(string TPSymbol, double &return_array[]){

//declaration varuables

//basic data

int        DT_YY[2048];

int        DT_MM[2048];

int        DT_DD[2048];

double     DT_OP[2048];

double     DT_HI[2048];

double     DT_LO[2048];

double     DT_CL[2048];

double     DT_VL[2048];

double     DT_RT[2048];

double     DT_EL[2048];

double     DT_MA[2048];

double     DT_RSI[2048];

double     DT_MACDM[2048];

double     DT_MACDS[2048];

double     mu = 0;

double     sigma = 0;

double     dr = 0;

double     Q[100];//wave function

double     NQ[100];//normalized wave function

double     r[100]; //return rate under normal distribution

double     K[21];

double     QFEL[21];

double     QPR[21];

double     NQPR[21];

//define the destination add

string Data_FileName = "Daily_"+TPSymbol+".csv";

FileDelete(QP_Directory+"//"+Data_FileName,FILE_COMMON);

ResetLastError();

int QPD_FileHandle    = FileOpen(QP_Directory+"//"+Data_FileName,FILE_COMMON|FILE_READ|FILE_WRITE|FILE_CSV,',');

// Write Header Line

FileWrite(QPD_FileHandle,"Year","Month","Day","Open","High","Low","Close","Volumn","Return","MA","RSI","MACDM",

"MACDS","QPL1","QPL2","QPL3","QPL4","QPL5","QPL6","QPL7","QPL8","QPL9","QPL10","QPL11","0",

"QPL-1","QPL-2","QPL-3","QPL-4","QPL-5","QPL-6","QPL-7","QPL-8","QPL-9","QPL-10","QPL-11");

//check TSsize we can retrive

Print("product ",TPSymbol);
```


#### 1. READ ALL Daily Time Series


```mql4
int TSsize = 0;

while (iTime(TPSymbol,PERIOD_D1,TSsize)>0 && (TSsize
{

TSsize++;

}

if(TSsize == 0) {

Print("no data for ",TPSymbol);

return -1;//no data for this product

}

for (int d=1;d
{

DT_YY[d-1] = TimeYear(iTime(TPSymbol,PERIOD_D1,d)); 

DT_MM[d-1] = TimeMonth(iTime(TPSymbol,PERIOD_D1,d)); 

DT_DD[d-1] = TimeDay(iTime(TPSymbol,PERIOD_D1,d)); 

DT_OP[d-1] = iOpen(TPSymbol,PERIOD_D1,d);

DT_HI[d-1] = iHigh(TPSymbol,PERIOD_D1,d);

DT_LO[d-1] = iLow(TPSymbol,PERIOD_D1,d);

DT_CL[d-1] = iClose(TPSymbol,PERIOD_D1,d);

DT_VL[d-1] = iVolume(TPSymbol,PERIOD_D1,d);

DT_MA[d-1] = iMA(TPSymbol,PERIOD_D1,13,8,MODE_SMA,PRICE_MEDIAN,d);

DT_RSI[d-1]= iRSI(TPSymbol,PERIOD_D1,14,PRICE_CLOSE,d);

DT_MACDM[d-1] = iMACD(TPSymbol,PERIOD_D1,12,26,9,PRICE_CLOSE,MODE_MAIN,d);

DT_MACDS[d-1] = iMACD(TPSymbol,PERIOD_D1,12,26,9,PRICE_CLOSE,MODE_SIGNAL,d);

//get price return

if(d >=2 && DT_CL[d-1] >0){

DT_RT[d-1] = DT_CL[d-1]/DT_CL[d-2] ; 

}else{

DT_RT[d-1] = 1; 

}

//calculate mu 

mu = mu+DT_RT[d-1];

}
```


#### 2. Calculate Mean (mu) and Standard Deviation (sigma) of return array


```mql4
mu = mu/TSsize;

// Calculate STDEV sigma

for (int d=0;d
{

sigma = sigma + (DT_RT[d]-mu)*(DT_RT[d]-mu);

}

sigma = sqrt((sigma / TSsize)); 

// Calculate dr where dr = 3*sigma/50

dr = 3 * sigma / 50;
```


#### 3. Generate the QP Wavefunction distribution


```mql4
//transform into wave function

int tQno = 0;

double zero_index = 1 - 50*dr;

for(int d=0; d< TSsize; d++) //travers the DT_RT

{

//retrive the index of Q(r) with the value of DT_RT[d] 

int index = int((DT_RT[d]-zero_index)/dr);

//in the position of index accumulate the index

if(index <0 || index>99)

{

continue;

}

Q[index] += 1;

tQno += 1;

} 

double auxR = 1 - (dr * 50);

for (int nQ=0;nQ<100;nQ++)

{

r[nQ]  = auxR;

NQ[nQ] = Q[nQ]/tQno; 

auxR = auxR + dr;

} 

//find maxQ and maxQno

double maxQ   = 0;

int maxQno = 0;

for (int nQ=0;nQ<100;nQ++)

{

if (NQ[nQ] > maxQ)

{

maxQ   = NQ[nQ];

maxQno = nQ; 

} 

}
```


#### 4. Evaluate Lambda L for the QP Wavefuntion


Given maxQno - i.e. ground state Q[0], r[0] = r[maxQno-dr]

We have Q[+1] = NQ[maxQno+1], r[+1] = r[maxQno]+(dr/2)

Q[-1] = NQ[maxQno-1], r[-1] = r[maxQno]-(dr*1.5)

Apply F.D.M. into QP Sch Eqtuation

L = abs((r[-1]^2*Q[-1]-(r[+1]^2*Q[+1]))/(r[-1]^4*Q[-1]-(r[+1]^4*Q[+1])))


```mql4
//find K

for (int eL=0;eL<21;eL++)

{

K[eL] = MathPow((1.1924 + (33.2383*eL) + (56.2169*eL*eL))/(1 + (43.6106 *eL)),(1.0/3.0));

}

//find lambda

double r0  = r[maxQno] - (dr/2);

double r1  = r0 + dr;

double rn1 = r0 - dr;

double Lup = (pow(rn1,2)*NQ[maxQno-1])-(pow(r1,2)*NQ[maxQno+1]);

double Ldw = (pow(rn1,4)*NQ[maxQno-1])-(pow(r1,4)*NQ[maxQno+1]);

double L   = MathAbs(Lup/Ldw);
```


#### 5. Using QP Schrodinger Eqt to FIND first 21 Energy Levels


By solving the Quartic Anharmonic Oscillator as cubic polynomial eqt

of the form



a*x^3 + b*x^2 + c*x + d = 0



Using (Dasqupta et. al. 2007) QAHO solving equation:



(E(n)/(2n+1))^3 - (E(n)/(2n+1)) - K(n)^3*L = 0



Solving the above Depressed Cubic Eqt using Cardano's Method



Given    t^3 + p*t + q = 0

Let      t = u + v

Cardano's Method deduced that:

u^3 = -q/2 + sqrt(q^2/4 + p^3/27)

v^3 = -q/2 - sqrt(q^2/4 + p^3/27)

The first cubic root (real root) will be:



t = u + v 



So, combining Cardano's Method into our QF Sch Eqt. 

We have

Substitue p = -(2n+1)^2;  q = -L(2n+1)^3*(K(n)^3) into the above equations to get the  real root


```mql4
//calculate QFEL by using L, K

for (int eL=0;eL<21;eL++)

{

double p = -1 * pow((2*eL+1),2);

double q = -1 * L * pow((2*eL+1),3) * pow(K[eL],3);

// Apply Cardano's Method to find the real root of the depressed cubic equation

double u = MathPow((-0.5*q + MathSqrt(((q*q/4.0) + (p*p*p/27.0)))),(1.0/3.0));

double v = MathPow((-0.5*q - MathSqrt(((q*q/4.0) + (p*p*p/27.0)))),(1.0/3.0));

// Store the QFEL 

QFEL[eL] = u + v;

}

//find out QPR and NQPR

for (int eL=0;eL<21;eL++)

{ 

QPR[eL]  = QFEL[eL]/QFEL[0];

NQPR[eL] = 1 + 0.21*sigma*QPR[eL];

return_array[eL] = NQPR[eL];

}

for (int d=1;d
{ 

//generate energy level and dump into csv

						double QPLn1,QPLn2,QPLn3,QPLn4,QPLn5,
					
						QPLn6,QPLn7,QPLn8,QPLn9,QPLn10,
					
						QPLn11,QPLn12,QPLn13,QPLn14,QPLn15,
					
						QPLn16,QPLn17,QPLn18,QPLn19,QPLn20,QPLn21;
					
if(NQPR[20] != 0.0) QPLn21 = DT_OP[d-1] / NQPR[20];

if(NQPR[19] != 0.0) QPLn20 = DT_OP[d-1] / NQPR[19];

if(NQPR[18] != 0.0) QPLn19 = DT_OP[d-1] / NQPR[18];

if(NQPR[17] != 0.0) QPLn18 = DT_OP[d-1] / NQPR[17];

if(NQPR[16] != 0.0) QPLn17 = DT_OP[d-1] / NQPR[16];

if(NQPR[15] != 0.0) QPLn16 = DT_OP[d-1] / NQPR[15];

if(NQPR[14] != 0.0) QPLn15 = DT_OP[d-1] / NQPR[14];

if(NQPR[13] != 0.0) QPLn14 = DT_OP[d-1] / NQPR[13];

if(NQPR[12] != 0.0) QPLn13 = DT_OP[d-1] / NQPR[12]; 

if(NQPR[11] != 0.0) QPLn12 = DT_OP[d-1] / NQPR[11];

if(NQPR[10] != 0.0) QPLn11 = DT_OP[d-1] / NQPR[10];

if(NQPR[9] != 0.0) QPLn10 = DT_OP[d-1] / NQPR[9];

if(NQPR[8] != 0.0) QPLn9 = DT_OP[d-1] / NQPR[8];

if(NQPR[7] != 0.0) QPLn8 = DT_OP[d-1] / NQPR[7];

if(NQPR[6] != 0.0) QPLn7 = DT_OP[d-1] / NQPR[6];

if(NQPR[5] != 0.0) QPLn6 = DT_OP[d-1] / NQPR[5];

if(NQPR[4] != 0.0) QPLn5 = DT_OP[d-1] / NQPR[4];

if(NQPR[3] != 0.0) QPLn4 = DT_OP[d-1] / NQPR[3];

if(NQPR[2] != 0.0) QPLn3 = DT_OP[d-1] / NQPR[2];

if(NQPR[1] != 0.0) QPLn2 = DT_OP[d-1] / NQPR[1];

if(NQPR[0] != 0.0) QPLn1 = DT_OP[d-1] / NQPR[0]; 

double QPL1 = DT_OP[d-1] * NQPR[0];

double QPL2 = DT_OP[d-1] * NQPR[1];

double QPL3 = DT_OP[d-1] * NQPR[2];

double QPL4 = DT_OP[d-1] * NQPR[3]; 

double QPL5 = DT_OP[d-1] * NQPR[4];

double QPL6 = DT_OP[d-1] * NQPR[5];

double QPL7 = DT_OP[d-1] * NQPR[6];

double QPL8 = DT_OP[d-1] * NQPR[7]; 

double QPL9 = DT_OP[d-1] * NQPR[8];

double QPL10 = DT_OP[d-1] * NQPR[9];

double QPL11 = DT_OP[d-1] * NQPR[10];

double QPL12 = DT_OP[d-1] * NQPR[11];

double QPL13 = DT_OP[d-1] * NQPR[12];

double QPL14 = DT_OP[d-1] * NQPR[13];

double QPL15 = DT_OP[d-1] * NQPR[14];

double QPL16 = DT_OP[d-1] * NQPR[15]; 

double QPL17 = DT_OP[d-1] * NQPR[16];

double QPL18 = DT_OP[d-1] * NQPR[17];

double QPL19 = DT_OP[d-1] * NQPR[18];

double QPL20 = DT_OP[d-1] * NQPR[19]; 

double QPL21 = DT_OP[d-1] * NQPR[20]; 

FileWrite(QPD_FileHandle,DT_YY[d-1],DT_MM[d-1],DT_DD[d-1],

DoubleToString(DT_OP[d-1],8),DoubleToString(DT_HI[d-1],8),

DoubleToString(DT_LO[d-1],8),DoubleToString(DT_CL[d-1],8),

DT_VL[d], DoubleToString(DT_RT[d-1],8),DoubleToString(DT_MA[d-1],8),

DoubleToString(DT_RSI[d-1],8),DoubleToString(DT_MACDM[d-1],8),

DoubleToString(DT_MACDS[d-1],8),DoubleToString(QPL2,8),

DoubleToString(QPL3,8),DoubleToString(QPL4,8),

DoubleToString(QPL5,8),DoubleToString(QPL6,8),

DoubleToString(QPL7,8),DoubleToString(QPL8,8),

DoubleToString(QPL9,8),DoubleToString(QPL10,8),DoubleToString(QPL11,8),

DoubleToString(QPL12,8),

0,

DoubleToString(QPLn2,8),DoubleToString(QPLn3,8),DoubleToString(QPLn4,8),

DoubleToString(QPLn5,8),DoubleToString(QPLn6,8),DoubleToString(QPLn7,8),DoubleToString(QPLn8,8),

DoubleToString(QPLn9,8),DoubleToString(QPLn10,8),DoubleToString(QPLn11,8),DoubleToString(QPLn12,8)

);

} 

FileClose(QPD_FileHandle);

return 0;

}
```


#### Get the Current Price of the product from the TP_Code array


```mql4
int init(){

for(int i = 0; i //go through every single product

{

double temp[21];

read_data(TP_Code[i], temp);

for(int j =0; j<21; j++){ 

all_NQPL[i][j] = temp[j];

//Print("for product ",TP_Code[i],"the normalized energy level ",j," is ",temp[j]);

//Print("NQPL: " , TP_Code[i], "   ", temp[j]);

}

//quantumTrader(temp,TP_Code[i]);

}

return 0;

}
```


## Source Code


Please download the source here: Source Code
