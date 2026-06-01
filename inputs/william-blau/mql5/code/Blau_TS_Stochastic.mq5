//+------------------------------------------------------------------+
//|                                           Blau_TS_Stochastic.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "Stochastic Oscillator (William Blau)"    // description
#include <WilliamBlau.mqh>                 // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window        // indicator in a separate window
#property indicator_buffers 13             // number of buffers used
#property indicator_plots   2              // number of plots
//--- horizontal levels
#property indicator_level1 40              // level #0
#property indicator_level2 60              // level #1
#property indicator_levelcolor Silver      // level color
#property indicator_levelstyle STYLE_DOT   // level style
#property indicator_levelwidth 1           // level width
//--- scale
#property indicator_minimum 0              // minimum
#property indicator_maximum 100            // maximum
//--- graphic plot #0 (Main)
#property indicator_label1  "%k"           // label of plot #0
#property indicator_type1   DRAW_HISTOGRAM // drawing type
#property indicator_color1  Silver         // histogram color
#property indicator_style1  STYLE_SOLID    // line style
#property indicator_width1  2              // line width
//--- graphic plot #1 (Signal Line)
#property indicator_label2  "%d,Signal"    // label of plot #1
#property indicator_type2   DRAW_LINE      // draw as a line
#property indicator_color2  Red            // line color
#property indicator_style2  STYLE_SOLID    // line style
#property indicator_width2  1              // line width
//--- input parameters
input int    q=5;  // q - period of Stochastic
input int    r=20; // r - 1st EMA, applied to Stochastic
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input int    ul=3; // ul - period of a Signal Line
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays
double MainBuffer[];       // fast Stochastic (graphic plot #0)
double SignalBuffer[];     // slow Stochastic: ul-period EMA of the fast stochastic (graphic plot #1)
double PriceBuffer[];      // price array
double LLBuffer[];         // minimal value (q bars)
double HHBuffer[];         // maximal value (q bars)
double StochBuffer[];      // q-period Stochastic
double EMA_StochBuffer[];  // r-period of the 1st EMA
double DEMA_StochBuffer[]; // s-period of the 2nd EMA
double TEMA_StochBuffer[]; // u-period of the 3rd EMA
double HHLLBuffer[];       // q-period of price range
double EMA_HHLLBuffer[];   // r-period of the 1st EMA (price range)
double DEMA_HHLLBuffer[];  // s-period of the 2nd EMA (price range)
double TEMA_HHLLBuffer[];  // u-period of the 3rd EMA (price range)
//--- global variables
int    begin1, begin2, begin3, begin4, begin5; // starting index
int    rates_total_min; // rates total min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers
   // graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);               // fast Stochastic
   // graphic plot #1
   SetIndexBuffer(1,SignalBuffer,INDICATOR_DATA);             // slow Stochastic: ul-period EMA of the fast Stochastic
   // buffers, used for intermediate calculations
   SetIndexBuffer(2,PriceBuffer,INDICATOR_CALCULATIONS);      // price array
   SetIndexBuffer(3,LLBuffer,INDICATOR_CALCULATIONS);         // min value (q bars)
   SetIndexBuffer(4,HHBuffer,INDICATOR_CALCULATIONS);         // max value (q bars)
   SetIndexBuffer(5,StochBuffer,INDICATOR_CALCULATIONS);      // q-period Stochastic
   SetIndexBuffer(6,EMA_StochBuffer,INDICATOR_CALCULATIONS);  // r-period of the 1st EMA
   SetIndexBuffer(7,DEMA_StochBuffer,INDICATOR_CALCULATIONS); // s-period of the 2nd EMA
   SetIndexBuffer(8,TEMA_StochBuffer,INDICATOR_CALCULATIONS); // u-period of the 3rd EMA
   SetIndexBuffer(9,HHLLBuffer,INDICATOR_CALCULATIONS);       // q-period price range
   SetIndexBuffer(10,EMA_HHLLBuffer,INDICATOR_CALCULATIONS);  // r-period of the 1st EMA (price range)
   SetIndexBuffer(11,DEMA_HHLLBuffer,INDICATOR_CALCULATIONS); // s-period of the 2nd EMA (price range)
   SetIndexBuffer(12,TEMA_HHLLBuffer,INDICATOR_CALCULATIONS); // u-period of the 3rd EMA (price range)
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"%k");                // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_HISTOGRAM); // draw as a histogram
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Silver);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID);   // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,2);             // line width
//--- graphic plot #1 (Signal Line)
   PlotIndexSetString(1,PLOT_LABEL,"%d,Signal");         // label of graphic plot #1
   PlotIndexSetInteger(1,PLOT_DRAW_TYPE,DRAW_LINE);      // draw as a line
   PlotIndexSetInteger(1,PLOT_LINE_COLOR,Red);           // line color
   PlotIndexSetInteger(1,PLOT_LINE_STYLE,STYLE_SOLID);   // line style
   PlotIndexSetInteger(1,PLOT_LINE_WIDTH,1);             // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,2);
/*
//--- horizontal levels
   IndicatorSetInteger(INDICATOR_LEVELS,2);                // number of levels
   IndicatorSetDouble(INDICATOR_LEVELVALUE,0,40);          // level #0
   IndicatorSetDouble(INDICATOR_LEVELVALUE,1,60);          // level #1
   IndicatorSetInteger(INDICATOR_LEVELCOLOR,Silver);       // level color
   IndicatorSetInteger(INDICATOR_LEVELSTYLE,STYLE_DOT);    // level style
   IndicatorSetInteger(INDICATOR_LEVELWIDTH,1);            // level width
   IndicatorSetString(INDICATOR_LEVELTEXT,0,"Oversold");   // level description #0 "Oversold"
   IndicatorSetString(INDICATOR_LEVELTEXT,1,"Overbought"); // level description #1 "Overbought"
//--- min/max values
   IndicatorSetDouble(INDICATOR_MINIMUM,0);   // min value
   IndicatorSetDouble(INDICATOR_MAXIMUM,100); // max value
*/
//---
   begin1=q-1;         //                                    - StochBuffer[], HHLLBuffer[], LLBuffer[], HHBuffer[]
   begin2=begin1+r-1;  // or =(q-1)+(r-1)                    - EMA_...[]
   begin3=begin2+s-1;  // or =(q-1)+(r-1)+(s-1)              - DEMA_...[]
   begin4=begin3+u-1;  // or =(q-1)+(r-1)+(s-1)+(u-1)        - TEMA_...[], MainBuffer[]
   begin5=begin4+ul-1; // or =(q-1)+(r-1)+(s-1)+(u-1)+(ul-1) - SignalBuffer[]
   //
   rates_total_min=begin5+1; // rates total min
//--- starting bar index (begin4) for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- starting bar index (begin5) for plot #1
   PlotIndexSetInteger(1,PLOT_DRAW_BEGIN,begin5);
//--- short indicator name
   string shortname=PriceName(AppliedPrice)+","+string(q)+","+string(r)+","+string(s)+","+string(u)+","+string(ul);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_TS_Stoch("+shortname+")");
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
      // StochBuffer[] - q-period Stochastic
      StochBuffer[i]=PriceBuffer[i]-LLBuffer[i];
      // HHLLBuffer[] - q-period price range
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
//--- calculation of fast Stochastic (graphic plot #0)
   if(prev_calculated==0)      // at first call
     {
      pos=begin4;              // starting from begin4
      for(i=0;i<pos;i++)       // pos
         MainBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise calculate only last bar
   // calculation of MainBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      value1=100*TEMA_StochBuffer[i];
      value2=TEMA_HHLLBuffer[i];
      MainBuffer[i]=(value2>0)?value1/value2:0;
     }
//--- calculation of slow Stochastic (graphic plot #1)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin4,ul,MainBuffer,SignalBuffer);
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+