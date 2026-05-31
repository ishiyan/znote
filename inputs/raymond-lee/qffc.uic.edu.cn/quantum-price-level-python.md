# Quantum Price Level Calculation (python version)

- **Source:** <https://qffc.uic.edu.cn/home/content/index/pid/277/cid/7151.html>

---


## Quantum Price Level Calculation (python version)


Import packages


```python
import matplotlib.pyplot as plt

import pandas as pd

import numpy as np

import math

import datetime

import torch 

from torch import nn

from torch.autograd import Variable

import matplotlib.pyplot as plt
```


#### Load Data


```python
product = 'AUDUSD'

fileName = 'TS_data/'+'AUDUSD1440.csv'

ts = pd.read_csv(fileName,parse_dates=[0])

ts = ts.dropna(axis=0,how='any') 

#print(ts.isna().any())

print(ts.shape)

DT_CL = [i for i in ts.values[:,-2]] 

						DT_CL
					
							(2105, 7)
						
[0.91891,
 0.92285,
 0.9298,
 0.93314,
 0.9262600000000001,
 0.92438,
 0.9322,
 0.9317799999999999,
 0.9351299999999999,

...
					
						...
					
 0.7375,
 0.7407,
 0.7370800000000001,
 ...]
```


#### Calculate Price Return


```python
K = []

for eL in range(0,21):
    K.append(pow((1.1924 + (33.2383*eL) + (56.2169*eL*eL))/(1 + (43.6106 *eL)),1/3))
    print("Energy Level ",eL," K",eL," = ",K[eL]) 

						Energy Level  0  K 0  =  1.0604104260891232

Energy Level  1  K 1  =  1.2665998003610162

Energy Level  2  K 2  =  1.4911995005771048

Energy Level  3  K 3  =  1.6634993435845786

Energy Level  4  K 4  =  1.8060990099778986

Energy Level  5  K 5  =  1.929191563789632

Energy Level  6  K 6  =  2.0383229272127377

Energy Level  7  K 7  =  2.1368812897262184

Energy Level  8  K 8  =  2.2271052412903205

Energy Level  9  K 9  =  2.310559911129437

Energy Level  10  K 10  =  2.3883874710464883

Energy Level  11  K 11  =  2.4614499171710933

Energy Level  12  K 12  =  2.530415652563917

Energy Level  13  K 13  =  2.5958146503424806

Energy Level  14  K 14  =  2.658075047465853

Energy Level  15  K 15  =  2.717548251004358

Energy Level  16  K 16  =  2.7745266609153885

Energy Level  17  K 17  =  2.8292564903338833

Energy Level  18  K 18  =  2.8819472383042357

Energy Level  19  K 19  =  2.93277882031813

Energy Level  20  K 20  =  2.981907024619207
```


#### Calculate Price Return


```python
DT_RT = []

for d in range(0, ts.shape[0]-1):

if DT_CL[d+1] > 0:

DT_RT.append(DT_CL[d]/DT_CL[d+1])

else:

DT_RT.append(1)

#  Calculate the s\mu and std dev 

mu = np.mean(DT_RT)

sigma = np.std(DT_RT)

# Approximately dr

dr = (3 * sigma)/50

print(product+": mu =", mu, "; sigma = ", sigma," dr=",dr)

						AUDUSD: mu = 1.0001520172318046 ; sigma =  0.00563034244868513  dr= 0.00033782054692110776
```


#### Generate wave function


```python
auxR = 0

Q = [0 for i in range(100)] 

NQ = [0 for i in range(100)]

maxRno = len(DT_RT)

tQno = 0

nQ = 0

numOfRInQSlot = 0

for r in DT_RT:

bFound = False

nQ = 0

auxR = 1 - (dr * 50) # Left boundary

while ((bFound != True) and (nQ < 100)):

if r > auxR and r <= (auxR + dr):

Q[nQ]+=1

tQno+=1

bFound = True

else:

nQ+=1

auxR = auxR + dr

# Normalize

NQ = np.array(Q)/tQno

# Find MaxQ and index of MaxQ

maxQ = NQ.max()

maxQno = NQ.tolist().index(maxQ)

print(maxQno)

print("maxQ =", maxQ, "; maxQno=", maxQno, "; total number of Q =", tQno)

r=[]

for i in range(100):

r.append(1-50*dr+i*dr)

plt.title(product+" Wavefunction")

plt.bar([i for i in range(100)], NQ, alpha=0.6,width = 0.8)

					50

maxQ = 0.04331087584215592 ; maxQno= 50 ; total number of Q = 2078
```


#### Calculate Lambda L


```python
r0  = r[maxQno] - (dr/2)

r1  = r0 + dr

rn1 = r0 - dr

Lup = (pow(rn1,2)*NQ[maxQno-1])-(pow(r1,2)*NQ[maxQno+1])

Ldw = (pow(rn1,4)*NQ[maxQno-1])-(pow(r1,4)*NQ[maxQno+1])

L   = abs(Lup/Ldw)

print(product+":", " r0 = ",r0," r1 = ",r1," r-1 = ",rn1," Q0 = ",NQ[maxQno]," Q1 = ",NQ[maxQno+1]," Q-1 = ",NQ[maxQno-1]," L = Lup/Ldw = ",Lup,"/",Ldw," = ",L)

						print(product+"'s lambda = ", L)
					
						AUDUSD:  r0 =  0.9998310897265394  r1 =  1.0001689102734606  r-1 =  0.9994932691796183  Q0 =  0.04331087584215592  Q1 =  0.03849855630413859  Q-1 =  0.0370548604427334  L = Lup/Ldw =  -0.0014942467280006297 / -0.0015447639489677908  =  0.9672977732287728

AUDUSD's lambda =  0.9672977732287728
```


#### Calculate QPR


```python
QFEL = [0 for i in range(21)]

QPR = [0 for i in range(21)]

NQPR = [0 for i in range(21)]

# Cardano Method

for eL in range(0, 21):

p = -1 * pow((2*eL+1),2);

q = -1 * L * pow((2*eL+1),3) * pow(K[eL],3)

# Apply Cardano's Method to find the real root of the depressed cubic equation

u = pow((-0.5*q + math.sqrt(((q*q/4.0) + (p*p*p/27.0)))),1/3)

v = pow((-0.5*q - math.sqrt(((q*q/4.0) + (p*p*p/27.0)))),1/3)

QFEL[eL] = u+v

print(product+":", "Energy Level",eL," QFEL = ",QFEL[eL])

for eL in range(0, 21):

QPR[eL]  = QFEL[eL]/QFEL[0]

						NQPR[eL] = 1 + 0.21*sigma*QPR[eL]
					
						AUDUSD: Energy Level 0  QFEL =  1.3595491196477827

AUDUSD: Energy Level 1  QFEL =  4.546660186831538

AUDUSD: Energy Level 2  QFEL =  8.496416610049124

AUDUSD: Energy Level 3  QFEL =  12.928147353880194

AUDUSD: Energy Level 4  QFEL =  17.74980277460103

AUDUSD: Energy Level 5  QFEL =  22.904133519944605

AUDUSD: Energy Level 6  QFEL =  28.35133528907752

AUDUSD: Energy Level 7  QFEL =  34.061803912757995

AUDUSD: Energy Level 8  QFEL =  40.01248924070005

AUDUSD: Energy Level 9  QFEL =  46.18483576031768

AUDUSD: Energy Level 10  QFEL =  52.56352186712402

AUDUSD: Energy Level 11  QFEL =  59.13564037491598

AUDUSD: Energy Level 12  QFEL =  65.8901404508479

AUDUSD: Energy Level 13  QFEL =  72.81743314040682

AUDUSD: Energy Level 14  QFEL =  79.90910386980983

AUDUSD: Energy Level 15  QFEL =  87.1576974913583

AUDUSD: Energy Level 16  QFEL =  94.55655404371201

AUDUSD: Energy Level 17  QFEL =  102.09968090001858

AUDUSD: Energy Level 18  QFEL =  109.78165161593893

AUDUSD: Energy Level 19  QFEL =  117.597524755553

AUDUSD: Energy Level 20  QFEL =  125.54277792474099
```


#### Save QPL to file


```python
daily_stock_data['Open']

# Initialize two-dimensional array

P_QPL = [[0 for i in range(len(daily_stock_data['Open']))] for i in range(len(NQPR))]

N_QPL = [[0 for i in range(len(daily_stock_data['Open']))] for i in range(len(NQPR))]

#Calculate +QPL

for i in range(len(NQPR)):

for j in range(len(daily_stock_data['Open'])):

P_QPL[i][j]=daily_stock_data['Open'][j]*NQPR[i]

#Calculate -QPL

for i in range(len(NQPR)):

for j in range(len(daily_stock_data['Open'])):

N_QPL[i][j]=daily_stock_data['Open'][j]/NQPR[i]

P_QPL = pd.DataFrame(P_QPL)

N_QPL = pd.DataFrame(N_QPL)

P_QPL = pd.DataFrame(P_QPL.values.T, index=P_QPL.columns, columns=P_QPL.index)

N_QPL = pd.DataFrame(N_QPL.values.T, index=N_QPL.columns, columns=N_QPL.index)

daily_stock_data=pd.concat([daily_stock_data, P_QPL], axis=1)

daily_stock_data=pd.concat([daily_stock_data, N_QPL], axis=1)

new_index = ['Date','Time','Open','High','Low','Close','Volume','QPL1','QPL2','QPL3','QPL4','QPL5','QPL6','QPL7','QPL8','QPL9','QPL10',

'QPL11','QPL12','QPL13','QPL14','QPL15','QPL16','QPL17','QPL18','QPL19','QPL20','QPL21','QPL-1','QPL-2','QPL-3','QPL-4',

'QPL-5','QPL-6','QPL-7','QPL-8','QPL-9','QPL-10','QPL-11','QPL-12','QPL-13','QPL-14','QPL-15','QPL-16','QPL-17','QPL-18','QPL-19',

'QPL-20','QPL-21']

daily_stock_data.columns = new_index

daily_stock_data.to_csv('TS_data_with_QPL/'+product+'.csv',index=False)
```
