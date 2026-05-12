#include <stdio.h>
#include <windows.h>

// This is a console application ...

double input1C[100] = {	69.688,70.188,70.156,70.375,70.344,70.688,70.500,70.438,71.469,71.438,
								71.388,71.250,71.219,71.063,71.156,71.125,70.906,70.813,70.938,71.406,
								71.250,70.906,70.781,70.688,70.500,70.063,69.719,69.875,70.031,69.938,
								69.406,68.906,68.750,68.000,68.375,68.031,67.813,68.219,68.125,68.531,
	                     68.063,67.813,67.219,67.094,67.063,67.125,66.938,66.813,66.781,66.563,
		                  66.031,66.219,66.250,66.156,66.188,66.438,66.344,66.750,66.938,66.219,
			               66.156,65.750,65.563,65.656,66.313,66.594,66.344,66.438,66.906,66.063,
				            65.625,65.906,65.188,64.938,64.906,65.250,65.375,61.438,61.281,61.844,
					         62.313,61.594,62.031,62.094,61.094,61.063,60.063,60.094,61.094,59.688,
						      59.250,59.469,60.906,61.719,61.688,61.156,60.875,61.125,60.594,60.875 } ;

double *outputMc ;

// define function prototype
typedef int (__stdcall * LPFWAV)(double *, double *, unsigned int, unsigned int, int) ;
typedef int (__stdcall * LPFWAVCols)(unsigned int, int) ;
/*
EXPORT int WINAPI WAV(double *pdData, double *pdOut, DWORD dwLength, DWORD dwNMIndex, int iMode);
EXPORT int WINAPI WAVCols(DWORD dwNMindex, int iMode) ;
*/
#define WAVSUCCESS 0

void main(void)
{
   HINSTANCE hDLL;   // Handle to DLL
	LPFWAV    WAV;    // Function pointer
	LPFWAVCols WAVCols ; // Function pointer
	int iRes, iCols, iRows, iIndex, iMode ;
	
	iRows = 100 ;
	iIndex = 12 ;
	iMode = 2 ;
		
	// get handle to DLL module
	hDLL = LoadLibrary("JRS_32.DLL") ;
   if(hDLL != NULL) {
		printf("JRS_32.DLL loaded\n") ;
		
		// get pointers to WAV functions
		WAV = (LPFWAV)GetProcAddress(hDLL, "WAV") ;
		WAVCols = (LPFWAVCols)GetProcAddress(hDLL, "WAVCols") ;
		if(!WAV || !WAVCols) {
			FreeLibrary(hDLL) ;       
			printf("Function not found\n") ;
		}
		else {
			printf("Functions found\n") ;

			// call WAVCols function
			iCols = (* WAVCols)(iIndex, iMode) ;		

			// allocate RAM for output Array
			outputMc = (double*) calloc(iRows*iCols, sizeof(double)) ;
			// check for out of RAM condition
			if(!outputMc) {
				FreeLibrary(hDLL) ; 
				printf("WAV Out of Memory Error %d\n") ;
				return ;
			}

			// call WAV function
			iRes = (* WAV)(input1C, outputMc, 100, iIndex, iMode) ;
			FreeLibrary(hDLL) ; 
			if(iRes == WAVSUCCESS) {
				printf("WAV Successful.\n") ;

				// do something with processed data

			}
			else
				printf("WAV error %d\n", iRes) ;
		}
	}
   else 
		printf("DLL not loaded \n");
 
	free(outputMc) ;

	return ;
}