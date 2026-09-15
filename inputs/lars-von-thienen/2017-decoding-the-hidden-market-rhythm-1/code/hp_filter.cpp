// ---------------------------------------------------------------------------------
// Hodrick Prescott Filter
// used in the cycle detection framework from whentotrade.com for detrending
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
// -------- PARAMETER USAGE ----------
// ------- Input
// data   - Pointer to array of raw data 
// nobs   - Number of observations
// lambda - the HP smoothing parameter 
// ret    - true=trend will be returned; false=cyclical component will be returned  
// ------- Output
// output - Pointer to array where the filtered data will be stored. Must be the same length as data. 
// ------- Return value
// error codes
// ---------------------------------------------------------------------------------

int hp_filter(double *data, UINT nobs,double lambda, double *output, BOOL ret)
{
   double* a;
   double* b;
   double *c;
   register UINT  i=0;
   double H1=0;
   double H2=0;
   double H3=0;
   double H4=0;
   double H5=0;
   double HH1=0;
   double HH2=0;
   double HH3=0;
   double HH4=0;
   double HH5=0;
   double Z;
   double HB;
   double HC;

   /* check if we have enough data nobs >5 */
   if (nobs <= 5) return 1;

   /* write into HEAP */
   a = (double *) calloc(nobs, sizeof(double));
   b = (double *) calloc(nobs, sizeof(double)) ;
   c = (double *) calloc(nobs, sizeof(double));

   /* check for memory issues */
   if (a == NULL || b == NULL || c == NULL) return 2;

   /* prepare output array */
   for(i=0;i<nobs;i++) output[i]=data[i];

   /* build coeff matrix */
   a[0]=1.0+lambda;
   b[0]=-2.0*lambda;
   c[0]=lambda;

   for(i=1;i<nobs-2;i++)
   {
	   a[i]=6.0*lambda+1;
	   b[i]=-4.0*lambda;
	   c[i]=lambda;
   }
   
   a[1]=5.0*lambda+1;
   a[nobs-1]=1.0+lambda;
   a[nobs-2]=5.0*lambda+1.0;

   b[nobs-2]=-2.0*lambda;
   b[nobs-1]=0.0;
   c[nobs-2]=0.0;
   c[nobs-1]=0.0;

   /* forward calc */
   for (i=0;i<nobs;i++)
	{
		Z=a[i]-H4*H1-HH5*HH2;
		if (Z==0) return 3;
		HB=b[i];
		HH1=H1;
		H1=(HB-H4*H2)/Z;
		b[i]=H1;
		HC=c[i];
		HH2=H2;
		H2=HC/Z;
		c[i]=H2;
		a[i]=(output[i]-HH3*HH5-H3*H4)/Z;
		HH3=H3;
		H3=a[i];
		H4=HB-H5*HH1;
		HH5=H5;
		H5=HC;
	}

	/* backward calc */
	H2=0;
	H1=a[nobs-1];
	output[nobs-1]=H1;

	for (i=nobs-1;i>0;i--)
	{
		output[i-1]=a[i-1]-b[i-1]*H1-c[i-1]*H2;
		H2=H1;
		H1=output[i-1];
	}

	 /* Return trend oder cyclical component ? */
   if (ret==FALSE) for(i=0;i<nobs;i++) output[i]=data[i]-output[i];

   /* cleanup */
   free(a);
   free(b);
   free(c);

   return 0;
}