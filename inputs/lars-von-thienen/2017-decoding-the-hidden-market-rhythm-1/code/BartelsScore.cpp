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

/*
	Example Call - Get Bartels Value
	
	//load inital data
	testdata2 : array of price values
	datapoints : length of testdata2 array
	cycle_length : cycle length to test for bartes score
	max_segments : how many segments should be tested (e.g. 5 segments are recommended)
	
	
	//prepare return values
  double bartelsvalue=0;
  double bartelssegmentspassed=0;
	
	//call the function
  GetBartelsScore(testdata2,datapoints,cycle_length,max_segments, bartelsvalue, bartelssegmentspassed);
*/

// --- START of Function GetBartelsScore ---
// -----------------------------------------
void GetBartelsScore(double dataset[], int datalength, double cyclelength, double maxsegments, double& return_bartels, double& return_segments)
{
   // Begin Bartes Test
   // -----------------
   double bartelsscore, segmentspassed;
   segmentspassed=0;
   bartelsscore=0;

   int datacounter=0;
   double A=0;
   double B=0;
   double SUM_A=0;
   double SUM_B=0;
   double SUM_A2B2=0;
   double bval=0;
   double SI=0;
   double CO=0;
   double bogenmass=0;


   bval=360/cyclelength;


  // Build Values for each Segment
  // -------------------------
   for (int x=0; x<datalength; x++)
   {
      bogenmass=(bval*(x+1))/180*3.1415926535;

      SI=sin(bogenmass)*dataset[x];
      CO=cos(bogenmass)*dataset[x];

      A=A+SI;
      B=B+CO;

      datacounter+=1;

      if ((datacounter==(int)cyclelength) && (segmentspassed<(int)maxsegments))
      {
         SUM_A=SUM_A+A;
         SUM_B=SUM_B+B;
         SUM_A2B2=SUM_A2B2+((A*A)+(B*B));

         segmentspassed+=1;
         datacounter=0;
         A=0;
         B=0;
      }
    }


  // ERROR CORRECTION IF NO SEGMENT WAS PASSED:
  if (segmentspassed==0)
  {
      return_bartels=0;
      return_segments=0;
  } else
  {
  // Calculate Bartels Value
  // -----------------------
    double SUM_A_Average=0;
    double SUM_B_Average=0;
    double SUM_A2B2_Average=0;
    double Amplitude=0;
    double Amplitude_A2B2=0;
    double a1=0;
    double b1=0;


    SUM_A_Average=SUM_A/segmentspassed;
    SUM_B_Average=SUM_B/segmentspassed;
    Amplitude=sqrt(((SUM_A_Average*SUM_A_Average)+(SUM_B_Average*SUM_B_Average)));

    SUM_A2B2_Average=SUM_A2B2/segmentspassed;
    Amplitude_A2B2=sqrt(SUM_A2B2_Average);

    a1=Amplitude_A2B2/sqrt(segmentspassed);
    b1=Amplitude/a1;

    bartelsscore=1/(exp((b1*b1)));

    // build return values
    return_bartels=bartelsscore;
    return_segments=segmentspassed;
  }

}
// --- END OF Function GetBartelsScore ---