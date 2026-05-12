#include <stdio.h>
#include <windows.h>

// This is a console application ...

// CAVEAT: The input array ppdInput2C is defined as a two dimensional array, but DDR expects
// to receive a pointer to a one dimensional array. Dereferencing the array name produces
// a pointer to double, and that works well in this example, BECAUSE the memory in the array 
// is contiguous. In other words the first element in row 2 is exactly one double after the 
// last element in row 1, etc. When dynamically allocating RAM you must allocate all the 
// required RAM so that it is contiguous i.e., as a one dimensional array.


double ppdInput2C[100][2] = { 69.688,	180.12,
									70.188,	179.34,
									70.156,	177.58,
									70.375,	175.59,
									70.344,	175.79,
									70.688,	177.46,
									70.500,	180.02,
									70.438,	180.54,
									71.469,	177.98,
									71.438,	176.51,
									71.388,	176.48,
									71.250,	176.36,
									71.219,	174.25,
									71.063,	178.48,
									71.156,	179.53,
									71.125,	178.86,
									70.906,	179.14,
									70.813,	180.74,
									70.938,	180.06,
									71.406,	180.24,
									71.250,	182.97,
									70.906,	183.43,
									70.781,	183.44,
									70.688,	178.98,
									70.500,	178.55,
									70.063,	176.32,
									69.719,	174.64,
									69.875,	173.52,
									70.031,	176.02,
									69.938,	171.26,
									69.406,	167.45,
									68.906,	159.13,
									68.750,	128.62,
									68.000,	133.04,
									68.375,	145.02,
									68.031,	139.45,
									67.813,	139.22,
									68.219,	127.88,
									68.125,	130.51,
									68.531,	130.31,
									68.063,	136.28,
									67.813,	140.80,
									67.219,	142.74,
									67.094,	140.11,
									67.063,	139.11,
									67.125,	141.81,
									66.938,	140.04,
									66.813,	136.35,
									66.781,	134.06,
									66.563,	135.46,
									66.031,	138.88,
									66.219,	137.60,
									66.250,	138.16,
									66.156,	136.21,
									66.188,	137.58,
									66.438,	134.72,
									66.344,	135.56,
									66.750,	136.13,
									66.938,	137.93,
									66.219,	136.90,
									66.156,	135.16,
									65.750,	129.69,
									65.563,	130.50,
									65.656,	131.21,
									66.313,	127.01,
									66.594,	125.91,
									66.344,	128.23,
									66.438,	131.42,
									66.906,	133.56,
									66.063,	131.07,
									65.625,	131.79,
									65.906,	135.26,
									65.188,	135.61,
									64.938,	138.34,
									64.906,	136.02,
									65.250,	139.15,
									65.375,	139.49,
									61.438,	139.54,
									61.281,	141.36,
									61.844,	140.85,
									62.313,	137.50,
									61.594,	136.84,
									62.031,	138.52,
									62.094,	138.23,
									61.094,	142.90,
									61.063,	144.54,
									60.063,	144.82,
									60.094,	145.89,
									61.094,	137.03,
									59.688,	138.81,
									59.250,	137.74,
									59.469,	137.95,
									60.906,	137.97,
									61.719,	141.16,
									61.688,	141.24,
									61.156,	140.13,
									60.875,	136.72,
									61.125,	136.97,
									60.594,	138.69,
									60.875,	141.51 } ;

double *output2C ;

// define function prototype
typedef int (__stdcall * LPFDDR)(double*,double*,unsigned int,unsigned int,double*,char*) ;
typedef int (__stdcall * LPFDDRUpdate)(char*,double*,double*,unsigned int,unsigned int) ;
/*
EXPORT int WINAPI DDR(double * pDataRef, double * pOutRef, DWORD dwRows, DWORD dwCols, 
								double * pdContrib, LPSTR sFileName) ;
EXPORT int WINAPI DDRUpdate(LPSTR szCofsFileName, double * pdResult, double * pdNewData, 
								DWORD dwColumn, DWORD dwCols) ;
*/

#define DDRSUCCESS 0

void main(void)
{
   HINSTANCE hDLL;   // Handle to DLL
	LPFDDR    DDR;    // Function pointer
	LPFDDRUpdate DDRUpdate ; // Function pointer
	int iRes ;
	unsigned int uiCols, uiRows ;
	double contrib[2] ;
	double value1=0, value2=0 ;
	double pdUpray1[2] = {69.688,	180.12} ;
	double pdUpray2[2] = {70.188,	179.34} ;

	uiRows = 100 ;
	uiCols = 2 ;
		
	// get handle to DLL module
	hDLL = LoadLibrary("JRS_32.DLL") ;
   if(hDLL != NULL) {
		printf("JRS_32.DLL loaded\n") ;
		
		// get pointers to DDR functions
		DDR = (LPFDDR)GetProcAddress(hDLL, "DDR") ;
		DDRUpdate = (LPFDDRUpdate)GetProcAddress(hDLL, "DDRUpdate") ;
		if(!DDR || !DDRUpdate) {
			FreeLibrary(hDLL) ;       
			printf("Function not found\n") ;
		}
		else {
			printf("Functions found\n") ;

			// allocate RAM for output Array
			output2C = (double*) calloc(uiRows*uiCols, sizeof(double)) ;
			// check for out of RAM condition
			if(!output2C) {
				FreeLibrary(hDLL) ;       
				printf("DDR Out of Memory Error %d\n") ;
				return ;
			}

			// call DDR function
			iRes = (* DDR)(*ppdInput2C, output2C, uiRows, uiCols, contrib, "COEFF.DDR") ;
			
			// call DDRUpdate function
			iRes += DDRUpdate("COEFF.DDR", &value1, pdUpray1, 0, 2) ;
			iRes += DDRUpdate("COEFF.DDR", &value2, pdUpray2, 1, 2) ;
			
			FreeLibrary(hDLL) ; 
			if(iRes==DDRSUCCESS) {
				printf("DDR Successful.\n") ;

				// do something with processed data

			}
			else
				printf("DDR error %d\n", iRes) ;
		}
	}
   else 
		printf("DLL not loaded \n");
 
	free(output2C) ;

	return ;
}