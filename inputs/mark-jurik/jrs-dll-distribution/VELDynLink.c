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

double output1C[100] ;

// define function prototype
typedef int (__stdcall * LPFVEL)(double *, double *, unsigned int, unsigned int) ;
/*
EXPORT int WINAPI VEL(	double * DataPtr, double * OutPtr, DWORD depth, DWORD length ) ;
*/
									

#define VELSUCCESS 0

void main(void)
{
   HINSTANCE hDLL;   // Handle to DLL
	LPFVEL    VEL;    // Function pointer
	int iRes ;
	
	// get handle to DLL module
	hDLL = LoadLibrary("JRS_32.DLL") ;
   if(hDLL != NULL) {
		printf("JRS_32.DLL loaded\n") ;
		
		// get pointer to VEL function
		VEL = (LPFVEL)GetProcAddress(hDLL, "VEL") ;
		if(!VEL) {
			FreeLibrary(hDLL) ;       
			printf("Function not found\n") ;
		}
		else {
			printf("Function found\n") ;
			
			// call VEL function
			iRes = (* VEL)(input1C, output1C, 10, 100) ;
			
			FreeLibrary(hDLL) ; 
			
			if(iRes == VELSUCCESS) {
				printf("VEL Successful.\n") ;

				// do something with processed data

			}
			else
				printf("VEL error %d\n", iRes) ;
		}
	}
   else 
		printf("DLL not loaded \n");
 
	return ;
}