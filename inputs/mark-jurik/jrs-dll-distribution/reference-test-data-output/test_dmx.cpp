#include <stdio.h>
#include <windows.h>

// This is a console application ...

#define LEN 252
#define L1 6
#define L2 42

double input1C[LEN] = {
91.5000,
94.8150,
94.3750,
95.0950,
93.7800,
94.6250,
92.5300,
92.7500,
90.3150,
92.4700,
96.1250,
97.2500,
98.5000,
89.8750,
91.0000,
92.8150,
89.1550,
89.3450,
91.6250,
89.8750,
88.3750,
87.6250,
84.7800,
83.0000,
83.5000,
81.3750,
84.4400,
89.2500,
86.3750,
86.2500,
85.2500,
87.1250,
85.8150,
88.9700,
88.4700,
86.8750,
86.8150,
84.8750,
84.1900,
83.8750,
83.3750,
85.5000,
89.1900,
89.4400,
91.0950,
90.7500,
91.4400,
89.0000,
91.0000,
90.5000,
89.0300,
88.8150,
84.2800,
83.5000,
82.6900,
84.7500,
85.6550,
86.1900,
88.9400,
89.2800,
88.6250,
88.5000,
91.9700,
91.5000,
93.2500,
93.5000,
93.1550,
91.7200,
90.0000,
89.6900,
88.8750,
85.1900,
83.3750,
84.8750,
85.9400,
97.2500,
99.8750,
104.9400,
106.0000,
102.5000,
102.4050,
104.5950,
106.1250,
106.0000,
106.0650,
104.6250,
108.6250,
109.3150,
110.5000,
112.7500,
123.0000,
119.6250,
118.7500,
119.2500,
117.9400,
116.4400,
115.1900,
111.8750,
110.5950,
118.1250,
116.0000,
116.0000,
112.0000,
113.7500,
112.9400,
116.0000,
120.5000,
116.6200,
117.0000,
115.2500,
114.3100,
115.5000,
115.8700,
120.6900,
120.1900,
120.7500,
124.7500,
123.3700,
122.9400,
122.5600,
123.1200,
122.5600,
124.6200,
129.2500,
131.0000,
132.2500,
131.0000,
132.8100,
134.0000,
137.3800,
137.8100,
137.8800,
137.2500,
136.3100,
136.2500,
134.6300,
128.2500,
129.0000,
123.8700,
124.8100,
123.0000,
126.2500,
128.3800,
125.3700,
125.6900,
122.2500,
119.3700,
118.5000,
123.1900,
123.5000,
122.1900,
119.3100,
123.3100,
121.1200,
123.3700,
127.3700,
128.5000,
123.8700,
122.9400,
121.7500,
124.4400,
122.0000,
122.3700,
122.9400,
124.0000,
123.1900,
124.5600,
127.2500,
125.8700,
128.8600,
132.0000,
130.7500,
134.7500,
135.0000,
132.3800,
133.3100,
131.9400,
130.0000,
125.3700,
130.1300,
127.1200,
125.1900,
122.0000,
125.0000,
123.0000,
123.5000,
120.0600,
121.0000,
117.7500,
119.8700,
122.0000,
119.1900,
116.3700,
113.5000,
114.2500,
110.0000,
105.0600,
107.0000,
107.8700,
107.0000,
107.1200,
107.0000,
91.0000,
93.9400,
93.8700,
95.5000,
93.0000,
94.9400,
98.2500,
96.7500,
94.8100,
94.3700,
91.5600,
90.2500,
93.9400,
93.6200,
97.0000,
95.0000,
95.8700,
94.0600,
94.6200,
93.7500,
98.0000,
103.9400,
107.8700,
106.0600,
104.5000,
105.0000,
104.1900,
103.0600,
103.4200,
105.2700,
111.8700,
116.0000,
116.6200,
118.2800,
113.3700,
109.0000,
109.7000,
109.2500,
107.0000,
109.1900,
110.0000,
109.2000,
110.1200,
108.0000,
108.6200,
109.7500,
109.8100,
109.0000,
108.7500,
107.8700
};

double input1L[LEN] = {
 90.75,  
 91.405, 
 94.25,  
 93.5,   
 92.815, 
 93.5,   
 92,     
 89.75,  
 89.44,  
 90.625, 
 92.75,  
 96.315, 
 96.03,  
 88.815, 
 86.75,  
 90.94,  
 88.905, 
 88.78,  
 89.25,  
 89.75,  
 87.5,   
 86.53,  
 84.625, 
 82.28,  
 81.565, 
 80.875, 
 81.25,  
 84.065, 
 85.595, 
 85.97,  
 84.405, 
 85.095, 
 85.5,   
 85.53,  
 87.875, 
 86.565, 
 84.655, 
 83.25,  
 82.565, 
 83.44,  
 82.53,  
 85.065, 
 86.875, 
 88.53,  
 89.28,  
 90.125, 
 90.75,  
 89,     
 88.565, 
 90.095, 
 89,     
 86.47,  
 84,     
 83.315, 
 82,     
 83.25,  
 84.75,  
 85.28,  
 87.19,  
 88.44,  
 88.25,  
 87.345, 
 89.28,  
 91.095, 
 89.53,  
 91.155, 
 92,     
 90.53,  
 89.97,  
 88.815, 
 86.75,  
 85.065, 
 82.03,  
 81.5,   
 82.565, 
 96.345, 
 96.47,  
 101.155,
 104.25, 
 101.75, 
 101.72, 
 101.72, 
 103.155,
 105.69, 
 103.655,
 104,    
 105.53, 
 108.53, 
 108.75, 
 107.75, 
 117,    
 118,    
 116,    
 118.5,  
 116.53, 
 116.25, 
 114.595,
 110.875,
 110.5,  
 110.72, 
 112.62, 
 114.19, 
 111.19, 
 109.44, 
 111.56, 
 112.44, 
 117.5,  
 116.06, 
 116.56, 
 113.31, 
 112.56, 
 114,    
 114.75, 
 118.87, 
 119,    
 119.75, 
 122.62, 
 123,    
 121.75, 
 121.56, 
 123.12, 
 122.19, 
 122.75, 
 124.37, 
 128,    
 129.5,  
 130.81, 
 130.63, 
 132.13, 
 133.88, 
 135.38, 
 135.75, 
 136.19, 
 134.5,  
 135.38, 
 133.69, 
 126.06, 
 126.87, 
 123.5,  
 122.62, 
 122.75, 
 123.56, 
 125.81, 
 124.62, 
 124.37, 
 121.81, 
 118.19, 
 118.06, 
 117.56, 
 121,    
 121.12, 
 118.94, 
 119.81, 
 121,    
 122,    
 124.5,  
 126.56, 
 123.5,  
 121.25, 
 121.06, 
 122.31, 
 121,    
 120.87, 
 122.06, 
 122.75, 
 122.69, 
 122.87, 
 125.5,  
 124.25, 
 128,    
 128.38, 
 130.69, 
 131.63, 
 134.38, 
 132,    
 131.94, 
 131.94, 
 129.56, 
 123.75, 
 126,    
 126.25, 
 124.37, 
 121.44, 
 120.44, 
 121.37, 
 121.69, 
 120,    
 119.62, 
 115.5,  
 116.75, 
 119.06, 
 119.06, 
 115.06, 
 111.06, 
 113.12, 
 110,    
 105,    
 104.69, 
 103.87, 
 104.69, 
 105.44, 
 107,    
 89,     
 92.5,   
 92.12,  
 94.62,  
 92.81,  
 94.25,  
 96.25,  
 96.37,  
 93.69,  
 93.5,   
 90,     
 90.19,  
 90.5,   
 92.12,  
 94.12,  
 94.87,  
 93,     
 93.87,  
 93,     
 92.62,  
 93.56,  
 98.37,  
 104.44, 
 106,    
 101.81, 
 104.12, 
 103.37, 
 102.12, 
 102.25, 
 103.37, 
 107.94, 
 112.5,  
 115.44, 
 115.5,  
 112.25, 
 107.56, 
 106.56, 
 106.87, 
 104.5,  
 105.75, 
 108.62, 
 107.75, 
 108.06, 
 108,    
 108.19, 
 108.12, 
 109.06, 
 108.75, 
 108.56, 
 106.62
};

double input1H[LEN] = {
 93.25,  
 94.94,  
 96.375, 
 96.19,  
 96,     
 94.72,  
 95,     
 93.72,  
 92.47,  
 92.75,  
 96.25,  
 99.625, 
 99.125, 
 92.75,  
 91.315, 
 93.25,  
 93.405, 
 90.655, 
 91.97,  
 92.25,  
 90.345, 
 88.5,   
 88.25,  
 85.5,   
 84.44,  
 84.75,  
 84.44,  
 89.405, 
 88.125, 
 89.125, 
 87.155, 
 87.25,  
 87.375, 
 88.97,  
 90,     
 89.845, 
 86.97,  
 85.94,  
 84.75,  
 85.47,  
 84.47,  
 88.5,   
 89.47,  
 90,     
 92.44,  
 91.44,  
 92.97,  
 91.72,  
 91.155, 
 91.75,  
 90,     
 88.875, 
 89,     
 85.25,  
 83.815, 
 85.25,  
 86.625, 
 87.94,  
 89.375, 
 90.625, 
 90.75,  
 88.845, 
 91.97,  
 93.375, 
 93.815, 
 94.03,  
 94.03,  
 91.815, 
 92,     
 91.94,  
 89.75,  
 88.75,  
 86.155, 
 84.875, 
 85.94,  
 99.375, 
 103.28, 
 105.375,
 107.625,
 105.25, 
 104.5,  
 105.5,  
 106.125,
 107.94, 
 106.25, 
 107,    
 108.75, 
 110.94, 
 110.94, 
 114.22, 
 123,    
 121.75, 
 119.815,
 120.315,
 119.375,
 118.19, 
 116.69, 
 115.345,
 113,    
 118.315,
 116.87, 
 116.75, 
 113.87, 
 114.62, 
 115.31, 
 116,    
 121.69, 
 119.87, 
 120.87, 
 116.75, 
 116.5,  
 116,    
 118.31, 
 121.5,  
 122,    
 121.44, 
 125.75, 
 127.75, 
 124.19, 
 124.44, 
 125.75, 
 124.69, 
 125.31, 
 132,    
 131.31, 
 132.25, 
 133.88, 
 133.5,  
 135.5,  
 137.44, 
 138.69, 
 139.19, 
 138.5,  
 138.13, 
 137.5,  
 138.88, 
 132.13, 
 129.75, 
 128.5,  
 125.44, 
 125.12, 
 126.5,  
 128.69, 
 126.62, 
 126.69, 
 126,    
 123.12, 
 121.87, 
 124,    
 127,    
 124.44, 
 122.5,  
 123.75, 
 123.81, 
 124.5,  
 127.87, 
 128.56, 
 129.63, 
 124.87, 
 124.37, 
 124.87, 
 123.62, 
 124.06, 
 125.87, 
 125.19, 
 125.62, 
 126,    
 128.5,  
 126.75, 
 129.75, 
 132.69, 
 133.94, 
 136.5,  
 137.69, 
 135.56, 
 133.56, 
 135,    
 132.38, 
 131.44, 
 130.88, 
 129.63, 
 127.25, 
 127.81, 
 125,    
 126.81, 
 124.75, 
 122.81, 
 122.25, 
 121.06, 
 120,    
 123.25, 
 122.75, 
 119.19, 
 115.06, 
 116.69, 
 114.87, 
 110.87, 
 107.25, 
 108.87, 
 109,    
 108.5,  
 113.06, 
 93,     
 94.62,  
 95.12,  
 96,     
 95.56,  
 95.31,  
 99,     
 98.81,  
 96.81,  
 95.94,  
 94.44,  
 92.94,  
 93.94,  
 95.5,   
 97.06,  
 97.5,   
 96.25,  
 96.37,  
 95,     
 94.87,  
 98.25,  
 105.12, 
 108.44, 
 109.87, 
 105,    
 106,    
 104.94, 
 104.5,  
 104.44, 
 106.31, 
 112.87, 
 116.5,  
 119.19, 
 121,    
 122.12, 
 111.94, 
 112.75, 
 110.19, 
 107.94, 
 109.69, 
 111.06, 
 110.44, 
 110.12, 
 110.31, 
 110.44, 
 110,    
 110.75, 
 110.5,  
 110.5,  
 109.5
};

double output1B[LEN];
double output1P[LEN];
double output1M[LEN];


// define function prototype
typedef int (__stdcall * LPFDMX)(double *, double *, double *, double *, double *, double *, double, int);
/*
EXPORT int WINAPI DMX(double *pdInHigh, double *pdInLow, double *pdInClose, double *pdOutBipolar, double *pdOutPlus, double *pdOutMinus, double dLength, int iSize);
*/
									
#define DMXSUCCESS 0

void print_output(void) {
	printf("//---------------------------\n");
	printf("// output: bipolar\n");
	printf("//---------------------------\n");
	int i0 = 0;
	for  (int i=0; i<L2; i++)
	{
		for (int j=0; j <L1; j++) {
			printf(" %.15f,", output1B[i0+j]); 
		}
		i0 += L1;
		printf("\n");
	}
	printf("//---------------------------\n");
	printf("// output: plus\n");
	printf("//---------------------------\n");
	i0 = 0;
	for  (int i2=0; i2<L2; i2++)
	{
		for (int j2=0; j2 <L1; j2++) {
			printf(" %.15f,", output1P[i0+j2]); 
		}
		i0 += L1;
		printf("\n");
	}
	printf("//---------------------------\n");
	printf("// output: minus\n");
	printf("//---------------------------\n");
	i0 = 0;
	for  (int i3=0; i3<L2; i3++)
	{
		for (int j3=0; j3 <L1; j3++) {
			printf(" %.15f,", output1M[i0+j3]); 
		}
		i0 += L1;
		printf("\n");
	}
	printf("//---------------------------\n");
}

void main(void)
{
	HINSTANCE hDLL;   // Handle to DLL
	LPFDMX    DMX;    // Function pointer
	int iRes;

	// get handle to DLL module
	hDLL = LoadLibraryA("JRS_32.DLL");
	if (hDLL != NULL) {
		printf("// JRS_32.DLL loaded\n");

		// get pointer to JMA function
		DMX = (LPFDMX)GetProcAddress(hDLL, "DMX");
		if (!DMX) {
			FreeLibrary(hDLL);
			printf("// DMX function not found\n");
		}
		else {
			printf("// DMX function found\n");

			// call DMX function
			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 2, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=2\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 3, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=3\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 4, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=4\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 5, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=5\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 6, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=6\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 7, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=7\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 8, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=8\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 9, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=9\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 10, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=10\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 11, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=11\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 12, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=12\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 13, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=13\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 14, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=14\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 15, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=15\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 16, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=16\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 17, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=17\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 18, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=18\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 19, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=19\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			iRes = (*DMX)(input1H, input1L, input1C, output1B, output1P, output1M, 20, LEN);
			if (iRes == DMXSUCCESS) {
				printf("// DMX Successful.\n");
				printf("/////////////////////////////\n");
				printf("// depth=20\n");
				printf("/////////////////////////////\n");
				print_output();
			}
			else
				printf("// DMX error %d\n", iRes);

			FreeLibrary(hDLL);
			printf("// Completed \n");
		}
	}
	else
		printf("// JRS_32.DLL not loaded \n");

	return;
}
