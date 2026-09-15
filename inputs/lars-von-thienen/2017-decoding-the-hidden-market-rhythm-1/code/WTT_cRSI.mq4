//+------------------------------------------------------------------+
//|                                                     WTT_cRSI.mq4 |
//|                                      Copyright 2017, WhenToTrade |
//|                                      https://www.whentotrade.com |
//|                 use dominant cycle as input parameter            |
//|                 as described in book: http://amzn.com/1974658244 |
//|               License: Attribution 4.0 International (CC BY 4.0) |
//+------------------------------------------------------------------+
#property copyright "Copyright 2017, WhenToTrade, Book: Decoding The Hidden Market Rhythm - Dynamic Cycles"
#property description "Cyclic smoothed RSI Indicator (cRSI). Input the dominant cycle length as described in Chapter 4: Fine-tuning technical indicators"
#property link "http://amzn.com/1974658244"
#property version "1.00"
#property strict
#property indicator_separate_window
#property indicator_buffers 7
#property indicator_plots   4
//#property indicator_minimum    0
//#property indicator_maximum    100
//--- plot CRSI
#property indicator_label1  "CRSI"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrRed
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1
//--- plot UpperBand
#property indicator_label2  "UpperBand"
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrMediumBlue
#property indicator_style2  STYLE_SOLID
#property indicator_width2  1
//--- plot LowerBand
#property indicator_label3  "LowerBand"
#property indicator_type3   DRAW_LINE
#property indicator_color3  clrMediumBlue
#property indicator_style3  STYLE_SOLID
#property indicator_width3  1
//--- plot NeutralBand
#property indicator_label4  "NeutralBand"
#property indicator_type4   DRAW_LINE
#property indicator_color4  clrLightSlateGray
#property indicator_style4  STYLE_SOLID
#property indicator_width4  1

#property indicator_type5 DRAW_NONE 
#property indicator_type6 DRAW_NONE
#property indicator_type7 DRAW_NONE

#property indicator_level1     30.0
#property indicator_level2     70.0
#property indicator_levelcolor clrSilver
#property indicator_levelstyle STYLE_DOT

//--- input parameters
input int CycleLength=20;
input int Vibration=10;
input int CyclicMemory=40;
input int Leveling=10;

//--- indicator buffers
double CRSIBuffer[];
double UpperBandBuffer[];
double LowerBandBuffer[];
double NeutralBandBuffer[];

//--- buffers
double ExtRSIBuffer[];
double ExtPosBuffer[];
double ExtNegBuffer[];

double cycleConstant;
double torque;
int phasingLag;
double aperc;
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers mapping
   
   SetIndexBuffer(0,CRSIBuffer);
   SetIndexBuffer(1,UpperBandBuffer);
   SetIndexBuffer(2,LowerBandBuffer);
   SetIndexBuffer(3,NeutralBandBuffer);
   SetIndexBuffer(4,ExtRSIBuffer);
   SetIndexBuffer(5,ExtPosBuffer);
   SetIndexBuffer(6,ExtNegBuffer);
      
   string short_name;
   short_name="cRSI("+string(CycleLength)+")";
   IndicatorShortName(short_name);
   SetIndexLabel(0,short_name);
   
   SetIndexDrawBegin(0, CycleLength);
   
   cycleConstant = (CycleLength - 1);
	torque		= 2.0 / (Vibration + 1);
	phasingLag	= (int)((Vibration - 1) / 2.0);
	aperc = (double)Leveling / 100;
   
//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
//---
   int    i,pos;
   double diff;
//---
   if(Bars<=CycleLength || CycleLength<2)
      return(0);  
      
//--- counting from 0 to rates_total
   ArraySetAsSeries(ExtRSIBuffer,false);
   ArraySetAsSeries(ExtPosBuffer,false);
   ArraySetAsSeries(ExtNegBuffer,false);
   ArraySetAsSeries(CRSIBuffer,false);
   ArraySetAsSeries(UpperBandBuffer,false);
   ArraySetAsSeries(LowerBandBuffer,false);
   ArraySetAsSeries(NeutralBandBuffer,false);
   ArraySetAsSeries(close,false);
//--- preliminary calculations
   pos=prev_calculated-1;
   if(pos<=CycleLength)
     {
      //--- first RSIPeriod values of the indicator are not calculated
      ExtRSIBuffer[0]=0.0;
      ExtPosBuffer[0]=0.0;
      ExtNegBuffer[0]=0.0;
      CRSIBuffer[0]=0.0;
      double sump=0.0;
      double sumn=0.0;
      for(i=1; i<=CycleLength; i++)
        {
         ExtRSIBuffer[i]=0.0;
         ExtPosBuffer[i]=0.0;
         ExtNegBuffer[i]=0.0;
         CRSIBuffer[i]=0.0;
         diff=close[i]-close[i-1];
         if(diff>0)
            sump+=diff;
         else
            sumn-=diff;
        }
      //--- calculate first visible value
      ExtPosBuffer[CycleLength]=sump/CycleLength;
      ExtNegBuffer[CycleLength]=sumn/CycleLength;
      if(ExtNegBuffer[CycleLength]!=0.0)
         ExtRSIBuffer[CycleLength]=100.0-(100.0/(1.0+ExtPosBuffer[CycleLength]/ExtNegBuffer[CycleLength]));
      else
        {
         if(ExtPosBuffer[CycleLength]!=0.0)
            ExtRSIBuffer[CycleLength]=100.0;
         else
            ExtRSIBuffer[CycleLength]=50.0;
        }
      //--- prepare the position value for main calculation
      pos=CycleLength+1;
      
      CRSIBuffer[CycleLength]=ExtRSIBuffer[CycleLength];
     }
//--- the main loop of calculations
   for(i=pos; i<rates_total && !IsStopped(); i++)
     {
      diff=close[i]-close[i-1];
      ExtPosBuffer[i]=(ExtPosBuffer[i-1]*(CycleLength-1)+(diff>0.0?diff:0.0))/CycleLength;
      ExtNegBuffer[i]=(ExtNegBuffer[i-1]*(CycleLength-1)+(diff<0.0?-diff:0.0))/CycleLength;
      if(ExtNegBuffer[i]!=0.0)
         ExtRSIBuffer[i]=100.0-100.0/(1+ExtPosBuffer[i]/ExtNegBuffer[i]);
      else
        {
         if(ExtPosBuffer[i]!=0.0)
            ExtRSIBuffer[i]=100.0;
         else
            ExtRSIBuffer[i]=50.0;
        }
        
      CRSIBuffer[i]=torque * (2 * ExtRSIBuffer[i] - ExtRSIBuffer[i-phasingLag]) + (1-torque) * CRSIBuffer[i-1]; 
      
      if (i < CycleLength+phasingLag+CyclicMemory) continue;
			
			double ub; double db; double lmax; double lmin; double ratio;
			double testvalue; int above; int below; double mstep;
			
			
			lmax=-999999; lmin=999999;
			for (int y=0; y<CyclicMemory; y++){
				if (CRSIBuffer[i-y]>lmax) lmax=CRSIBuffer[i-y]; 
				else if (CRSIBuffer[i-y]<lmin) lmin=CRSIBuffer[i-y];
			}
			
			mstep=(lmax-lmin)/100;

			db=0;
			for (int steps=0; steps<=100; steps++)
			{
				testvalue=lmin+(mstep*steps);
				above=0; below=0;
				
				for (int m=0; m<CyclicMemory; m++)
					if (CRSIBuffer[i-m]>=testvalue) above++; else below++;
					
				ratio=(double)below / (double)CyclicMemory;
				if (ratio>=aperc)  { db=testvalue; break; }
			}
			
			
			ub=0;
			for (int steps=0; steps<=100; steps++)
			{
				testvalue=lmax-(mstep*steps);
				above=0; below=0;
				
				for (int m=0; m<CyclicMemory; m++)
					if (CRSIBuffer[i-m]>=testvalue) above++; else below++;
					
				ratio=(double)above / (double)CyclicMemory;
				if (ratio>=aperc)  { ub=testvalue; break; }
			}
      
      
      LowerBandBuffer[i]=db;
      UpperBandBuffer[i]=ub;
      NeutralBandBuffer[i]=(double)((ub+db)/2);
     }
   
//--- return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+