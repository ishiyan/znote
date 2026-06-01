//+------------------------------------------------------------------+
//|                                                 Blau_TStochI.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp."  // copyright
#property link      "http://www.mql5.com"                        // URL
#property description "q-period Stochastic Index (William Blau)" // description
#include <WilliamBlau.mqh>               // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window      // indicator in a separate window
#property indicator_buffers 12           // number of buffers used
#property indicator_plots   1            // indicator plots
//--- horizontal levels
#property indicator_level1 40            // level #0
#property indicator_level2 60            // level #1
#property indicator_levelcolor Silver    // level color
#property indicator_levelstyle STYLE_DOT // line style
#property indicator_levelwidth 1         // level width
//--- min/max values
#property indicator_minimum 0            // minimum
#property indicator_maximum 100          // maximum
//--- graphic plot #0 (Main)
#property indicator_label1  "TStochI"    // label of plot #0
#property indicator_type1   DRAW_LINE    // draw as a line
#property indicator_color1  Blue         // line color
#property indicator_style1  STYLE_SOLID  // line style
#property indicator_width1  1            // line width
//--- input parameters
input int    q=5;  // q - period of Stochastic
input int    r=20; // r - 1st EMA, applied to Stochastic
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays, used for the calculation
double MainBuffer[];       // Stochastic Index (graphic plot #0)
double PriceBuffer[];      // price array
double LLBuffer[];         // minimal value (q bars)
double HHBuffer[];         // maximal value (q bars)
double StochBuffer[];      // q-period Stochastic
double EMA_StochBuffer[];  // r-period 1st EMA
double DEMA_StochBuffer[]; // s-period 2nd EMA
double TEMA_StochBuffer[]; // u-period 3rd EMA
double HHLLBuffer[];       // q-period price range
double EMA_HHLLBuffer[];   // r-period 1st EMA (price range)
double DEMA_HHLLBuffer[];  // s-period 2nd EMA (price range)
double TEMA_HHLLBuffer[];  // u-period 3rd EMA (price range)
//--- global variables
int    begin1, begin2, begin3, begin4; // starting index
int    rates_total_min; // rates total min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);               // index of Stochastic
   // buffers for intermediate calculations
   SetIndexBuffer(1,PriceBuffer,INDICATOR_CALCULATIONS);      // price array
   SetIndexBuffer(2,LLBuffer,INDICATOR_CALCULATIONS);         // minimal value (q bars)
   SetIndexBuffer(3,HHBuffer,INDICATOR_CALCULATIONS);         // maximal value (q bars)
   SetIndexBuffer(4,StochBuffer,INDICATOR_CALCULATIONS);      // q-period Stochastic
   SetIndexBuffer(5,EMA_StochBuffer,INDICATOR_CALCULATIONS);  // r-period of the 1st EMA
   SetIndexBuffer(6,DEMA_StochBuffer,INDICATOR_CALCULATIONS); // s-period of the 2nd EMA
   SetIndexBuffer(7,TEMA_StochBuffer,INDICATOR_CALCULATIONS); // u-period of the 3rd EMA
   SetIndexBuffer(8,HHLLBuffer,INDICATOR_CALCULATIONS);       // q-period of price range
   SetIndexBuffer(9,EMA_HHLLBuffer,INDICATOR_CALCULATIONS);   // r-period of the 1st EMA (price range)
   SetIndexBuffer(10,DEMA_HHLLBuffer,INDICATOR_CALCULATIONS); // s-period of the 2nd EMA (price range)
   SetIndexBuffer(11,TEMA_HHLLBuffer,INDICATOR_CALCULATIONS); // u-period of the 3rd EMA (price range)
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"TStochI");         // label of graphic plot #0
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
   IndicatorSetDouble(INDICATOR_LEVELVALUE,0,40);          // level #0
   IndicatorSetDouble(INDICATOR_LEVELVALUE,1,60);          // level #1
   IndicatorSetInteger(INDICATOR_LEVELCOLOR,Silver);       // level color
   IndicatorSetInteger(INDICATOR_LEVELSTYLE,STYLE_DOT);    // level line style
   IndicatorSetInteger(INDICATOR_LEVELWIDTH,1);            // level line width
   IndicatorSetString(INDICATOR_LEVELTEXT,0,"Oversold");   // level description #0 "Oversold"
   IndicatorSetString(INDICATOR_LEVELTEXT,1,"Overbought"); // level description #1 "Overbought"
//--- min/max values
   IndicatorSetDouble(INDICATOR_MINIMUM,0);   // minimum
   IndicatorSetDouble(INDICATOR_MAXIMUM,100); // maximum
*/
//---
   begin1=q-1;        //                             - StochBuffer[], HHLLBuffer[], LLBuffer[], HHBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_...[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_...[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - TEMA_...[], MainBuffer[]
   //
   rates_total_min=begin4+1; // rates total min
//--- starting index #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- short name
   string shortname=PriceName(AppliedPrice)+","+string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_TStochI("+shortname+")");
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
//--- rates total
   if(rates_total<rates_total_min) return(0);
//--- calculation of PriceBuffer[]
   CalculatePriceBuffer(
                        AppliedPrice,        // price type
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        PriceBuffer          // price array
                       );
//--- calculation of q-period Stochastic and q-period price range
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // starting from begin1
      for(i=0;i<pos;i++)       // pos
        {
         StochBuffer[i]=0.0;   // zero values
         HHLLBuffer[i]=0.0;    //
         LLBuffer[i]=0.0;      //
         HHBuffer[i]=0.0;      //
        }
     }
   else pos=prev_calculated-1; // overwise calculate only last bar
   // calculation of StochBuffer[], HHLLBuffer[], LLBuffer[], HHBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      // LLBuffer[] - search for the minimal price (q bars)
      // HHBuffer[] - search for the maximal price (q bars)
      min=1000000.0;
      max=-1000000.0;
      for(k=i-(q-1);k<=i;k++)
        {
         if(min>Low[k])  min=Low[k];
         if(max<High[k]) max=High[k];
        }
      LLBuffer[i]=min;
      HHBuffer[i]=max;
      // calculation of StochBuffer[] - q-period Stochastic
      StochBuffer[i]=PriceBuffer[i]-LLBuffer[i];
      // calculation of HHLLBuffer[] - q-period price range
      HHLLBuffer[i]=HHBuffer[i]-LLBuffer[i];
     }
//--- EMA smoothing
   // r-period 1st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           StochBuffer,     // input array
                           EMA_StochBuffer  // output array
                          );
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,HHLLBuffer,EMA_HHLLBuffer);
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_StochBuffer,DEMA_StochBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_HHLLBuffer,DEMA_HHLLBuffer);
   // u-period 3rd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_StochBuffer,TEMA_StochBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_HHLLBuffer,TEMA_HHLLBuffer);
//--- calculation of Stochastic Index (graphic plot #0)
   if(prev_calculated==0)      // at first call
     {
      pos=begin4;              // starting from begin4
      for(i=0;i<pos;i++)       // pos
         MainBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise calculate only last bar
   // calc MainBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      value1=100*TEMA_StochBuffer[i];
      value2=TEMA_HHLLBuffer[i];
      MainBuffer[i]=(value2>0)?value1/value2:0;
     }
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+