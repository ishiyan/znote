# WAV 2.0 — Historical Sampling Filter DLL Module

User's Guide for Windows Application Developers

© 1994–2002 Jurik Research & Consulting

## BibTeX

```bibtex
@manual{jurik_wav_dll,
  title        = {WAV 2.0: Historical Sampling Filter DLL Module for Windows Application Developers — User's Guide},
  author       = {{Jurik Research}},
  year         = {2002},
  organization = {Jurik Research & Consulting},
  address      = {PO 460669, Aurora, CO 80046},
}
```

## Requirements

- Windows 95, 98, 2000 or NT 4.
- Application software that can access DLL functions.

## Installing the 32-bit DLL Module

1. Execute the Installer, `JRS_DLL.EXE`. It will analyze your computer and give you a computer identification number. Write it down.
2. Get your access PASSWORD from Jurik Research Software. You can do so by calling 323-258-4860 (USA), faxing 323-258-0598 (USA), e-mailing support@nfsmith.net, or writing Jurik Research Software at 686 South Arroyo Parkway, Suite 237, Pasadena, California 91105.
3. Rerun the installer `JRS_DLL.EXE`, this time entering the password when asked. Also enter all the Jurik Research modules that you currently are licensed to run.

### About New Passwords

If you upgrade to a new computer, you will need a new password to run WAV. If you want to run WAV on additional computers, you will need additional passwords. Call 323-258-4860 for details.

## Why Use WAV?

### Brief Description

If you are building a model whereby each data fact-record needs historical values of a time series and you can arrange the time series in a spreadsheet, then the Historical Data Wavelet Sampler, WaveSamp, is for you. When the original time series is arranged as a single column on a spreadsheet, WaveSamp adds additional columns such that within any row the additional cells look farther into the past as you progress from left to right. The wavelet sampling algorithm filters and samples the time series to efficiently squeeze short, medium and long term information into a very small number of columns for your forecasting or financial trading system.

### Background

If you buy stock at today's market price, the price will already reflect long term fundamental factors. Variations in price (the source of profit making) are to a large degree due to changes in its perceived value. However, perception is partly emotional and thus partly unpredictable, giving trade prices a chaotic appearance. Despite this, a certain amount of predictability does exist provided you have all the necessary information to make such a prediction.

A simple modification to a series of prices is to produce its moving average. The moving average serves to filter out chaotic "noise" in the day-to-day prices, leaving a smooth trend line. A simple short term buy/sell policy might be to buy immediately when the price rises above its moving average (and sell later on) or to sell immediately when the price falls below its moving average (and buy later on).

### The Key Issue

Market oscillations between being overbought and oversold are due, in part, to a kind of psychological momentum that tends to persist despite changes in market conditions. Each market has its own time-varying momentum (TVM), and these TVMs influence each other. Many TVMs, with different cycle lengths, may be driving the market you wish to forecast.

For a trading system to work properly, it must have the right historical samples for detecting all possible TVMs affecting the market you wish to trade. Although slow cycle TVMs may be sampled slowly (once per month), fast cycles must be sampled quickly (once per day). The big question is: what is the best spread of samples in a financial time series when you do not have a clue about which TVMs are driving the market?

### Breakthrough: Wavelet Sampling

Proper sampling of the market line requires getting just enough samples for detecting presence of the slow waveform, and just enough for detecting the medium-slow waveform, and just enough for all the other waveforms too. The sampling points get increasingly farther apart the further into history you sample.

## Fundamentals of WAV Operation

Consider 5 horizontal rows of little squares (A through E). Let the last square in row A represent the S&P daily value on the last day of the year 1993. Thus row A is a time-series of prices.

- Row A: To capture fast cycles, every day's price must be sampled for the last four days.
- Row B: To capture a slower cycle, every other day is sampled.
- Rows C, D, E: Slower cycles are sampled successively.
- Row F: Combine all the days that need to be sampled into one row.

This is a very efficient way to determine on which days the S&P price needs to be sampled to cover all possible cycle speeds with the least number of samples.

WaveSamp does more than merely sample historical prices. A single sample 32 days ago would not be very meaningful since such a sample would ignore data on all the days surrounding it. That's why WaveSamp filters the time-series before sampling it. The special filtering method forces every sample to contain information about a block of data points on both sides of the sample.

## The INDEX Table

| Index | N | Max. Distance |
|-------|---|---------------|
| 1 | 1 | 1 |
| 2 | 2 | 2 |
| 3 | 3 | 3 |
| 4 | 4 | 4 |
| 5 | 5 | 5 |
| 6 | 7 | 8 |
| 7 | 10 | 11 |
| 8 | 14 | 16 |
| 9 | 19 | 21 |
| 10 | 26 | 30 |
| 11 | 35 | 39 |
| 12 | 48 | 56 |
| 13 | 65 | 73 |
| 14 | 90 | 106 |
| 15 | 123 | 139 |
| 16 | 172 | 204 |
| 17 | 237 | 269 |
| 18 | 334 | 398 |

The column labeled "max. distance" indicates the farthest distance into the historical past that WaveSamp will sample for a specified value of N.

Example: if you decide that an accurate forecast requires sampling up to the previous 135 days, select the next highest number from the "max. distance" column (139). The corresponding INDEX would be 15.

## The Output Array

The WAV DLL accepts the original time series as input and returns an array of data, whose number of rows is the same as the number of elements in the original time series. The number of columns in the output array depends on two factors: the user-selectable INDEX and the user-selectable MODE of operation.

When MODE is set to "Standard", the total number of columns in the output array equals the INDEX value. Each column is assigned a value for N, starting with N=1 and increasing per Table 1.

For each element in the input time series, WAV outputs a row of data into the output array. Output in column *k* is delayed by the "max. distance" value for that column's N. Rows that are not completely filled are zeroed out.

## Estimating the INDEX Value

We recommend the following heuristic: set WAV's maximum historical distance to be at least four times the forecast horizon. For example, if you want to predict 8 rows into the future, then you need historical information spanning 8×4 = 32 rows into the past. According to Table 1, this requires setting INDEX to 11.

## Selecting the Appropriate Columns

One elegant property of wavelet sampling is its invariance to scale. Whether you want to forecast 4 days ahead or 40 days ahead, we recommend using only 8 of the columns produced by WaveSamp. The only difference is the actual columns selected.

For a forecast model predicting 8 rows ahead (forecast horizon = 8), the recommended INDEX value is 11. This produces 11 columns, of which you really only need to feed the last 8 to your forecast model.

| Forecast Horizon | Recommended Columns (INDEX range) |
|-----------------|----------------------------------|
| 1–4 | INDEX 1–8 |
| 5 | INDEX 2–9 |
| 6–7 | INDEX 3–10 |
| 8–9 | INDEX 4–11 |
| 10–14 | INDEX 5–12 |
| 15–18 | INDEX 6–13 |
| 19–26 | INDEX 7–14 |
| 27–34 | INDEX 8–15 |
| 35–51 | INDEX 9–16 |
| 52–67 | INDEX 10–17 |
| 69–100 | INDEX 11–18 |

The user is not constrained to employ only 8 columns. As many or as few as desired may be used (provided there is enough historical data to support the lookbacks).

## Modes of Operation

WAV offers three different modes to process your data:

### 1. Standard

Designed to sample signals that do not have any long term trend. These signals include oscillators, stochastics, and Nth order derivatives. The total number of columns produced equals INDEX.

### 2. Detrend

Produces INDEX+1 columns. The first additional column is a detrended version of the input time series. The remaining INDEX columns are the result of applying WAV to this detrended time series.

Designed to sample signals that wander over long periods of time (e.g. prices that tend to increase by market inflation). WaveSamp cancels out the long term trend, causing the resulting values to fluctuate around zero.

Available INDEX values: 10–18 (strongly recommend no lower than 12).

### 3. Detrend & Normalize

Produces INDEX+1 columns. The first additional column is a detrended and normalized version of the input time series. The remaining INDEX columns are the result of applying WAV to this modified time series.

The detrended input signal's amplitude is continuously rescaled to attain uniform strength over the entire time series. For example, if during the past 5 years the price of T-Bonds was especially volatile during a 2-year period, automatic scale normalization would scale down the price activity during that time.

Available INDEX values: 12–18 (strongly recommend no lower than 14).

### Total Columns Produced

| Mode | Number of Columns |
|------|-------------------|
| Standard | INDEX |
| Detrend | INDEX + 1 |
| Detrend/Normalize | INDEX + 1 |

## C Programming the 32-bit WAV DLL

The file `JRS_32.DLL` contains the functions `WAV` and `WAVcols`.

### WAV Function

```c
extern _declspec(dllimport) int WINAPI WAV( double *pdData, double *pdOut, DWORD dwLength,
DWORD dwINDEX, int iMode ) ;
```

#### Parameters

| Parameter | Description |
|-----------|-------------|
| `pdData` | Pointer to double specifying the memory location of the first cell in the input array. |
| `pdOut` | Pointer to double specifying the memory location of the first cell in the output array. Memory must be allocated by the caller, sized to contain (rows × columns) double precision numbers. Do not pass a two-dimensional array (pointer to pointer); pass the address of the first element. |
| `dwLength` | DWORD indicating the number of rows of data in the input array. |
| `dwINDEX` | DWORD specifying the INDEX value. |
| `iMode` | INT specifying the mode: 1 = Standard, 2 = Detrend, 3 = Detrend+Normalize. |

### WAVCols Function

```c
extern _declspec(dllimport) int WINAPI WAVCols( DWORD dwINDEX, int iMode ) ;
```

Returns the number of columns required for WAV's output array.

### Detailed Instructions

**Input Array:** Allocate memory for your original data array (a single column vector of doubles):

```c
int length = 1200 ;
DataPtr = (double *) GlobalAllocPtr( GHND, sizeof(double) * length ) ;
```

**Output Array:** Determine required columns then allocate:

```c
iMode = 2 ;
length = 1200 ;
dwINDEX = 12 ;
OutCols = WAVCols ( dwINDEX , iMode ) ;
OutPtr = (double *) GlobalAllocPtr ( GHND, length*OutCols * sizeof(double) ) ;
```

### Error Codes

| Code | Meaning |
|------|---------|
| 0 | No error |
| -1 | Problem with password/installation |
| 10001 | Pointer to data is NULL |
| 10002 | Pointer to output memory is NULL |
| 10003 | Mode parameter not between 1 and 3 inclusive |
| 10004 | Index parameter outside min and max values |
| 10005 | Not enough data rows for selected value of Index |
| 10006 | Index must be at least 10 if Mode is 2 |
| 10007 | Index must be at least 12 if Mode is 3 |

## Visual Basic Programming Example

### Introduction

In your Jurik Research DLL installation directory (e.g., `C:\JRS_DLL`) the workbook `WAV_DLL.XLS` contains a working example of how to use Excel's VBA to operate WAV automatically. The workbook includes:

- Worksheet "DLL VBA Results" — where you can apply the Visual Basic macro that calls the DLL
- Worksheet "Excel add-in Results" — containing the results of running the WAV for Excel add-in product
- Visual Basic Module — containing the VB macro code

### Declarations

```vb
Declare Function WAV Lib "JRS_32.dll" ( _
                            ByRef daData As Double, _
                            ByRef pdOut As Double, _
                            ByVal dwLength As Long, _
                            ByVal dwINDEX As Long, _
                            ByVal iMode As Long) As Long

Declare Function WAVCols Lib "JRS_32.dll" ( _
                            ByVal dwINDEX As Long, _
                            ByVal iMode As Long) As Long
```

### Example

```vb
Sub WAV_Test()
    Dim k As Long
    Dim i As Long
    Dim iResult As Long
    Dim dwLength As Long
    Dim dwNMIndex As Long
    Dim TotCols As Long
    Dim OutCells As Long
    Dim RowOffset As Long
    Dim iMode As Long
    Dim calctype As Long

    ' iMode determines output type
    '       1   standard
    '       2   detrended
    '       3   detrended/normalized

    Dim InputData(1 To 199) As Double
    Dim OutputData() As Double

    'disable automatic calculation
    calctype = Application.Calculation
    Application.Calculation = xlManual

    dwLength = 199        ' input has 199 elements
    dwNMIndex = 12        ' set INDEX = 12

    ' Read Data from spreadsheet into array
    ' Input data is in column 1
    For k = 1 To dwLength
        InputData(k) = Cells(k + 1, 1)
    Next k

    ' *** Create the standard mode output ***
    iMode = 1

    ' redimension output array to be large enough
    TotCols = WAVCols(dwNMIndex, iMode)
    OutCells = TotCols * dwLength
    ReDim OutputData(1 To OutCells) As Double

    iResult = WAV(InputData(1), OutputData(1), dwLength, dwNMIndex, iMode)

    If iResult <> 0 Then
        Call Error_handler(iResult, calctype)
    Else
        ' Show results in columns 5+ on spreadsheet
        For i = 1 To TotCols
            RowOffset = 0
            For k = 1 To dwLength
                Cells(1 + k, 4 + i).FormulaR1C1 = OutputData(RowOffset + i)
                RowOffset = RowOffset + TotCols
            Next k
        Next i
    End If

    'enable automatic calculation
    Application.Calculation = calctype
End Sub

Private Sub Error_handler(ByVal error_code As Long, ByVal calctype As Long)
    Dim result As Long
    result = MsgBox("Error number " & Str(error_code) & " was returned by WAV.", , "WAV Error")
    Application.Calculation = calctype
    End
End Sub
```
