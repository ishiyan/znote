//+------------------------------------------------------------------+
//|                                                     Blau_SMI.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "q-period Stochastic Momentum Index (William Blau)" // description
#include <WilliamBlau.mqh>               // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window      // indicator in a separate window
#property indicator_buffers 12           // number of buffers used
#property indicator_plots   1            // number of plots
//--- horizontal levels
#property indicator_level1 -40           // level #0 (vertical axis)
#property indicator_level2 40            // level #1 (vertical axis)
#property indicator_levelcolor Silver    // level line color
#property indicator_levelstyle STYLE_DOT // level line style
#property indicator_levelwidth 1         // level line width
//--- min/max values on the axis
#property indicator_minimum -100         // lower bound
#property indicator_maximum 100          // upper bound
//--- graphic plot #0 (Main)
#property indicator_label1  "SMI"        // label of graphic plot #0
#property indicator_type1   DRAW_LINE    // draw as a line
#property indicator_color1  Blue         // line color
#property indicator_style1  STYLE_SOLID  // line style
#property indicator_width1  1            // indicator line width
//--- input parameters
input int    q=5;  // q - period of Stochastic Momentum
input int    r=20; // r - 1st EMA, applied to Stochastic Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays, used for the calculation
double MainBuffer[];          // Stochastic Momentum Index (graphic plot #0)
double PriceBuffer[];         // price array
double LLBuffer[];            // minimal value of the lowest price (q period)
double HHBuffer[];            // maximal value of the highest price (q period)
double SMBuffer[];            // q-period Stochastic Momentum
double EMA_SMBuffer[];        // r-period of the 1st EMA
double DEMA_SMBuffer[];       // s-period of the 2nd EMA
double TEMA_SMBuffer[];       // u-period of the 3rd EMA
double HalfHHLLBuffer[];      // half of q-period Price Range
double EMA_HalfHHLLBuffer[];  // r-period of the 1st EMA (half of price range)
double DEMA_HalfHHLLBuffer[]; // s-period of the 2nd EMA (half of price range)
double TEMA_HalfHHLLBuffer[]; // u-period of the 3rd EMA (half of price range)
//--- global variable
int    begin1, begin2, begin3, begin4; // starting index
int    rates_total_min; // rates total min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers
   // graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);                   // Stochastic Momentum Index
   // buffers, used for intermediate calculations
   SetIndexBuffer(1,PriceBuffer,INDICATOR_CALCULATIONS);          // price array
   SetIndexBuffer(2,LLBuffer,INDICATOR_CALCULATIONS);             // minimal value of the lowest price of the period q
   SetIndexBuffer(3,HHBuffer,INDICATOR_CALCULATIONS);             // maximal value of the highest price of the period q
   SetIndexBuffer(4,SMBuffer,INDICATOR_CALCULATIONS);             // q-period Stochastic Momentum
   SetIndexBuffer(5,EMA_SMBuffer,INDICATOR_CALCULATIONS);         // r-period 1st EMA
   SetIndexBuffer(6,DEMA_SMBuffer,INDICATOR_CALCULATIONS);        // s-period 2nd EMA
   SetIndexBuffer(7,TEMA_SMBuffer,INDICATOR_CALCULATIONS);        // u-period 3rd EMA
   SetIndexBuffer(8,HalfHHLLBuffer,INDICATOR_CALCULATIONS);       // half q-period price range
   SetIndexBuffer(9,EMA_HalfHHLLBuffer,INDICATOR_CALCULATIONS);   // r-period 1st EMA (half of price range)
   SetIndexBuffer(10,DEMA_HalfHHLLBuffer,INDICATOR_CALCULATIONS); // s-period 2nd EMA (half of price range)
   SetIndexBuffer(11,TEMA_HalfHHLLBuffer,INDICATOR_CALCULATIONS); // u-period 3rd EMA (half of price range)
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"SMI");             // graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // draw as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,2);
/*
//--- horizontal levels
   IndicatorSetInteger(INDICATOR_LEVELS,2);                // number of levels
   IndicatorSetDouble(INDICATOR_LEVELVALUE,0,-40);         // level #0 (vertical axis)
   IndicatorSetDouble(INDICATOR_LEVELVALUE,1,40);          // level #1 (vertical axis)
   IndicatorSetInteger(INDICATOR_LEVELCOLOR,Silver);       // level line color
   IndicatorSetInteger(INDICATOR_LEVELSTYLE,STYLE_DOT);    // level line style
   IndicatorSetInteger(INDICATOR_LEVELWIDTH,1);            // level line width
   IndicatorSetString(INDICATOR_LEVELTEXT,0,"Oversold");   // level #0 "Oversold"
   IndicatorSetString(INDICATOR_LEVELTEXT,1,"Overbought"); // level #1 "Overbought"
//--- min/max values
   IndicatorSetDouble(INDICATOR_MINIMUM,-100); // lower bound
   IndicatorSetDouble(INDICATOR_MAXIMUM,100);  // upper bound
*/
//---
   begin1=q-1;        //                             - SMBuffer[], HalfHHLLBuffer[], LLBuffer[], HHBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_...[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_...[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - TEMA_...[], MainBuffer[]
   //
   rates_total_min=begin4+1; // minimal rates
//--- starting bar index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- short indicator name
   string shortname=PriceName(AppliedPrice)+","+string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_SMI("+shortname+")");
//--- OnInit done
   return(0);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(
                const int rates_total,     // rates total
                const int prev_calculated, // bars, calculated at previous call
                const datetime &Time[],    // Time
                const double &Open[],      // Open
                const double &High[],      // High
                const double &Low[],       // Low
                const double &Close[],     // Close
                const long &TickVolume[],  // Tick Volume
                const long &Volume[],      // Real Volume
                const int &Spread[]        // Spread
               )
  {
   int i,k,pos;
   double min,max;
   double value1,value2;
//--- rates total min
   if(rates_total<rates_total_min) return(0);
//--- calculation of PriceBuffer[] array
   CalculatePriceBuffer(
                        AppliedPrice,        // price type
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        PriceBuffer          // target array
                       );
//--- calculation of q-period Stochastic Momentum and half of q-period of price range
   // SMBuffer[], HalfHHLLBuffer[], LLBuffer[], HHBuffer[]
   if(prev_calculated==0)       // at first call
     {
      pos=begin1;               // starting from 0
      for(i=0;i<pos;i++)        // pos values
        {
         SMBuffer[i]=0.0;       // zero values
         HalfHHLLBuffer[i]=0.0; //
         LLBuffer[i]=0.0;       //
         HHBuffer[i]=0.0;       //
        }
     }
   else pos=prev_calculated-1;  // overwise calculate only last value
   // calculation of SMBuffer[], HalfHHLLBuffer[], LLBuffer[], HHBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      // calculation of LLBuffer[] - search for minimal price value (q bars)
      // calculation of HHBuffer[] - search for maximal price value (q bars)
      min=1000000.0;
      max=-1000000.0;
      for(k=i-(q-1);k<=i;k++)
        {
         if(min>Low[k])  min=Low[k];
         if(max<High[k]) max=High[k];
        }
      LLBuffer[i]=min;
      HHBuffer[i]=max;
      // calculation of SMBuffer[] - q-period Stochastic Momentum
      SMBuffer[i]=PriceBuffer[i]-0.5*(LLBuffer[i]+HHBuffer[i]);
      // calculation of HalfHHLLBuffer[] - half of price range (q bars)
      HalfHHLLBuffer[i]=0.5*(HHBuffer[i]-LLBuffer[i]);
     }
//--- EMA smoothing
   // r-period 1st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           SMBuffer,        // input array
                           EMA_SMBuffer     // target array
                          );
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,HalfHHLLBuffer,EMA_HalfHHLLBuffer);
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_SMBuffer,DEMA_SMBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_HalfHHLLBuffer,DEMA_HalfHHLLBuffer);
   // u-period 3rd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_SMBuffer,TEMA_SMBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_HalfHHLLBuffer,TEMA_HalfHHLLBuffer);
//--- calculaton of Stochastic Momentum Index (graphic plot #0)
   if(prev_calculated==0)      // at first call
     {
      pos=begin4;              // starting from 0
      for(i=0;i<pos;i++)       // pos values
         MainBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // calculation of MainBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      value1=100*TEMA_SMBuffer[i];
      value2=TEMA_HalfHHLLBuffer[i];
      MainBuffer[i]=(value2>0)?value1/value2:0;
     }
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+