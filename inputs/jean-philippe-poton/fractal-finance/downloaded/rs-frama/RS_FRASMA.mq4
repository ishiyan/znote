//+------------------------------------------------------------------------------------------------------------------+
//|                                                                              RS_FRASMA.mq4                       |
//|                                                                              jppoton [jppoton@yahoo.com]         |
//|                                                                                                                  |
//| This indicator is a fractalised moving average similar to the one found in FRASMA.mq4 except that it is using    | 
//| a rescaled range analysis to compute the Hurst exponent, then used to weigh a simple moving average.             |
//| The detailed explanation of the method can be found on my blog: http://fractalfinance.blogspot.com/              | 
//| WARNING: The rescaled range analysis is rather demanding in terms of computation's time, it is therefore strongly|
//| advised to keep the period relatively small, the defaut is 64, but even at such a low level, some delay is to be |
//| expected before the RS_FRASMA gets drawn.                                                                        |
//|                                                                                                                  |
//|                                                                                                                  |                                                                                                         |   
//| v1.0 - October 2009                                                                                              |   
//+------------------------------------------------------------------------------------------------------------------+
#property copyright "Copyright © 2008, jppoton@yahoo.com"
#property link      "http://fractalfinance.blogspot.com/"
//----
#property indicator_chart_window

#property indicator_color1 Red
#property indicator_width1 2
//************************************************************
// Input parameters
//************************************************************
extern int    period        =64;
extern int    normal_speed  =30;
extern int    PIP_Convertor =10000;
extern int    type_data     =PRICE_CLOSE;
//************************************************************
// Constant
//************************************************************
string FILENAME="RS_FRASMA.mq4";
//************************************************************
// Private vars
//************************************************************
//---- input buffer
double ExtInputBuffer[];
//---- output buffer
double ExtOutputBuffer[];
//+-----------------------------------------------------------------------+
//| FUNCTION : init                                                       |                                                                                                                                                                                                                                                      
//| Initialization function                                               |                                   
//| Check the user input parameters and convert them in appropriate types.|                                                                                                    
//+-----------------------------------------------------------------------+
int init()
  {
// Check period input parameter
   if(period<2)
     {
      Alert("[ 10-ERROR  "+FILENAME+" ] input parameter \"period\" must be >= 1 ("+period+")");
      return( -1 );
     }
   if(type_data<PRICE_CLOSE || type_data>PRICE_WEIGHTED)
     {
      Alert("[ 20-ERROR  "+FILENAME+" ] input parameter \"type_data\" unknown ("+type_data+")");
      return( -1 );
     }

   IndicatorBuffers(2);
   SetIndexBuffer(0,ExtOutputBuffer);
   SetIndexStyle(0,DRAW_LINE,STYLE_SOLID,2);
   SetIndexDrawBegin(0,2*period);
   SetIndexBuffer(1,ExtInputBuffer);
//----
   return( 0 );
  }
//+------------------------------------------------------------------+
//| FUNCTION : deinit                                                |
//| Custor indicator deinitialization function                       |
//+------------------------------------------------------------------+
int deinit()
  {
   return(0);
  }
//+------------------------------------------------------------------+
//| FUNCTION : start                                                 |
//| This callback is fired by metatrader for each tick               |
//+------------------------------------------------------------------+
int start()
  {
   int counted_bars=IndicatorCounted();
   if(counted_bars < 0)  return(-1);
   if(counted_bars>0) counted_bars--;
   int limit=Bars-counted_bars;
   if(counted_bars==0) limit-=1+period;

   _computeLastNbBars(limit);
//----
   return( 0 );
  }
//+================================================================================================================+
//+=== FUNCTION : _computeLastNbBars                                                                            ===+
//+===                                                                                                          ===+
//+===                                                                                                          ===+
//+=== This callback is fired by metatrader for each tick                                                       ===+
//+===                                                                                                          ===+
//+=== In :                                                                                                     ===+
//+===    - lastBars : these "n" last bars must be repainted                                                    ===+
//+===                                                                                                          ===+
//+================================================================================================================+
//+------------------------------------------------------------------+
//| FUNCTION : _computeLastNbBars                                    |
//| This callback is fired by metatrader for each tick               |
//| In : - lastBars : these "n" last bars must be repainted          | 
//+------------------------------------------------------------------+
double tmpArray[];
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void _computeLastNbBars(int lastBars)
  {
   int pos;
   switch(type_data)
     {
      case PRICE_CLOSE  : ArrayCopy(tmpArray,Close,0,0,WHOLE_ARRAY); RSAnalysis(lastBars, tmpArray); break;
      case PRICE_OPEN   : ArrayCopy(tmpArray,Open,0,0,WHOLE_ARRAY);  RSAnalysis(lastBars, tmpArray); break;
      case PRICE_HIGH   : ArrayCopy(tmpArray,High,0,0,WHOLE_ARRAY);  RSAnalysis(lastBars, tmpArray); break;
      case PRICE_LOW    : ArrayCopy(tmpArray,Low,0,0,WHOLE_ARRAY);   RSAnalysis(lastBars, tmpArray); break;
      case PRICE_MEDIAN   :
         for(pos=lastBars; pos>=0; pos--)ExtInputBuffer[pos]=(High[pos]+Low[pos])/2.0; RSAnalysis(lastBars,ExtInputBuffer);
         break;
      case PRICE_TYPICAL  :
         for(pos=lastBars; pos>=0; pos--)ExtInputBuffer[pos]=(High[pos]+Low[pos]+Close[pos])/3.0; RSAnalysis(lastBars,ExtInputBuffer);
         break;
      case PRICE_WEIGHTED :
         for(pos=lastBars; pos>=0; pos--)ExtInputBuffer[pos]=(High[pos]+Low[pos]+Close[pos]+Close[pos])/4.0; RSAnalysis(lastBars,ExtInputBuffer);
         break;
      default :
         Alert("[ 20-ERROR  "+FILENAME+" ] the imput parameter type_data <"+type_data+"> is unknown");
     }
  }
//+---------------------------------------------------------------------+
//| FUNCTION : RSAnalysis                                               |
//| Compute the value of R/s for the various partition of the           |
//| starting set of "period" values                                     |
//| In :                                                                |
//|    - lastBars : these "n" last bars must be repainted               |
//|    - inputData : data array on which the RS Analysis will be applied|
//+---------------------------------------------------------------------+
void RSAnalysis(int lastBars,double &inputData[])
  {
   int  pos,i,j,k,l,m,z,iter,K0,t;
   int  d[10],K[10];
   double  max,min,sum,mu,std,H1,H2,H,sumx,sumx2,sumy,sumy2,sumxy,alpha,speed;
   double  W[200][200],Wi[200],R[500],Rst[500],Rs[500];
//----
   for(pos=lastBars; pos>=0; pos--)
     {
      K0=MathFloor(period/4);
      iter=MathFloor(MathLog(K0)/MathLog(2));
      ArrayInitialize(W,0.0);
      ArrayInitialize(R,0.0);
      ArrayInitialize(Wi,0.0);
      ArrayInitialize(Rst,0.0);
      ArrayInitialize(Rs,0.0);
      sumx=0;
      sumy=0;
      sumxy=0;
      sumx2=0;
      sumy2=0;
      for(i=1; i<=iter; i++) // i is the subdivision index in Ki blocks, higher-level index
        {
         d[i]=MathPow(2,i+1);             // d[i]=size of each block in cut "i"  
         K[i]=MathFloor(period/d[i]);     // K[i]=nber of blocks in cut "i"
         t=0;
         l=1;
         while(t<=period-d[i])
           {
            mu=0;
            for(j=1; j<=d[i]; j++)
              {
               mu+=PIP_Convertor*inputData[pos+t+j]/d[i];
              }
            sum=0;
            for(j=1; j<=d[i]; j++)
              {
               sum+=MathPow((PIP_Convertor*inputData[pos+t+j]-mu),2);
              }
            std=0;
            std=MathSqrt(sum/d[i]);
            if(std<=0)std=0.1;
            for(k=1; k<=d[i]; k++)
              {
               for(z=1; z<=k; z++)
                 {
                  W[i,k+t]+=PIP_Convertor*inputData[pos+t+z]-mu;
                 }
               Wi[k+t]=W[i,k+t];
              }
            max=_highest(d[i],t+1,Wi);
            min=_lowest(d[i],t+1,Wi);
            if(max<0)max=0;
            if(min>0)min=0;
            R[l]=max-min;
            Rst[l]=R[l]/std;
            t=t+d[i];
            l=l+1;
           }  //********************************END OF while LOOP ON t AND l AS INDEXES    
         for(m=1; m<=K[i]; m++)
           {
            Rs[i]+=Rst[m]/K[i];
           }
         sumx+=MathLog(d[i])/MathLog(2);
         sumy+=MathLog(Rs[i])/MathLog(2);
         sumx2+=MathPow((MathLog(d[i])/MathLog(2)),2);
         sumy2+=MathPow((MathLog(Rs[i])/MathLog(2)),2);
         sumxy+=(MathLog(d[i])/MathLog(2))*(MathLog(Rs[i])/MathLog(2));
        }        //********************************END OF i LOOP
      H1=(iter*sumxy-sumx*sumy);
      H2=iter*sumx2-MathPow(sumx,2);
      if(H2<=0)H2=0.1;
      H=H1/H2;
      if(2*H<=0)H=0.001;
      alpha=1/(2*H);
      speed=MathRound(normal_speed*alpha);
      ExtOutputBuffer[pos]=iMA(NULL,0,speed,0,0,0,pos);
     }           //*********************************END OF pos LOOP
  }
//+------------------------------------------------------------------+
//| FUNCTION : _highest                                              |
//| Search for the highest value in an array data                    |
//| In :                                                             |
//|    - n : find the highest on these n data                        |
//|    - pos : begin to search for from this index                   |
//|    - inputData : data array on which the searching for is done   |
//|                                                                  |
//| Return : the highest value                                       |                                                 |
//+------------------------------------------------------------------+
double _highest(int n,int pos,double &inputData[])
  {
   int length=pos+n;
   double highest=0.0;
//----
   for(int i=pos; i<length; i++)
     {
      if(inputData[i]>highest)highest=inputData[i];
     }
   return( highest );
  }
//+------------------------------------------------------------------+
//| FUNCTION : _lowest                                               |                                                                                                          ===+
//| Search for the lowest value in an array data                     |
//| In :                                                             |
//|    - n : find the hihest on these n data                         |
//|    - pos : begin to search for from this index                   |
//|    - inputData : data array on which the searching for is done   |
//|                                                                  |
//| Return : the highest value                                       |
//+------------------------------------------------------------------+
double _lowest(int n,int pos,double &inputData[])
  {
   int length=pos+n;
   double lowest=9999999999.0;
//----
   for(int i=pos; i<length; i++)
     {
      if(inputData[i]<lowest)lowest=inputData[i];
     }
   return( lowest );
  }
//+------------------------------------------------------------------+                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
