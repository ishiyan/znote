//+------------------------------------------------------------------+
//|                                               WTT_CycleSwing.mq4 |
//|                                Copyright 2014- 2017, WhenToTrade |
//|                                      https://www.whentotrade.com |
//|             Book reference: https://www.amazon.com/dp/1974658244 |
//|               License: Attribution 4.0 International (CC BY 4.0) |
//+------------------------------------------------------------------+
#property copyright "Copyright 2014-2017, WhenToTrade"
#property link      "https://www.whentotrade.com"
#property description "WhenToTrade Cycle Swing Indicator (CSI)"
#property description "The CSI is an ultra smooth momentum indicator based on dominant cycles acceleration"
#property description "See book reference: 'Decoding The Hidden Market Rhyhtm - Part 1'"
#property version   "1.00"
#property strict
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_plots   2
//--- plot CSI
#property indicator_label1  "CSI"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrRed
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1

//--- indicator buffers
double CSIBuffer[];
double sourceValues[50];

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {

//--- indicator buffers mapping
   SetIndexBuffer(0,CSIBuffer);

//name and label
   //MQL4:
   //IndicatorShortName("WTT CSI");
   //MQL5:
   IndicatorSetString(INDICATOR_SHORTNAME,"WTT CSI");
   
   //MQL4:
   // SetIndexLabel(0,"CSI");
   //MQL5:
   PlotIndexSetString(0,PLOT_LABEL,"CSI");

//Set the starting point of CSI
   //MQL4:
   //SetIndexDrawBegin(0,250);
   //MQL5:
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,250);

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

   if(rates_total<=200) return(0);

   //--- start variable for calculation of bars
   int start_index=prev_calculated;

   //--- work at the last bar if the indicator values have already been calculated at the previous tick
   if(prev_calculated>0)
      start_index--;

   //--- define indexing direction in arrays
   bool as_series_closes=ArrayGetAsSeries(close);
   bool as_series_buffer=ArrayGetAsSeries(CSIBuffer);
      
   //--- replace indexing direction with direct one if necessary
   if(as_series_closes)
      ArraySetAsSeries(close,false);
   if(as_series_buffer)
      ArraySetAsSeries(CSIBuffer,false);
  
   //--- calculate indicator values
   for(int i=start_index;i<rates_total;i++)
     {
      //--- skip
      if(i<=50) 
        {
         CSIBuffer[i]=0;
         continue;
        }

      //--- prepare data
      for(int p=0;p<50;p++)
         sourceValues[p]=close[i-49+p];

      //--- pre-process dominant cycle momentum
      double thrust1=iWTT_CSI_processor(sourceValues,1);
      double thrust2=iWTT_CSI_processor(sourceValues,10);
      
      //--- get the final cycle acceleration (aka swing)
      CSIBuffer[i]=thrust1-thrust2;

     }

   //--- return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| www.WhenToTrade.com Cycle Swing Pre-Processor                    |
//+------------------------------------------------------------------+
double Cycle1(int i, double waveThrottle, int cycs)
{
   if (i==0) return 1.0+waveThrottle;
   if (i==1) return 1.0+waveThrottle*5.0;
   if (i==(cycs-1)) return 1.0+waveThrottle;
   if (i==(cycs-2)) return 1.0+waveThrottle*5.0;
   
   return 6.0*waveThrottle+1.0;
}

double Cycle2(int i, double waveThrottle, int cycs)
{ 
   if (i==0) return -2.0*waveThrottle;
   if (i==(cycs-1)) return 0.0;
   if (i==(cycs-2)) return -2.0*waveThrottle;
   
   return -4.0*waveThrottle;
}

double Cycle3(int i, double waveThrottle, int cycs)
{
   if (i==(cycs-1)) return 0.0;
   if (i==(cycs-2)) return 0.0;
   
   return waveThrottle;
}

double iWTT_CSI_processor(const double &raw[], int CycleCount)
  {
   double wtt1=0,wtt2=0,wtt3=0,wtt4=0,wtt5=0,_wtt1=0,_wtt2=0,_wtt3=0,_wtt4=0,_wtt5=0;
   double momentum,acceleration,swing; 
   int cycs=50;
   double waveThrottle=160*CycleCount;
   double currentVal;

   for(int i=0;i<cycs;i++)
   {
      swing=Cycle1(i,waveThrottle,cycs)-wtt4*wtt1-_wtt5*_wtt2;
      if(swing==0) break;
      momentum= Cycle2(i,waveThrottle,cycs);
      _wtt1  = wtt1;
      wtt1   = (momentum-wtt4*wtt2)/swing;
      
      acceleration=Cycle3(i,waveThrottle,cycs);
      _wtt2  = wtt2;
      wtt2   = acceleration/swing;

      currentVal=(raw[i]-_wtt3*_wtt5-wtt3*wtt4)/swing;
      _wtt3  = wtt3;
      wtt3   = currentVal;
      wtt4   = momentum-wtt5*_wtt1;
      _wtt5  = wtt5;
      wtt5   = acceleration;
   }

   return currentVal;
  }
//+------------------------------------------------------------------+