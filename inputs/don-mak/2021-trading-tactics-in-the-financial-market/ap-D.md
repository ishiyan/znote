# Appendix D: MATLAB Programs


## D.1 accelosc


```matlab
%accelosc,

Plot Amplitude and Phase of accelerator oscillator

% unwrap phase,

Find Sure and Unsure Profit Zones

clear
NN=240; %240
intomega=pi/NN;
M1=5;

M2=34;

for I= 1: NN+1
omegavector(I) = (I-1)*intomega;

H1vector(I)=1/M1*( 1- exp(-i*M1*omegavector(I)) ) /( 1 exp(-i*omegavector(I) ) );
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));

H2vector(I)= 1/M2*( 1- exp(-i*M2*omegavector(I)) ) /( 1 exp(-i*omegavector(I) ) );
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));

H3vector(I)= H1vector(I) - H2vector(I); % awesome oscillator

mag3(I)=abs(H3vector(I));
phase3(I)= angle(H3vector(I));
H5vector(I) = H1vector(I) *H3vector(I); % SMA(5)*awesome oscillator

mag5(I)=abs(H5vector(I));
phase5(I)= angle(H5vector(I));
H6vector(I) = H3vector(I) - H5vector(I); % accelerator oscillator
(AC)
mag6(I)=abs(H6vector(I));
phase6(I)= angle(H6vector(I));
end
mag(1) = 1;
phase1(1) = 0;
mag2(1) = 1;
phase2(1) = 0;
mag3(1) = 0;
phase3(1) = pi/2;
mag5(1) = 0;
phase5(1) = pi/2;
mag6(1) = 0;
phase6(1) = pi;
phase6unwrap = unwrap(phase6);
for I= 1: NN+1
barlag(I) = phase6unwrap(I)/omegavector(I);
end
figure(1)
plot(omegavector, mag3, 'k+-' , omegavector, mag5, 'kx-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Awesome oscillator and SMA(5)*Awesome oscillator')
figure(2)
plot(omegavector, phase3, 'r+-' , omegavector, phase5, 'kx-' )
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('Awesome oscillator and SMA(5)*Awesome oscillator')

figure(3)
plot(omegavector, mag6, 'k-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Accelerator oscillator')
figure(4)
plot(omegavector, phase6, 'k-' )
xlabel('Circular Frequency (radians)')
ylabel('Wrapped Phase (radians)')
title('Accelerator oscillator')
% to find intersection point of phase3 and omegavector, to find
Sure Profit Zone and Unsure Profit Zone
for I = 1: NN
if ( phase6(I) - omegavector(I) ) > 0 & ( phase6(I+1)
- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase6(I)
end
end
figure(5)
plot( omegavector, phase6unwrap, 'k.' )
xlabel('Circular Frequency (radians)')
ylabel('Unwrapped Phase (radians)')
title('Accelerator oscillator')
figure(6)
plot(omegavector, barlag, 'k+-' )
xlabel('Circular Frequency (radians)')
ylabel('bars lag)')
title('Accelerator oscillator')
figure(7)
plot(omegavector, mag3, 'r+-' , omegavector, mag5, 'bx-' ,
omegavector, mag6, 'k.-'

) % 3 awesome, 6 wrapped AC

xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Awesome oscillator, SMA(5)*Awesome oscillator and
Accelerator Oscillator')

figure(8)
plot(omegavector, phase3, 'k-' , omegavector, phase6, 'r.' )
xlabel('Circular Frequency (radians)')
ylabel('wrapped Phase (radians)')
title('Awesome Oscillator, Accelerator oscillator')
```


## D.2 acceloscsig


```matlab
% acceloscsig, plot accelerator oscillator(AO) of a dummy signal, plot
signal with 2 frequencies, plot signal of 1 frequency when amp2 = 0
% set profit = 0 if first data point of accelerator oscillator is greater
than 0
clear
factor = 30 ; % factor = 20.83, 9, 6.283 , 5, 9/2, 9/3, 9/4
% check profit, 31.4, 15.7, 10.47, 7.85, 6.28
%

check profit, take approx 30, 15, 10, 8, 6

factor2 = factor/4 ;
omega = pi/factor;
omega2 = pi/factor2;
NN = 10 * factor; %

NN = 10*factor

% define original signal
amp2 = 0

; % 0.4

theta0 = 0 ; % add to price signal

0, pi/2, pi, 3*pi/2

for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I)

+ theta0 ) + amp2*

sin( omega2*xvector(I) );
end
% set parameters of awesome oscillator and accelerator oscillator
N1= 5;
N2=34;
N3=5;

% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator
end
N2PN3 = N2+N3;
for I = N2PN3 : NN+1
signalline(I) = 0;
for J = 1:N3
signalline(I) = signalline(I ) + 1/N3 * aweosc(I+1 - J);
end
end
for I = N2PN3 : NN+1
accelosc (I) = aweosc(I) - signalline(I); %calculate aceleraator
oscillator
end
% To calculate buy price and sell price, and profit of acceleration
oscillator
B = 0; % Buy originally set to 0
Iprofit=1;
if

accelosc(N2PN3)

we do not buy
Iprofit = 0;
end

> 0 % first data point greater than 0,

for I = N2PN3: NN+1
if

B == 0 &

I ,

accelosc(I)

> 0

ybuy = yvector(I)

B = 1
else
if B == 1
I,

&

accelosc(I) < 0

ysell = yvector(I)

switch Iprofit
case {0}
profit = 0
Iprofit=1;
case{1}
profit = ( (ysell - ybuy)/2 ) *100
end
B = 0
end
end
end
figure(1)
plot(xvector, yvector, 'kx-',

xvector(N2: NN+1), aweosc(N2 :

NN+1), 'r+-', xvector(N2PN3: NN+1),signalline(N2PN3 : NN+1), 'b+-',
xvector, zero, 'k' )
xlabel('t')
ylabel('price, awesome oscillator, signal line')
figure(2)
plot(xvector, yvector, 'kx-', xvector(N2PN3: NN+1),
accelosc(N2PN3 : NN+1), 'k+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, accelerator oscillator of price')
```


## D.3 awesig


```matlab
% % awesig, plot awesome oscillator(AO) of a dummy signal, plot signal
with 2 frequencies, plot signal of 1 frequency when amp2 = 0
% set profit = 0 if first data point of awesome oscillator is greater
than 0
clear
factor = 30 ; % factor = 20.83, 9, 6.283 , 5, 9/2, 9/3, 9/4
% factor = 24.166, AO of signal is in phase with signal

%

check profit, 31.4, 15.7, 10.47, 7.85, 6.28

%

check profit, take approx 30, 15, 10, 8, 6

factor2 = factor/4 ;
omega = pi/factor;
omega2 = pi/factor2;
NN = 8 * factor; % NN = 8*factor
% define original signal
amp2 = 0 ; % 0.4
theta0 = 0

; % add to price signal

0, pi/2 pi, 3*pi/2

for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I)

+ theta0 ) + amp2*

sin( omega2*xvector(I) );
end
% set parameters of awesome oscillator and accelerator oscillator
N1= 5;
N2=34;
N3=5;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator of signal
end

N2PN3 = N2+N3;
for I = N2PN3 : NN+1
signalline(I) = 0;
for J = 1:N3
signalline(I) = signalline(I ) + 1/N3 * aweosc(I+1 - J);
end

end
for I = N2PN3 : NN+1
accelosc (I) = aweosc(I) - signalline(I); %calculate aceleraator
oscillator of signal
end
% To calculate buy price and sell price, and profit of awesome oscillator
B = 0; % Buy originally set to 0
Iprofit=1;
if

aweosc(N2)

> 0 % first data point greater than 0, we do

not buy
Iprofit = 0;
end
for I = N2: NN+1
if

B == 0

&

I ,

aweosc(I)

> 0

ybuy = yvector(I)

B = 1
else
if B == 1
I,

&

aweosc(I) < 0

ysell = yvector(I)

switch Iprofit
case {0}
profit = 0
Iprofit=1;
case{1}
profit = ( (ysell - ybuy)/2 ) *100
end
B = 0
end
end
end

figure(1)
plot(xvector, yvector, 'kx-',

xvector(N1: NN+1), sma1signal(N1 :

NN+1), 'r+-', xvector(N2: NN+1),sma2signal(N2 : NN+1), 'b+-',

xvector,

zero, 'k' )
xlabel('t')
ylabel('price, sma5, sma34')
figure(2)
plot(xvector, yvector, 'kx-', xvector(N2: NN+1), aweosc(N2 : NN+1),
'r+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price,awesome oscillator of price')
```


## D.4 awesome


```matlab
% awesome, Plot Amplitude and Phase of simple moving averages and awesome
oscillator
% unwrap phase, Find Sure and Unsure profit Zone
clear
NN= 240 ; % 240
intomega=pi/NN;
M1=5 ; % 5
M2=34; % 34
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)=1/M1*( 1- exp(-i*M1*omegavector(I)) ) /( 1 exp(-i*omegavector(I) ) );
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
H2vector(I)= 1/M2*( 1- exp(-i*M2*omegavector(I)) ) /( 1 exp(-i*omegavector(I) ) );
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));
H3vector(I)= H1vector(I) - H2vector(I); % awesome oscillator
mag3(I)=abs(H3vector(I));
phase3(I)= angle(H3vector(I));
end

phase3unwrap = unwrap(phase3); % unwrap phase
for I= 1: NN+1
barlag(I) = phase3unwrap(I)/omegavector(I);
end
mag(1) = 1;
phase1(1)=0;
mag2(1) = 1;
phase2(1)=0;
mag3(1) = 0;
phase3(1) = pi/2;
phase3unwrap(1) = pi/2;
figure(1)
plot(omegavector, mag1, 'k+-' , omegavector, mag2, 'kx-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Simple Moving Average')
figure(2)
plot(omegavector, phase1, 'k+-' , omegavector, phase2, 'kx-' )
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('Simple Moving Average')
figure(3)
plot(omegavector, mag3, 'k-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Awesome Oscillator')
figure(4)
plot(omegavector, phase3, 'k-'

)

xlabel('Circular Frequency (radians)')
ylabel('Wrapped Phase (radians)')
title('Awesome Oscillator')
% to find intersection point of phase3 and omegavector, to find Sure
Profit Zone and Unsure Profit Zone
for I = 1: NN
if ( phase3(I) - omegavector(I) ) > 0 & ( phase3(I+1)

- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase3(I)
end
end
figure(5)
plot( omegavector, phase3unwrap, 'k-' )
xlabel('Circular Frequency (radians)')
ylabel('Unwrapped Phase (radians)')
title('Awesome Oscillator')
figure(6)
plot(omegavector, barlag, 'k+-' )
xlabel('Circular Frequency (radians)')
ylabel('bars lag)')
title('Awesome Oscillator')
```


## D.5 buysellprice


```matlab
%buysellprice, to calculate theoretical buy and sell price where price
is a signal of a single sine wave.
% omega, theta0 and phi are given
% As sine wave is an odd function with respect to the horizontal axis,
sell price = - buy price
clear
omega = pi/6 % circular frequency
theta0 = 0 ;% theta0 = initial phase shift of price signal, e.g. pi/4,
pi/2
phi = -0.4718

; % phi = phase lead of velocity indicator, e.g., pi/2

nbuy = fix( (2*pi - theta0 - phi)/omega ) + 1
buyprice = sin (nbuy *omega + theta0 )
nsell = fix( (3*pi - theta0 - phi)/omega ) + 1
sellprice = sin (nsell *omega + theta0 )
profit = sellprice - buyprice
profitpercent = profit/2 *100
```


## D.6 ema


```matlab
% ema, Plot Amplitude and Phase and bar lag of exponential moving average
clear
NN=180; %60
intomega=pi/NN;
N = 3;
alpha = 2/(N+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha/ (1 -(1- alpha)* exp (-i * omegavector(I) ) ) ;
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
barlag1(I) = phase1(I) / omegavector(I);
end
barlag1(1) = -(N-1)/2;
figure(1)
subplot(1, 1, 1)
plot(omegavector, mag1, 'kx-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Exponential Moving Average')
figure(2)
subplot(1, 1, 1)
plot(omegavector, phase1, 'kx-'

)

xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('Exponential Moving Average')
figure(3)
subplot(1, 1, 1)
plot(omegavector, barlag1, 'kx-' )
xlabel('Circular Frequency (radians)')
ylabel('bar lag')
title('Exponential Moving Average')
```


## D.7 emaaccel


```matlab
%emaaccel , Plot Amplitude and Phase of ema3 - ema6, ema9(ema3 - ema6),
emaaccel = (ema3 - ema6) - ema9(ema3 - ema6)
clear
NN=240;
intomega=pi/NN;
M1=3 ; % 12
alpha1=2/(M1+1);
M2= 6; %26
alpha2=2/(M2+1);
M3=9 ; %9
alpha3=2/(M3+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha1/ ( 1-(1-alpha1)*exp(-i*omegavector(I)));
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
H2vector(I)= alpha2/ (1-(1-alpha2)*exp(-i*omegavector(I)));
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));
H4vector(I) = H1vector(I) - H2vector(I); %ema3 - ema6
mag4(I)=abs(H4vector(I));
phase4(I)= angle(H4vector(I));
H3vector(I)= alpha3/ ( 1-(1-alpha3)*exp(-i*omegavector(I)));
H6vector(I) = H3vector(I)*H4vector(I);% signal line = ema9(ema3 ema6)
mag6(I)=abs(H6vector(I));
phase6(I)= angle(H6vector(I));
H5vector(I) = H4vector(I) - H6vector(I); % (ema3 - ema6) ema9(ema3 - ema6)
mag5(I)=abs(H5vector(I));
phase5(I)= angle(H5vector(I));
end

mag1(1) = 1;
phase1(1) = 0;
mag2(1) = 1;
phase2(1) = 0;
mag4(1) = 0; % (ema3 - ema6)
phase4(1) = pi/2;
mag6(1) = 0; % signal line
phase6(1) = pi/2;
mag5(1) = 0; %(ema3 - ema6) - ema9(ema3 - ema6)
phase5(1) = pi;
figure(1)
subplot(1, 1, 1)
plot( omegavector, mag5, 'k-' ) % emaaccel
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('EMAACCEL') % emaaccel = (ema3 - ema6) – ema9(ema3 - ema6)
figure(2)
subplot(1, 1, 1)
plot( omegavector, phase5, 'k-' )

% emaaccel

xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('EMAACCEL') % emaaccel = (ema3 - ema6) – ema9(ema3 - ema6)
% to find intersection point of phase3 and omegavector
for I = 1: NN
if ( phase5(I) - omegavector(I) ) > 0 & ( phase5(I+1)
- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase5(I)
end
end
figure(3)
plot(omegavector, mag4, 'r+-' , omegavector, mag6, 'bx-' ,
omegavector, mag5, 'k.-' ) % (ema3 - ema6), signal line, emaaccel
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('EMAACCEL') % emaaccel = (ema3 - ema6) – ema9(ema3 - ema6)

figure(4)
subplot(1, 1, 1)
plot(omegavector, phase4, 'r+-' , omegavector, phase6, 'bx-' ,
omegavector, phase5, 'k-' )

% 4 (ema3 - ema6),

6 ema9(ema3 - ema6),

5 emaaccel
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('EMAACCEL') % emaaccel = (ema3 - ema6) - ema9(ema3 - ema6)
```


## D.8 emaaccelsig


```matlab
% % emaaccelsig, plot emaaccel of a dummy signal, plot signal with 2
frequencies, plot signal of 1 frequency when amp2 = 0
% set profit = 0 if first data point of emaaccel is greater than 0
clear
factor = 6 ; % factor = 20.83, 9, 6.283 , 5, 9/2, 9/3, 9/4
%

check profit, take approx 30, 15, 10, 8, 6

factor2 = factor/4 ;
omega = pi/factor;
omega2 = pi/factor2;
NN = 8 * factor; % NN = 8*factor
% define original signal
amp2 = 0

; % 0.4

theta0 = 0 ; % add to price signal

0, pi/2, pi, 3*pi/2

for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I)
sin( omega2*xvector(I) );
end
% set parameters of emaaccel
M1=3;
alpha1=2/(M1+1);
M2=6 ;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt =30; % 30

+ theta0 ) + amp2*

% calculate technical indicators on signal
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
end
% To calculate buy price and sell price, and profit of emaaccel
B = 0; % Buy originally set to 0
Iprofit=1;
if

macdhsignal(startpt)

> 0 % first data point greater than

0, we do not buy
Iprofit = 0;
end
for I = startpt: NN+1
if

B == 0 &

I ,

macdhsignal(I)

> 0

ybuy = yvector(I)

B = 1
else
if B == 1
I,

&

macdhsignal(I) < 0

ysell = yvector(I)

switch Iprofit
case {0}
profit = 0
Iprofit=1;
case{1}
profit = ( (ysell - ybuy)/2 ) *100
end
B = 0
end
end
end

figure(1)
plot(xvector, yvector, 'kx-',

xvector(startpt: NN+1),

macdsignal(startpt : NN+1), 'r+-', xvector(startpt:
NN+1),ema3macd(startpt : NN+1), 'b+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, ema3-ema6, ema9(ema3-ema6)')
figure(2)
plot(xvector, yvector, 'kx-', xvector(startpt: NN+1),
macdhsignal(startpt : NN+1), 'r+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, emaacel of price')
```


## D.9 emamema


```matlab
%emamema, Plot Amplitude and Phase of a fast ema minus a slow ema
clear
NN=240;
intomega=pi/NN;
M1=3 ; % cf 12 for MACD
alpha1=2/(M1+1);
M2=6 ; % cf 26 for MACD
alpha2=2/(M2+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha1/ ( 1-(1-alpha1)*exp(-i*omegavector(I)));
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
H2vector(I)= alpha2/ (1-(1-alpha2)*exp(-i*omegavector(I)));
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));
H4vector(I) = H1vector(I) - H2vector(I); %cf MACD
mag4(I)=abs(H4vector(I));
phase4(I)= angle(H4vector(I));
phase4(1) = pi/2;
barlag4(I) = ( phase4(I) - pi/2 ) / omegavector(I);
end

mag1(1) = 1;
phase1(1) = 0;
mag2(1) = 1;
phase2(1) = 0;
mag4(1) = 0; % fast ema - slow ema
figure(1)
plot(omegavector, mag1, 'r+-' , omegavector, mag2, 'bx-' ,
omegavector, mag4, 'k.-' ) %1 fast EMA, 2 slow EMA, 4 fast ema - slow
ema
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('EMA - EMA ')
figure(2)
subplot(1, 1, 1)
plot(omegavector, phase1, 'r+-' , omegavector, phase2, 'bx-' ,
omegavector, phase4, 'k-' )
%1 fast EMA, 2 slow EMA, 4 fast ema - slow
ema
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('EMA - EMA ')
figure(3)
plot( omegavector, mag4, 'k-' )
ema - slow ema

%1 fast EMA, 2 slow EMA, 4 fast

xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('EMA - EMA ')
figure(4)
subplot(1, 1, 1)
plot( omegavector, phase4, 'k-' )
%1 fast EMA, 2 slow EMA, 4 fast
ema - slow ema
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('EMA - EMA ')
% to find intersection point of phase4 and omegavector
for I = 1: NN
if ( phase4(I) - omegavector(I) ) > 0 & ( phase4(I+1)
- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase4(I)
end
end

figure(5)
subplot(1, 1, 1)
plot( omegavector, barlag4, 'rx-' )
xlabel('Circular Frequency (radians)')
ylabel('barlag')
title('EMA - EMA ')
```


## D.10 emaseveral


```matlab
% emaseveral, Plot Amplitude and Phase and bar lag of several exponential
moving averages for comparison purpose
clear
NN=60;
intomega=pi/NN;
N1=3;
N2 = 6;
alpha1 = 2/(N1+1);
alpha2 = 2/(N2+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha1/ (1 -(1- alpha1)* exp (-i * omegavector(I) ) ) ;
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
barlag1(I) = phase1(I) / omegavector(I);
H2vector(I)= alpha2/ (1 -(1- alpha2)* exp (-i * omegavector(I) ) ) ;
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));
barlag2(I) = phase2(I) / omegavector(I);
end
barlag1(1) = - (N1-1)/2;
barlag2(1) = - (N2-1)/2;
figure(1)
subplot(1, 1, 1)
plot(omegavector, mag1, 'kx-' , omegavector, mag2, 'k+-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Exponential Moving Average')

figure(2)
subplot(1, 1, 1)
plot(omegavector, phase1, 'kx-'

, omegavector, phase2, 'k+-' )

xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('Exponential Moving Average')
figure(3)
subplot(1, 1, 1)
plot(omegavector, barlag1, 'kx-' , omegavector, barlag2, 'k+-')
xlabel('Circular Frequency (radians)')
ylabel('bar lag')
title('Exponential Moving Average')
```


## D.11 emasig


```matlab
% emasig, plot ema of a signal
clear
factor = 9/4;
omega = pi/factor;
NN = 4 * factor;
M1=6;
alpha1=2/(M1+1);
startpt = 5;
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I));
end
emasignal(1) = yvector(1);
for I = 2: NN+1
emasignal(I) = alpha1 * yvector(I) + (1 - alpha1) * emasignal(I 1);
end
figure(1)
plot(xvector, yvector, 'kx-', xvector(startpt : NN+1),
emasignal(startpt : NN+1), 'k+-',
xlabel('t')
ylabel('price, ema of price')

xvector, zero, 'k' )
```


## D.12 fftcac40


```matlab
% fftcac40,

plotting signal, magnitude of fft, phase of fft, real of

ifft, and phase of ifft
fft = Fast Fourier Transform, ifft = Inverse Fast Fourier Transform
clear
% CAC 40 from March 6, 2019 to Jun 39, 2019
yvector = [ 5288 5267 5231 5265 5270 5306 5349 5405 5412 5425
5382 5378 5269 5260 5307 5301 5296 5350 5405 5423 5468 5463
5476 5471 5436 5449 5485 5502 5508 5528 5563 5580 5591 5576
5557 5569 5580 5586 5538 5548 5483 5395 5417 5313 5327 5262
5341 5374 5448 5438 5358 5385 5378 5281 5316 5336 5312 5222
5248 5207 5241 5268 5292 5278 5364 5382 5408 5374 5375 5367
5390 5509 5518 5535 5528 5521 5514 5500 5493 5538 5567 5576
5618 5620 5593 5589 5572 5567 5551 5572 5578 5614 5571 5550
5552 5567 5618 5505 5578 5610 5601 5511 5618 5557 5359 5241
5234 5266 5387 5327 5310 5363 5251 5236 5300 5371 5344
5435

];

NN = 117 ; % i.e., 118 data points
NN = length(yvector) - 1
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
% To find fft of price
fftvector = fft(yvector);
mag=abs (fftvector);
phase = angle(fftvector);
% To find ifft of fft of price, ifft(fft of price) should equal to
price
ifftvector = ifft(fftvector);
real2= real( ifftvector);
mag2=abs (ifftvector);
phase2 = angle(ifftvector);
figure(1)
subplot(1, 1,1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price ')
title(' CAC 40 ')

figure(2)
subplot(1, 1,1)
plot(xvector, mag, 'k+', xvector, zero, 'k' )
xlabel('n')
ylabel('magnitude of fft')
figure(3)
subplot(1, 1,1)
plot(xvector(2:NN), mag(2:NN), 'k+', xvector, zero, 'k' )
xlabel('n')
ylabel('magnitude of fft, without n = 0')
figure(4)
subplot(1, 1,1)
plot(xvector, phase, 'k+-', xvector, zero, 'k' )
xlabel('n')
ylabel('phase of fft')
figure(5)
subplot(1, 1,1)
plot(xvector, yvector, 'k+-' , xvector, mag2, 'go' ) % note that mag2

= real2 as the price data do not have imaginary numbers
xlabel('n')
ylabel('magnitude of ifft o, price +')
figure(6)
subplot(1, 1,1)
plot(xvector, phase2, 'k+-', xvector, zero, 'k' )
xlabel('n')
ylabel('phse of ifft')
```


## D.13 fftftse


```matlab
% fftftse,

plotting signal, magnitude of fft, phase of fft, real of

ifft, and phase of ifft
clear
% FTSE

from March 1, 19 to Aug 14, 19

yvector = [

115 data point

7106 7134 7183 7196 7157 7104 7130 7151 7159

7185 7228 7299 7324 7291 7355 7207 7177 7196 7194 7234 7279
7317 7391 7418 7401 7446 7451 7425 7421 7418 7437 7436 7469
7471 7459 7523 7471 7434 7428 7440 7418

7385 7351 7380 7260

7271 7207 7203 7163 7241 7297 7353 7348 7310 7328 7334 7231
7277 7269 7185 7218 7161 7184 7214 7220 7259 7331 7375 7398
7367 7368 7345 7357 7443 7403 7424 7407 7416 7422 7416 7402
7425 7497 7559 7609 7603 7553 7549 7536 7530 7509 7506 7531
7577 7535 7493 7508 7514 7556 7501 7489 7549 7686 7645 7586
7584 7407 7223 7171 7198 7285 7253 7226 7250 7147

];

NN=114; % i.e., 115 data point
NN = length(yvector) - 1
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
% To find fft of price
fftvector = fft(yvector);
mag=abs (fftvector);
phase = angle(fftvector);
% To find ifft of fft of price, ifft(fft of price) should equal to
price
ifftvector = ifft(fftvector);
real2= real( ifftvector);
mag2=abs (ifftvector);
phase2 = angle(ifftvector);
figure(1)
subplot(1, 1,1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price ')
title('FTSE 100 ')
figure(2)
subplot(1, 1,1)
plot(xvector, mag, 'k+', xvector, zero, 'k' )
xlabel('n')
ylabel('magnitude of fft')

figure(3)

subplot(1, 1,1)
plot(xvector(2:NN), mag(2:NN), 'k+', xvector, zero, 'k' )
xlabel('n')
ylabel('magnitude of fft, without n = 0')
figure(4)
subplot(1, 1,1)
plot(xvector, phase, 'k+-', xvector, zero, 'k' )
xlabel('n')
ylabel('phase of fft')
figure(5)
subplot(1, 1,1)
plot(xvector, yvector, 'k+-' , xvector, mag2, 'go' ) % note that mag2
= real2 as the price data do not have imaginary numbers
xlabel('n')
ylabel('magnitude of ifft o, price +')
figure(6)
subplot(1, 1,1)
plot(xvector, phase2, 'k+-', xvector, zero, 'k' )
xlabel('n')
ylabel('phse of ifft')
```


## D.14 ffthangseng


```matlab
% ffthangseng,

plotting signal,

magnitude of fft, phase of fft, real

of ifft, and phase of ifft
clear
%Hang Seng from March 1 2019 to Aug 12, 2019
yvector = [ 28812 28959 28961 29037 28779 28228 28503 28920
28807 28851 29012 29409 29466 29320 29071 29113 28523 28567
28728 28775 29051 29562 29624 29986 29936 30077 30157 30119
29839 29909 29810 30129 30124 29963 29963 29805 29549 29605
29892 29699 29209 29363 29003 28311 28550 28122 28268 28275
27946 27787 27657 27705 27267 27353 27268 27390 27235 27114
26901 26893 26761 26895 26965 27578 27789 27308 27294 27118
27227 27498 28202 28550 28473 28513 28185 28221 28621 28542
28875 28855 28795 28774 28331 28116 28204 28431 28471 28554
28619 28593 28461 28765 28371 28466 28524 28594 28397 28106
28146 27777 27505 26918 26151 25976 25997 26120 25939 25824 ];

NN=107; % i.e., 108 data point
NN = length(yvector) - 1
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
% To find fft of price
fftvector = fft(yvector);
mag=abs (fftvector);
phase = angle(fftvector);
% To find ifft of fft of price, ifft(fft of price) should equal to
price
ifftvector = ifft(fftvector);
real2= real( ifftvector);
mag2=abs (ifftvector);
phase2 = angle(ifftvector);
figure(1)
subplot(1, 1,1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price ')
title('Hang Seng ')
figure(2)
subplot(1, 1,1)
plot(xvector, mag, 'k+', xvector, zero, 'k' )
xlabel('n')
ylabel('magnitude of fft')
figure(3)
subplot(1, 1,1)
plot(xvector(2:NN), mag(2:NN), 'k+', xvector, zero, 'k' )
xlabel('n')
ylabel('magnitude of fft, without n = 0')
figure(4)
subplot(1, 1,1)
plot(xvector, phase, 'k+-', xvector, zero, 'k' )
xlabel('n')
ylabel('phase of fft')

figure(5)
subplot(1, 1,1)
plot(xvector, yvector, 'k+-' , xvector, mag2, 'go' ) % note that mag2

= real2 as the price data do not have imaginary numbers
xlabel('n')
ylabel('magnitude of ifft o, price +')
figure(6)
subplot(1, 1,1)
plot(xvector, phase2, 'k+-', xvector, zero, 'k' )
xlabel('n')
ylabel('phse of ifft')
```


## D.15 fftsinewave


```matlab
% fftsinewave,

plotting Fast Fourier Transform of sine wave, and

Inverse Fast Fourier Transform of Fast Fourier Transform of sine wave,
which should be the same as the original sine wave
clear
int = 20;
omega = pi/int;
NN = 4 * int - 1;
D = 0; % D is a constant added to the sine wave, e.g., D = 2;
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= D + sin( omega*xvector(I)); % raw signal. e.g., price
end
figure(1)
plot(xvector, yvector, 'r+ ', xvector, zero, 'k' )
xlabel('t')
ylabel('price')
fftvector = fft(yvector);
mag=abs (fftvector);
phase = angle(fftvector);

figure(2)
plot(xvector, mag, 'r+', xvector, zero, 'k' ) % plot magnitude of
fft
xlabel('t')
ylabel('magnitude of fft')
figure(3)
plot(xvector, phase, 'r', xvector, zero, 'k' ) % plot phase of fft
xlabel('t')
ylabel('phase of fft')
ifftvector = ifft(fftvector);
real2= real( ifftvector);
mag2=abs (ifftvector);
phase2 = angle(ifftvector);
figure(4)
plot(xvector, real2, 'r+ ', xvector, yvector, 'go' , xvector, zero,
'k' ) % plot real part of ifft, which is equal to magnitude of ifft, which
should be the same as original price
xlabel('t')
ylabel('magnitude of ifft +, price o ')
figure(5)
plot(xvector, phase2, 'r', xvector, zero, 'k' )
xlabel('t')
ylabel('phase of ifft')
```


## D.16 fftsp500


```matlab
% fftsp500,

plotting signal, magnitude of fft, phase of fft, real of

ifft, and phase of ifft
clear
% S& P500 from April 24, 2019 to Aug 12, 2019
yvector = [2927.25 2926.17 2939.88 2943.03 2945.83 2923.73
2917.52 2945.64 2932.47 2884.05 2879.42 2870.72 2881.40 2811.87
2834.41 2850.96 2876.32 2859.53 2840.23 2864.36 2856.27 2822.24
2826.06 2802.39 2783.02 2788.86 2752.06 2744.45 2803.27 2826.15
2843.49 2873.34 2886.73 2885.72 2879.84 2891.64 2886.98 2889.67
2917.75 2926.46 2954.18 2950.46 2945.35 2917.38 2913.78 2924.92
2941.76 2964.33 2973.01 2995.82 2990.41 2975.95 2979.63
2993.07 2999.91 3013.77 3014.30 3004.04 2984.42 2995.11 2976.61
2995.03 3005.47 3019.56 3003.67 3025.86 3020.97 3013.18 2980.38
2953.56 2932.05 2844.74 2881.77 2883.98 2938.09 2918.65

2882.70 ];
NN=76; %i.e., 77 data points
NN = length(yvector) - 1
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
% To find fft of price
fftvector = fft(yvector);
mag=abs (fftvector);
phase = angle(fftvector);

% To find ifft of fft of price, ifft(fft of price) which should equal
to price
ifftvector = ifft(fftvector);
real2= real( ifftvector);
mag2=abs (ifftvector);
phase2 = angle(ifftvector);
figure(1)
subplot(1, 1,1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price ')
title('S & P500')
figure(2)
subplot(1, 1,1)
plot(xvector, mag, 'k+', xvector, zero, 'k' )
xlabel('n')
ylabel('magnitude of fft')
figure(3)
subplot(1, 1,1)
plot(xvector(2:NN), mag(2:NN), 'k+', xvector, zero, 'k' )
xlabel('n')
ylabel('magnitude of fft, without n = 0')

figure(4)
subplot(1, 1,1)
plot(xvector, phase, 'k+-', xvector, zero, 'k' )
xlabel('n')
ylabel('phase of fft')
figure(5)
subplot(1, 1,1)
plot(xvector, yvector, 'k+-' , xvector, mag2, 'go' ) % note that mag2
= real2 as the price data do not have imaginary numbers
xlabel('n')
ylabel('magnitude of ifft o, price +')
figure(6)
subplot(1, 1,1)
plot(xvector, phase2, 'k+-', xvector, zero, 'k' )
xlabel('n')
ylabel('phse of ifft')
```


## D.17 hema


```matlab
% hema,

To calculate h(k) of ema, unit impulse response of

exponential moving average
clear
M3=3;
M6=6;
M9=9;
M12=12;
M26=26;
alpha3 = 2/(M3 +1);
alpha6 = 2/(M6 +1);
alpha9 = 2/(M9 +1);
alpha12 = 2/(M12 +1);
alpha26= 2/(M26 +1);
NN=40;
for I= 1: NN+1
kvector(I)=I -1;
h3vector(I) = alpha3 * (1 - alpha3)^(I-1);
h6vector(I) = alpha6 * (1 - alpha6)^(I-1);

h9vector(I) = alpha9 * (1 - alpha9)^(I-1);
h12vector(I) = alpha12 * (1 - alpha12)^(I-1);
h26vector(I) = alpha26 * (1 - alpha26)^(I-1);
end
figure(1)
subplot(1, 1, 1)
plot(kvector, h3vector, 'ko' , kvector, h6vector, 'kx',kvector,

h9vector, 'k^',kvector, h12vector, 'k*',kvector, h26vector, 'k+' )
xlabel('k')
ylabel('Unit sample response, h(k)')
title('Exponential Moving Average')
figure(2)
subplot(1, 1, 1)
plot(kvector, h3vector, 'r-' , kvector, h6vector, 'b-',kvector,
h9vector, 'g-',kvector, h12vector, 'm-',kvector, h26vector, 'k-' )
xlabel('k')
ylabel('Unit sample response, h(k)')
title('Exponential Moving Average for M =3,6,9,12,26')
```


## D.18 macd


```matlab
%macd, Plot Amplitude and Phase of MACD
clear
NN= 240; % 240, 14400
intomega=pi/NN;
M1=12; % 12 for MACD
alpha1=2/(M1+1);
M2=26 ; % 26 for MACD
alpha2=2/(M2+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha1/ ( 1-(1-alpha1)*exp(-i*omegavector(I)));
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
H2vector(I)= alpha2/ (1-(1-alpha2)*exp(-i*omegavector(I)));
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));

H4vector(I) = H1vector(I) - H2vector(I); %MACD
mag4(I)=abs(H4vector(I));
phase4(I)= angle(H4vector(I));
phase4(1) = pi/2;
barlag4(I) = ( phase4(I) - pi/2 ) / omegavector(I);
end
mag1(1) = 1;
phase1(1) = 0;
mag2(1) = 1;
phase2(1) = 0;
mag4(1) = 0; % MACD
figure(1)
plot(omegavector, mag1, 'r+-' , omegavector, mag2, 'bx-' ,
omegavector, mag4, 'k.-' )

%1 fast EMA, 2 slow EMA, 4 MACD

xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('MACD')
figure(2)
subplot(1, 1, 1)
plot(omegavector, phase1, 'r+-' , omegavector, phase2, 'bx-' ,
omegavector, phase4, 'k-' )

%1 fast EMA, 2 slow EMA, 4 MACD

xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('MACD')
% to find intersection point of phase4 and omegavector, Sure and
Unsure Profit Zone
for I = 1: NN
if ( phase4(I) - omegavector(I) ) > 0 & ( phase4(I+1)
- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase4(I)
end
end
figure(3)
subplot(1, 1, 1)
plot( omegavector, barlag4, 'kx-'

)

xlabel('Circular Frequency (radians)')
ylabel('barlag')
title('MACD')
```


## D.19 macdh


```matlab
%macdh, Plot Amplitude and Phase of MACD, signal line, and MACDH
clear
NN=240; %240, larger NN, e.g., 14400, to find intersection point more
accurately, answer: omega = 0.235
intomega=pi/NN;
M1=12 ;
alpha1=2/(M1+1);
M2=26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha1/ ( 1-(1-alpha1)*exp(-i*omegavector(I)));
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
H2vector(I)= alpha2/ (1-(1-alpha2)*exp(-i*omegavector(I)));
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));
H4vector(I) = H1vector(I) - H2vector(I); %MACD
mag4(I)=abs(H4vector(I));
phase4(I)= angle(H4vector(I));
H3vector(I)= alpha3/ ( 1-(1-alpha3)*exp(-i*omegavector(I)));
H6vector(I) = H3vector(I)*H4vector(I);% signal line
mag6(I)=abs(H6vector(I));
phase6(I)= angle(H6vector(I));
H5vector(I) = H4vector(I) - H6vector(I); % MACDH
mag5(I)=abs(H5vector(I));
phase5(I)= angle(H5vector(I));
end

mag1(1) = 1;
phase1(1) = 0;
mag2(1) = 1;
phase2(1) = 0;
mag4(1) = 0; % MACD
phase4(1) = pi/2;
mag6(1) = 0; % signal line
phase6(1) = pi/2;
mag5(1) = 0; %MACDH
phase5(1) = pi;
figure(1)
plot(omegavector, mag4, 'r+-' , omegavector, mag6, 'bx-' ,
omegavector, mag5, 'k.-' ) % MACD, signal line, MACDH
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('MACDH')
figure(2)
subplot(1, 1, 1)
plot(omegavector, phase4, 'r+-' , omegavector, phase6, 'bx-' ,
omegavector, phase5, 'k.-' )

% 4 MACD,

6 signal line, 5 MACDH

xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('MACDH')
figure(3)
subplot(1, 1, 1)
plot(omegavector, omegavector, 'k-' , omegavector, phase5, 'k-' )
% omegavector, omegavector is the line plotted to show that there can
be a loss in the trade when phase is less than omega
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('MACDH')
% to find intersection point of phase3 and omegavector
for I = 1: NN
if ( phase5(I) - omegavector(I) ) > 0 & ( phase5(I+1)
- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase5(I)
end
end
```


## D.20 macdh1


```matlab
%macdh1, MACDH with M1 = 1, i.e. price
%Plot Amplitude and Phase of MACD1, signal line, and MACDH1
clear
NN=240;
intomega=pi/NN;
M1=1; % cf 12 for MACDH
alpha1=2/(M1+1);
M2=26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha1/ ( 1-(1-alpha1)*exp(-i*omegavector(I)));
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
H2vector(I)= alpha2/ (1-(1-alpha2)*exp(-i*omegavector(I)));
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));
H4vector(I) = H1vector(I) - H2vector(I); %MACD1
mag4(I)=abs(H4vector(I));
phase4(I)= angle(H4vector(I));
H3vector(I)= alpha3/ ( 1-(1-alpha3)*exp(-i*omegavector(I)));
H6vector(I) = H3vector(I)*H4vector(I);% signal line = 6
mag6(I)=abs(H6vector(I));
phase6(I)= angle(H6vector(I));
H5vector(I) = H4vector(I) - H6vector(I); % MACDH1
mag5(I)=abs(H5vector(I));
phase5(I)= angle(H5vector(I));
end
mag1(1) = 1;
phase1(1) = 0;
mag2(1) = 1;

phase2(1) = 0;
mag4(1) = 0; % MACD1=4
phase4(1) = pi/2;
mag6(1) = 0; % signal line
phase6(1) = pi/2;
mag5(1) = 0; %MACDH1=5
phase5(1) = pi;
figure(1)
subplot(1, 1, 1)
plot(omegavector, mag4, 'r+-' , omegavector, mag6, 'bx-' ,
omegavector, mag5, 'k.-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('MACDH1')
figure(2)
subplot(1, 1, 1)
plot(omegavector, phase4, 'r+-' , omegavector, phase6, 'bx-' ,
omegavector, phase5, 'k.-' )

% 4 MACD1,

6 signal line, 5 MACDH1

xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('MACDH1')
% to find intersection point of phase5 and omegavector
for I = 1: NN
if ( phase5(I) - omegavector(I) ) > 0 & ( phase5(I+1)
- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase5(I)
end
end
```


## D.21 macdh1sig


```matlab
% % macdh1sig, M1 = 1, plot MACDH1 of a dummy signal, plot signal with
2 frequencies, plot signal of 1 frequency when amp2 = 0
% set profit = 0 if first data point of MACDH1 is greater than 0
clear
factor = 6 ; % factor = 20.83, 9, 6.283 , 5, 9/2, 9/3, 9/4
%

check profit, 31.4, 15.7, 10.47, 7.85, 6.28

%

check profit, take approx 30, 15, 10, 8, 6 in book

factor2 = 2 ; %factor/4;
omega = pi/factor;
omega2 = pi/factor2;
NN = 10 * factor; % NN = 8*factor, 20*
% define original signal
amp2 = 0. ; % 0.4, 0.25
theta0 = 0 ; % add to price signal

0, pi/2, pi, 3*pi/2

for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I)

+ theta0 ) + amp2*

sin( omega2*xvector(I) );
end
% set parameters of MACDH1
M1=1;
alpha1=2/(M1+1);
M2=26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt =30; % 30
% calculate technical indicators on signal
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
end
% To calculate buy price and sell price, and profit of MACDH1
B = 0; % Buy originally set to 0
Iprofit=1;
if
macdhsignal(startpt)
greater than 0, we do not buy
Iprofit = 0;
end

> 0 % when first data point is

for I = startpt: NN+1
if B == 0 & macdhsignal(I) > 0
I ,
ybuy = yvector(I)
B = 1
else
if B == 1
& macdhsignal(I) < 0
I,
ysell = yvector(I)
switch Iprofit
case {0}
profit = 0
Iprofit=1;
case{1}
profit = ( (ysell - ybuy)/2 ) *100
end
B = 0
end
end
end
figure(1)
plot(xvector, yvector, 'kx-',

xvector(startpt: NN+1),

macdsignal(startpt : NN+1), 'r+-', xvector(startpt:
NN+1),ema3macd(startpt : NN+1), 'b+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, macd1, signal line')
figure(2)
plot(xvector, yvector, 'kx-', xvector(startpt: NN+1),
macdhsignal(startpt : NN+1), 'r+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, MACDH1 of price')
```


## D.22 macdhsig


```matlab
% % macdhsig, plot MACDH of a dummy signal, plot signal with 2 frequencies,
plot signal of 1 frequency when amp2 = 0
% set profit = 0 if first data point of MACDH is greater than 0
clear
factor = 6 ; % factor = 20.83, 9, 6.283 , 5, 9/2, 9/3, 9/4
%

check profit, 31.4, 15.7, 10.47, 7.85, 6.28

%

check profit, take approx 30, 15, 10, 8, 6

factor2 = factor/4 ;
omega = pi/factor;
omega2 = pi/factor2;
NN = 8 * factor; % NN = 8*factor
% define original signal
amp2 = 0 ; % 0.4
theta0 = pi/2 ; % add to price signal

0, pi/2, pi, 3*pi/2

for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I)

+ theta0 ) + amp2*

sin( omega2*xvector(I) );
end
% set parameters of MACDH
M1=12;
alpha1=2/(M1+1);
M2=26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt =30; % 30
% calculate technical indicators on signal
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
end
% To calculate buy price and sell price, and profit of MACDH
B = 0; % Buy originally set to 0
Iprofit=1;
if
macdhsignal(startpt)

> 0 % when first data point is

greater than 0, we do not buy
Iprofit = 0;
end
for I = startpt: NN+1
if

B == 0 &

I ,

macdhsignal(I)

> 0

ybuy = yvector(I)

B = 1
else
if B == 1
I,

&

macdhsignal(I) < 0

ysell = yvector(I)

switch Iprofit
case {0}
profit = 0
Iprofit=1;
case{1}
profit = ( (ysell - ybuy)/2 ) *100
end
B = 0
end
end
end
figure(1)
plot(xvector, yvector, 'kx-',

xvector(startpt: NN+1),

macdsignal(startpt : NN+1), 'r+-', xvector(startpt:
NN+1),ema3macd(startpt : NN+1), 'b+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, ema12, ema26')
figure(2)
plot(xvector, yvector, 'kx-', xvector(startpt: NN+1),
macdhsignal(startpt : NN+1), 'r+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, MACDH of price')
```


## D.23 macdsig


```matlab
% macdsig, plot MACD of a dummy signal, plot signal with 2 frequencies,
plot signal of 1 frequency when amp2 = 0
% set profit = 0 if first data point of macd is greater than 0

clear
factor = 8 ; % factor = 20.83, 9, 6.283 , 5, 9/2, 9/3, 9/4
%
check profit, 31.4, 15.7, 10.47, 7.85, 6.28
%
check profit, take approx 30, 15, 10, 8, 6
factor2 = factor/4 ;
omega = pi/factor;
omega2 = pi/factor2;
NN = 10 * factor; % NN = 8*factor
% define original signal
amp2 = 0. ; % 0.4
theta0 = pi/2

; % add to price signal

0, pi/2, pi, 3*pi/2

for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I)

+ theta0 ) + amp2*

sin( omega2*xvector(I) );
end
% set parameters of MACD
M1=12;
alpha1=2/(M1+1);
M2=26;
alpha2=2/(M2+1);
startpt =30; % 30
% calculate technical indicators on signal
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
end
% To calculate buy price and sell price, and profit of MACD
B = 0; % Buy originally set to 0
Iprofit=1;
if
macdsignal(startpt)
greater than 0, we do not buy
Iprofit = 0;
end

> 0

% when first data point is

for I = startpt: NN+1
if

B == 0 &

I ,

macdsignal(I)

> 0

ybuy = yvector(I)

B = 1
else
if B == 1
I,

&

macdsignal(I) < 0

ysell = yvector(I)

switch Iprofit
case {0}
profit = 0
Iprofit=1;
case{1}
profit = ( (ysell - ybuy)/2 ) *100
end
B = 0
end
end
end
figure(1)
plot(xvector, yvector, 'kx-',

xvector(startpt: NN+1),

ema1signal(startpt : NN+1), 'r+-', xvector(startpt:
NN+1),ema2signal(startpt : NN+1), 'b+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, ema12, ema26')
figure(2)
plot(xvector, yvector, 'kx-', xvector(startpt: NN+1),
macdsignal(startpt : NN+1), 'r+-',

xvector, zero, 'k' )

xlabel('t')
ylabel('price, MACD of price')
```


## D.24 pmema


```matlab
%pmema, Plot Amplitude and Phase of Price minus EMA of price
clear
NN=240;
intomega=pi/NN;
M1=1; % cf MACD 12

alpha1=2/(M1+1);
M2= 6

%cf MACD 26

alpha2=2/(M2+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha1/ ( 1-(1-alpha1)*exp(-i*omegavector(I)));
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
H2vector(I)= alpha2/ (1-(1-alpha2)*exp(-i*omegavector(I)));
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));
H4vector(I) = H1vector(I) - H2vector(I); %pmema, cf MACD
mag4(I)=abs(H4vector(I));
phase4(I)= angle(H4vector(I));
phase4(1) = pi/2;
end
mag1(1) = 1;
phase1(1) = 0;
mag2(1) = 1;
phase2(1) = 0;
mag4(1) = 0; % cf MACD
figure(1)
plot( omegavector, mag4, 'k+- ' )

% Price - EMA of Price

xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('

Price - EMA of Price ') %

Price - EMA of Price

figure(2)
subplot(1, 1, 1)
plot( omegavector, phase4, 'k+- ' )

% Price - EMA of Price

xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('

Price - EMA of Price ' )

figure(3)
subplot(1, 1, 1)
plot( omegavector, phase4, 'k- '

, omegavector,omegavector, 'k-

' )

% Price - EMA of Price,plot straight line to find Sure and Unsure

Profit Zone
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians) ' )
title('

Price - EMA of Price ' )

% to find intersection point of phase3 and omegavector
for I = 1: NN
if ( phase4(I) - omegavector(I) ) > 0 & ( phase4(I+1)
- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase4(I)
end
end
figure(4)
plot(omegavector, mag1, 'r+-' , omegavector, mag2, 'bx-' ,
omegavector, mag4, 'k.-' ) %1 fast EMA, 2 slow EMA, 4 fast EMA - slow
EMA
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title(' Price - EMA of Price ')
figure(5)
subplot(1, 1, 1)
plot(omegavector, phase1, 'r+-' , omegavector, phase2, 'bx-' ,
omegavector, phase4, 'k.-' ) %1 fast EMA, 2 slow EMA, 4 fast EMA slow EMA
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title(' Price - EMA of Price ')
```


## D.25 pmemasig


```matlab
% pmemasig, plot price minus ema of price (pmema) of a dummy signal,
plot signal with 2 frequencies, plot signal of 1 frequency when amp2 =
0
% set profit = 0 if first data point pmema is greater than 0
clear
factor = 6 ; % factor = 20.83, 9, 6.283 , 5, 9/2, 9/3, 9/4
%
check profit, 31.4, 15.7, 10.47, 7.85, 6.28
%
check profit, take approx 30, 15, 10, 8, 6
factor2 = factor/4 ;
omega = pi/factor;

omega2 = pi/factor2;
NN = 8 * factor; % NN = 8*factor
% define original signal
amp2 = 0 ; % 0.4
theta0 = pi/2 ; % add to price signal 0, pi/2, pi, 3*pi/2
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I) + theta0 ) + amp2*
sin( omega2*xvector(I) );
end
startpt =30; % 30
% set parameters of pmema
M1=1 ;
alpha1=2/(M1+1);
M2= 6 ;
alpha2=2/(M2+1);
% calculate technical indicators on signal
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
end
% To calculate buy price and sell price, and profit of pmema
B = 0; % Buy originally set to 0
Iprofit=1;
if
macdsignal(startpt)
greater than 0, we do not buy
Iprofit = 0;
end

> 0

% when first data point is

for I = startpt: NN+1
if B == 0 & macdsignal(I) > 0
I ,
ybuy = yvector(I)
B = 1
else
if B == 1
& macdsignal(I) < 0
I,
ysell = yvector(I)

switch Iprofit
case {0}
profit = 0
Iprofit=1;
case{1}
profit = ( (ysell - ybuy)/2 ) *100
end
B = 0
end
end
end
figure(1)
plot(xvector, yvector, 'kx-', xvector(startpt: NN+1),
ema1signal(startpt : NN+1), 'r+-', xvector(startpt:
NN+1),ema2signal(startpt : NN+1), 'b+-', xvector, zero, 'k' )
xlabel('t')
ylabel('price, ema1 of price, ema2 of price ') %ema1 of price = price
here
figure(2)
plot(xvector, yvector, 'kx-', xvector(startpt: NN+1),
macdsignal(startpt : NN+1), 'r+-', xvector, zero, 'k' )
xlabel('t')
ylabel('price, (price - ema of price ) ')
```


## D.26 pmsma


```matlab
% pmsma, Plot Amplitude and Phase of price minus simple moving average
of price
clear
NN=240; %240, 480
intomega=pi/NN;
M1=1 ; % 1, cf awesome 5
M2=10

%

10, 20, cf awesome 34

for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)=1/M1*( 1- exp(-i*M1*omegavector(I)) ) /( 1 exp(-i*omegavector(I) ) );
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));

H2vector(I)= 1/M2*( 1- exp(-i*M2*omegavector(I)) ) /( 1 exp(-i*omegavector(I) ) );
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));
phase2unwrapth(I) = - (M2 -1)/2 * omegavector(I); % theoretical
unwrapped phase, see Science of Financial Market Trading page 156

H3vector(I)= H1vector(I) - H2vector(I); % 3 = price - SMA of price
mag3(I)=abs(H3vector(I));
phase3(I)= angle(H3vector(I));

end

phase2unwrap = unwrap(phase2); % matlab function did not unwrap phase2,
and therefore has an error, see Fig 3 which compares phase2unwrap with
phase2unwrapth, the theoretical unwrapped phase
phaseunwrap = unwrap(phase3); % matlab function, phaseunwrap is exactly
the same as phase3, i.e., does not need to unwrap

mag(1) = 1;
phase1(1)=0;
mag2(1) = 1;
phase2(1)=0;
mag3(1) = 0;
phase3(1) = pi/2;

for I= 1: NN+1
barlag (I) = phase3(I)/omegavector(I);
end

figure(1)
plot(omegavector, mag1, 'k+-' , omegavector, mag2, 'kx-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Simple Moving Average')

figure(2)
plot(omegavector, phase1, 'k+-' , omegavector, phase2, 'kx-' )
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('Simple Moving Average')
figure(3)
plot(omegavector, phase2unwrap,'kx', omegavector, phase2unwrapth,
'r-' )
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('Simple Moving Average')
figure(4)
plot(omegavector, mag3, 'k-' )
xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title(' Price - SMA of Price ')
figure(5)
plot(omegavector, phase3, 'k-' )
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title(' Price - SMA of Price ')

figure(6)
plot(omegavector, phase3, 'k-' , omegavector, omegavector, 'k-'

)

xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title(' Price - SMA of Price ')

% to find intersection point of phase3 and omegavector
for I = 1: NN
if ( phase3(I) - omegavector(I) ) > 0 & ( phase3(I+1)
- omegavector(I+1) ) < 0
intersectomega = omegavector(I)
intersectphase =phase3(I)
end

if ( phase3(I) - omegavector(I) ) < 0 & ( phase3(I+1) -

omegavector(I+1) ) > 0 %for M2 large, e.g., M2 = 100, see text
intersectomeganegtopos = omegavector(I)
intersectphasenegtopos =phase3(I)
end
end
figure(7)
plot(omegavector, phase3, 'k.'

, omegavector, phaseunwrap,

'r-' ) % phaseunwrap = phase3
xlabel('Circular Frequency (radians)')
ylabel('Unwrapped Phase (radians)')
title(' Price - SMA of Price ')
figure(8)
plot(omegavector, barlag, 'k+-' )
xlabel('Circular Frequency (radians)')
ylabel('bars lag)')
title(' Price - SMA of Price ')
```


## D.27 pmsmapmema


```matlab
% pmsmapmema, Plot Amplitude and Phase of price minus simple moving
average of price and compare with Amplitude and Phase of price –
exponential moving average of price
clear
NN=240; %240, 480
intomega=pi/NN;
M1=1 ; % cf awesome 5
M2=20 ; % cf awesome 34
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)=1/M1*( 1- exp(-i*M1*omegavector(I)) ) /( 1 exp(-i*omegavector(I) ) );
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I));
H2vector(I)= 1/M2*( 1- exp(-i*M2*omegavector(I)) ) /( 1 exp(-i*omegavector(I) ) );
mag2(I)=abs(H2vector(I));
phase2(I)= angle(H2vector(I));

H3vector(I)= H1vector(I) - H2vector(I); % pmsma
mag3(I)=abs(H3vector(I)); % 3 = pmsma
phase3(I)= angle(H3vector(I));
end
mag(1) = 1;
phase1(1)=0;
mag2(1) = 1;
phase2(1)=0;
mag3(1) = 0;
phase3(1) = pi/2;
% calculate price - ema to compare with price - sma
M1=1; % cf MACD 12
alpha1=2/(M1+1);
M2=6 ; %cf MACD 26
alpha2=2/(M2+1);
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= alpha1/ ( 1-(1-alpha1)*exp(-i*omegavector(I)));
mag1e(I)=abs(H1vector(I));
phase1e(I)= angle(H1vector(I));
H2vector(I)= alpha2/ (1-(1-alpha2)*exp(-i*omegavector(I)));
mag2e(I)=abs(H2vector(I));
phase2e(I)= angle(H2vector(I));
H4vector(I) = H1vector(I) - H2vector(I); %pmema
mag4e(I)=abs(H4vector(I)); % mag4e = magnitude of pmema
phase4e(I)= angle(H4vector(I));
end
mag1e(1) = 1;
phase1e(1) = 0;
mag2e(1) = 1;
phase2e(1) = 0;
phase4e(1) = pi/2;
mag4e(1) = 0; % pmema
figure(1)
plot(omegavector, mag3, 'k-' , omegavector, mag4e, 'k+-' )
xlabel('Circular Frequency (radians)')
ylabel('Magnitude')
title(' Price - SMA of Price, Price - EMA of Price ')

figure(2)
plot(omegavector, phase3, 'k-' , omegavector, phase4e, 'k+-' )
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title(' Price - SMA of Price, Price - EMA of Price ')
```


## D.28 pmsmasig


```matlab
% % pmsmasig, plot price - sma of a dummy signal, plot signal with 2
frequencies, plot signal of 1 frequency when amp2 = 0
% set profit = 0 if first data point of (price - sma of price) is greater
than 0
clear
factor = 15 ; % factor = 30, 15, 10, 8, 6 check profit
%
check profit, 31.4, 15.7, 10.47, 7.85, 6.28
factor2 = factor/4 ;
omega = pi/factor;
omega2 = pi/factor2;
NN = 10 * factor; % NN = 8*factor, N2 = 100

NN = 20*factor

% define original signal
amp2 = 0 ; % 0.4
theta0 = pi/2 ; % add to price signal 0, pi/2, pi, 3*pi/2
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I) + theta0 ) + amp2*
sin( omega2*xvector(I) );
end
% set parameters of sma's
N1= 1;
N2=10 ; % 10, 20, 100
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2

sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate price - sma
of price
end
end
% To calculate buy price and sell price, and profit of (price - sma
of price)
B = 0; % Buy originally set to 0
Iprofit=1;
if
aweosc(N2)
not buy
Iprofit = 0;
end

> 0 % first data point greater than 0, we do

for I = N2: NN+1
if B == 0 & aweosc(I) > 0
I ,
ybuy = yvector(I)
B = 1
else
if B == 1
&
aweosc(I) < 0
I,
ysell = yvector(I)
switch Iprofit
case {0}
profit = 0
Iprofit=1;
case{1}
profit = ( (ysell - ybuy)/2 ) *100
end
B = 0
end
end
end
figure(1)
plot(xvector, yvector, 'kx-',

xvector(N2: NN+1), sma1signal(N2 :

NN+1), 'r+-', xvector(N2: NN+1),sma2signal(N2 : NN+1), 'b+-',
zero, 'k' )
xlabel('t')
ylabel('price, sma, sma')

xvector,

figure(2)
plot(xvector, yvector,'kx-', xvector(N2: NN+1), aweosc(N2 : NN+1),
'r+-', xvector, zero, 'k' )
xlabel('t')
ylabel('price, (price - sma of price ) ')
```


## D.29 sinecos


```matlab
% sinecos, plot price simulated by a sine wave and the slope of the price
with various phase lags from the price signal. The object of the exercise
is to show that whether profit or loss would be made when a velocity
indicator, which emulates the slope, has a phase lead or lag.
clear
t=40;
f=6/4;
for I= 1: f*t+1
xvector(I)= 0;
yvector(I)=0;
zvector(I)=0;
zero(I)=0;
end
const = 0; % 0 , 2
Acos = 1;% 0.8, usually 1
phaselagcos= pi/2; % pi/2, 0 , -pi/2, pi , -pi ;
for I = 1: f*t+1
xvector(I) = I-1;
yvector(I)= const + sin(pi/(t/2) * xvector(I));
zvector(I)= Acos* sin(pi/(t/2) * xvector(I) + phaselagcos) ; %
sin(omega + pi/2 ) = cos(omega)
end
figure(1)
plot(xvector, yvector , 'r', xvector, zvector, 'b', xvector,
zero , 'k')
xlabel('t')
ylabel('price, velocity')
```


## D.30 sma


```matlab
% sma, Plot Amplitude and Phase (wrapped and unwrapped) and bar lag (of
unwrapped phase) of a simple moving average
clear
NN=180; %N = 10, NN = 500
%N = 100, NN = 1000

intomega=pi/NN;
N = 10; % 6, 100, 50, 20
for I= 1: NN+1
omegavector(I) = (I-1)*intomega;
H1vector(I)= (1/N)*( 1 - exp(-i* N *omegavector(I)))/ (1 - exp (-i
* omegavector(I))) ;
mag1(I)=abs(H1vector(I));
phase1(I)= angle(H1vector(I)); % wrapped phase
phase2(I) = - (N-1)/2 * omegavector(I); % unwrapped phase, Science
of financial market trading P156
barlag(I) = phase2(I) / omegavector(I);
end
H1vector(1)= 1 ;
mag1(1)=abs(H1vector(1));
phase1(1)= angle(H1vector(1)); % wrapped phase
phaseunwrap = unwrap(phase1);% here MATLAB unwrap function does not do
any unwrapping
figure(1)
subplot(1, 1, 1)
plot(omegavector, mag1, 'k-'

)

xlabel('Circular Frequency (radians)')
ylabel('Amplitude')
title('Simple Moving Average')
figure(2)
subplot(1, 1, 1)
plot(omegavector, phase1, 'k+-'

)

xlabel('Circular Frequency (radians)')
ylabel('Wrapped Phase (radians)')
title('Simple Moving Average')
figure(3)
subplot(1, 1, 1)
plot(omegavector, phase2, 'k-'

, omegavector, phaseunwrap,

'r+' )
xlabel('Circular Frequency (radians)')
ylabel('Phase (radians)')
title('Simple Moving Average')

figure(4)
subplot(1, 1, 1)
plot(omegavector, barlag, 'r-' )
xlabel('Circular Frequency (radians)')
ylabel('bar lag')
title('Simple Moving Average')
```


## D.31 smasig


```matlab
% smasig, plot sma of signal
clear
factor =

20;

omega = pi/factor;
NN = 4 * factor;
N = 20; % N = number of data points used
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I));
end
for I = N: NN+1
smasignal(I) = 0;
for J = 1:N
smasignal(I) = smasignal(I ) + 1/N * yvector(I+1 - J);
end
end
figure(1)
plot(xvector, yvector, 'kx-', xvector(N: NN+1), smasignal(N :
NN+1), 'k+-',

xvector, zero, 'k' )

xlabel('n')
ylabel('price, sma of price')
```


## D.32 smasig2


```matlab
% smasig2, plot sma of signal with 2 frequencies, plot signal of 1
frequency when amp2 = 0
% fig 2 plots unwrapped phase

clear
factor = 9/2 ; % for N =10,factor = 20.83, 9, 6.283 , 5, 9/2, 9/3, 9/4
% N = 10, check profit, 31.4, 15.7, 10.47, 7.85, 6.28
% N = 10 check profit, take approx 30, 15, 10, 8, 6
theta0 = 0 ; % add to price signal
% for N = 100, factor = 99, 66,

0, pi/2 pi, 3*pi/2

99/2

factor2 = 15;
omega = pi/factor;
omega2 = pi/factor2;
NN = 8*factor ; % for N = 10 NN = 8*factor
% for N = 100 NN = 20*factor
N = 10; % N = number of data points used in SMA, N = 10, 100
amp2 = 0; % 0.4
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= sin( omega*xvector(I)

+ theta0 ) + amp2*

sin( omega2*xvector(I) );
end
% To calculate buy price and sell price, and profit
B = 0; % Buy originally set to 0
for I = N: NN+1
smasignal(I) = 0;
for J = 1:N
smasignal(I) = smasignal(I ) + 1/N * yvector(I+1 - J);
end
if

B == 0 &

I ,

( yvector(I) - smasignal(I)

) > 0

ybuy = yvector(I)

B = 1
else
if B == 1
I,

&

(

yvector(I) - smasignal(I)

ysell = yvector(I)

profit = ( (ysell - ybuy)/2 ) *100
B = 0
end
end
end

) < 0

figure(1)
plot(xvector, yvector, 'kx-', xvector(N: NN+1), smasignal(N :

NN+1), 'k+-',

xvector, zero, 'k' )

xlabel('t')
% calculate unwrapped phase
sign = 1;
if factor == 9/2 | factor == 9/3 % | is or
sign = -1;
end
for I = N: NN+1
smasignalunwrap(I) = sign *smasignal(I) ;
end
% plot price signal and sma of price signal with wrapped
and unwrapped phase
figure(2)
plot(xvector, yvector, 'kx-', xvector(N: NN+1), smasignal(N :
NN+1), 'k+-',

xvector(N: NN+1), smasignalunwrap(N : NN+1), 'ro',

xvector, zero, 'k' )
xlabel('t')
ylabel('price, sma of price')
ylabel('price, sma of price')
```


## D.33 tradeartif


```matlab
% tradeartif,

trade an artificial signal using different trading

tactics
% artificial data, 1 sine wave
or sum of 2 sine waves, e.g., factor = 25 ; theta0 = pi ; factor2
= 4 ; NN = 120; amp2 = 0.3

;

amp2 = 0.9

%simulate CAC40, factor=8, factor2 = 3
% n = 0 to
clear
tactic = 12 ; %
% tactic = 1, sma1msma10
% tactic = 2, sma1msma20

% tactic = 3

awesome oscillator

% tactic = 4, accelerator oscillator
% tactic = 5, MACD
% tactic = 6, MACDH
% tactic = 7, MACDH1
% tactic = 8 , price - ema3 of price
% tactic = 9 , price - ema6 of price
% tactic = 10 , ema3 of price - ema6 of price
% tactic = 11 , emaaccel
% tactic = 12 , sine wave with a phase delay to check sampling loss

thetashift =

pi/12 ; % thetashift = arbitrary phase shift of filtered

price signal= phi in buysellprice
startpt = 1;
amp1 = 1 ;
factor = 6 ; % 30, 20,
% N = 10, check profit, 31.4, 15.7, 10.47, 7.85, 6.28
% N = 10 check profit, take approx 30, 15, 10, 8, 6
mu = pi/24 ;% mu to emulate sampling delay,
factor2 = 3 ; % 3, 4, 5, 3 will get more loss trades
omega = pi/factor;
theta0 = omega - mu

; % theta0 can also be set to a certain constant,

e.g., 0, pi/2, pi
amp2 = 0. ; % 0.3, 0.4, 0.2, 0.25
omega2 = pi/factor2;
NN = 20; %6 * factor; % for N = 10 NN = 8*factor, 120, 20 for tactic
= 12, cf 80 for real data
% for N = 100 NN = 20*factor
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
yvector(I)= amp1* sin( omega*xvector(I)
sin( omega2*xvector(I) );
end
% NN = length(yvector) - 1
maxprice = max(yvector)
minprice = min(yvector)
range=maxprice-minprice

+ theta0 ) + amp2*

for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
switch tactic
case (1)
% set parameters of price - simple moving average with N = 10
N1= 1;
N2=10;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma10(I) = sma1signal(I) - sma2signal(I); % calculate

price -

sma10
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma10(I);
end
startpt = N2;
case (2)
% set parameters of price - simple moving average with N = 20
N1= 1;
N2=20;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;

for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma(I) = sma1signal(I) - sma2signal(I); % calculate

price - sma10

techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma(I);
end
startpt = N2;
case (3)
% set parameters of awesome oscillator
N1= 5;
N2=34;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = aweosc(I);
end
startpt = N2

case(4) % accelerator oscillator
% set parameters of awesome oscillator and accelerator oscillator
N1= 5;
N2=34;
N3=5;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator
end
N2PN3 = N2+N3;
for I = N2PN3 : NN+1
signalline(I) = 0;
for J = 1:N3
signalline(I) = signalline(I ) + 1/N3 * aweosc(I+1 - J);
end
end
for I = N2PN3 : NN+1
accelosc (I) = aweosc(I) - signalline(I); %calculate acelerator
oscillator
techsignal1(I) = aweosc(I);
techsignal2(I) = signalline(I);
techsignal(I) = accelosc(I);
end
startpt = N2PN3
case(5)
% tactic = 5, calculate MACD
M1=12;
alpha1=2/(M1+1);

M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(6)
% tactic = 6, calculate MACDH
M1=12;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);

ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
case(7)
% tactic = 7, calculate MACDH1
M1=1;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
case(8)
% tactic = 8, calculate price minus ema3 of price
M1=1;

alpha1=2/(M1+1);
M2= 3;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(9)
% tactic = 9, calculate price minus ema6 of price
M1=1;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end

case(10)
% tactic = 10, calculate ema3 of price minus ema6 of price
M1=3;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(11)
% tactic = 11, calculate emaaccel = (ema3 - ema6) - ema9(ema3 - ema6)
M1=3 ;
alpha1=2/(M1+1);
M2= 6 ;
alpha2=2/(M2+1);
M3=9 ;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);

macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
case(12)
% sine wave with a phase delay to check sampling loss
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
techsignal(I) = amp1 *sin( omega*xvector(I) + theta0 +
thetashift ) + amp2* sin( omega2*xvector(I) );
end
% theoretical calculation
buytheor = sin ( (fix ( (2*pi - theta0 - thetashift)/omega) +1) * omega
+ theta0 )
selltheor= -buytheor
profittheor = selltheor - buytheor
end
end
% To calculate buy price and sell price, and profit of a trading tactic
B = 0; % Buy originally set to 0
totalB = 0;
totalS= 0; %total number of times to sell
profit = 0; % set original profit = 0
for I = startpt: NN
if

B == 0

& (techsignal(I) < 0

& techsignal(I + 1) > 0 )

B = 1;
totalB = totalB + B
I ,
here,

ybuy = yvector(I + 1) %

n in Figure equal to I printed

e.g., n=19 is equivalent to I+1=20

Bvector(totalB) = I ; % not I +1
profitvectorB (totalB) = profit;
else
if B == 1

&

( techsignal(I) > 0

& techsignal(I + 1) <

0 )
I ,

ysell = yvector(I + 1)

totalS = totalS + B; % Number of times of selling
profitloss(totalS) = ysell - ybuy ; % calculate profit/loss

of each trade
profit = profit + (ysell - ybuy)
Svector(totalS) = I ; % not I +1
profitvectorS(totalS) = profit;
B=0;
end
end
end
'Number of times selling', totalS
profitpercentage = profit/2 * 100
figure(1)
subplot(2,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price')
title (' Artificial data ')
subplot(2,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel(' n ')
switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA100 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')

case(11)
ylabel('emaaccel')
case(12)
ylabel('arbitrary filtered price')
end
figure(2)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' Artificial data ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k+-',
xvector, zero, 'k' )
xlabel(' ')
switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
case(12)
ylabel('arbitrary filtered price')
end

subplot(3,1, 3)

plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' , xvector, zero, 'k' )
xlabel('n')
ylabel('total profit ')
title ('

')

figure(3)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' Artificial data ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k+-',
xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')

case(12)
ylabel('arbitrary filtered price')
end
subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' ,

Svector, profitloss, 'go' , xvector, zero, 'k' )

xlabel('n')
ylabel('T profit,profit/trade')
title ('

')
```


## D.34 tradecac40


```matlab
% tradecac40,

trade CAC 40 index using different trading tactics

clear
tactic = 8

; %

% tactic = 1, sma1msma10
% tactic = 2, sma1msma20
% tactic = 3

awesome oscillator

% tactic = 4, accelerator oscillator
% tactic = 5, MACD
% tactic = 6, MACDH
% tactic = 7, MACDH1
% tactic = 8 , price - ema3 of price
% tactic = 9 , price - ema6 of price
% tactic = 10 , ema3 of price - ema6 of price
% tactic = 11 , emaaccel
% CAC 40 from March 6, 2019 to Aug 21, 2019, 118 data points
yvector = [ 5288 5267 5231 5265 5270 5306 5349 5405 5412 5425
5382 5378 5269 5260 5307 5301 5296 5350 5405 5423 5468 5463
5476 5471 5436 5449 5485 5502 5508 5528 5563 5580 5591 5576
5557 5569 5580 5586 5538 5548 5483 5395 5417 5313 5327 5262
5341 5374 5448 5438 5358 5385 5378 5281 5316 5336 5312 5222
5248 5207 5241 5268 5292 5278 5364 5382 5408 5374 5375 5367
5390 5509 5518 5535 5528 5521 5514 5500 5493 5538 5567 5576
5618 5620 5593 5589 5572 5567 5551 5572 5578 5614 5571 5550
5552 5567 5618 5505 5578 5610 5601 5511 5618 5557 5359 5241
5234 5266 5387 5327 5310 5363 5251 5236 5300 5371 5344
5435

];

NN = 117;
% NN = length(yvector) - 1
maxprice = max(yvector)
minprice = min(yvector)
range=maxprice-minprice
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
switch tactic
case (1)
% set parameters of price - simple moving average with N = 10
N1= 1;
N2=10;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma10(I) = sma1signal(I) - sma2signal(I); % calculate

price -

sma10
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma10(I);
end
startpt = N2;
case (2)
% set parameters of price - simple moving average with N = 20
N1= 1;
N2=20;

% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma(I) = sma1signal(I) - sma2signal(I); % calculate

price - sma10

techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma(I);
end
startpt = N2;
case (3)
% set parameters of awesome oscillator
N1= 5;
N2=34;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end

for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = aweosc(I);
end
startpt = N2
case(4) % accelerator oscillator
% set parameters of awesome oscillator and accelerator oscillator
N1= 5;
N2=34;
N3=5;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator
end
N2PN3 = N2+N3;
for I = N2PN3 : NN+1
signalline(I) = 0;
for J = 1:N3
signalline(I) = signalline(I) + 1/N3 * aweosc(I+1 - J);
end
end

for I = N2PN3 : NN+1
accelosc (I) = aweosc(I) - signalline(I); %calculate acelerator
oscillator
techsignal1(I) = aweosc(I);
techsignal2(I) = signalline(I);
techsignal(I) = accelosc(I);
end
startpt = N2PN3
case(5)
% tactic = 5, calculate MACD
M1=12;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(6)
% tactic = 6, calculate MACDH
M1=12;
alpha1=2/(M1+1);

M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
case(7)
% tactic = 7, calculate MACDH1
M1=1;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);

ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
case(8)
% tactic = 8, calculate price minus ema3 of price
M1=1;
alpha1=2/(M1+1);
M2= 3;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(9)
% tactic = 9, calculate price minus ema6 of price
M1=1;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;

ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(10)
% tactic = 10, calculate ema3 of price minus ema6 of price
M1=3;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(11)
% tactic = 11, calculate emaaccel = (ema3 - ema6) - ema9(ema3 - ema6)
M1=3 ;

alpha1=2/(M1+1);
M2= 6 ;
alpha2=2/(M2+1);
M3=9 ;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
end
% To calculate buy price and sell price, and profit of a trading tactic
B = 0; % Buy originally set to 0
totalB = 0;
totalS= 0; %total number of times to sell
profit = 0; % set original profit = 0
for I = startpt: NN
if

B == 0

& (techsignal(I) < 0

& techsignal(I + 1) > 0 )

B = 1;
totalB = totalB + B
I ,
ybuy = yvector(I + 1) %
here,

n in Figure equal to I printed

e.g., n=19 is equivalent to I+1=20

Bvector(totalB) = I ; % not I +1
profitvectorB (totalB) = profit;
else

if B == 1

&

( techsignal(I) > 0

& techsignal(I + 1) <

0 )
I ,

ysell = yvector(I + 1)

totalS = totalS + B; % Number of times of selling
profitloss(totalS) = ysell - ybuy ; % calculate profit/loss
of each trade
profit0 = ysell - ybuy
profit = profit + (ysell - ybuy)
Svector(totalS) = I ; % not I +1
profitvectorS(totalS) = profit;
B=0;
end
end
end
'Number of times selling', totalS
profitpercentage = profit/(maxprice - minprice) * 100
figure(1)
subplot(2,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price')
title (' CAC40 ')
subplot(2,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel(' n ')
switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA100 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')

case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
figure(2)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' CAC40 ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')

case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' , xvector, zero, 'k' )
xlabel('n')
ylabel('total profit ')
title ('

')

figure(3)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' CAC40 ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')

case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' ,

Svector, profitloss, 'go' , xvector, zero, 'k' )

xlabel('n')
ylabel('T profit,profit/trade')
title ('

')
```


## D.35 tradefhtse


```matlab
% tradeftse,

trade FTSE index using different trading tactics

clear
tactic = 6 ; %
% tactic = 1, sma1msma10
% tactic = 2, sma1msma20
% tactic = 3 awesome oscillator
% tactic = 4, accelerator oscillator
% tactic = 5, MACD
% tactic = 6, MACDH
% tactic = 7, MACDH1
% tactic = 8 , price - ema3 of price
% tactic = 9 , price - ema6 of price
% tactic = 10 , ema3 of price - ema6 of price
% tactic = 11 , emaaccel
% FTSE

from March 1, 19 ro Aug 14, 19

yvector = [

NN =114, 115 data points

7106 7134 7183 7196 7157 7104 7130 7151 7159

7185 7228 7299 7324 7291 7355 7207 7177 7196 7194 7234 7279
7317 7391 7418 7401 7446 7451 7425 7421 7418 7437 7436 7469
7471 7459 7523 7471 7434 7428 7440 7418 7385 7351

7380 7260

7271 7207 7203 7163 7241 7297 7353 7348 7310 7328 7334 7231
7277 7269 7185 7218 7161 7184 7214 7220 7259 7331 7375 7398
7367 7368 7345 7357 7443 7403 7424 7407 7416 7422 7416 7402
7425 7497 7559 7609 7603 7553 7549 7536 7530 7509 7506 7531
7577 7535 7493 7508 7514 7556 7501 7489 7549 7686

7645 7586

7584 7407 7223 7171 7198 7285 7253 7226 7250 7147

];

NN = 114;
% NN = length(yvector) - 1
maxprice = max(yvector)
minprice = min(yvector)
range=maxprice-minprice
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
switch tactic
case (1)
% set parameters of price - simple moving average with N = 10
N1= 1;
N2=10;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma10(I) = sma1signal(I) - sma2signal(I); % calculate

price -

sma10
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma10(I);
end
startpt = N2;
case (2)
% set parameters of price - simple moving average with N = 20
N1= 1;
N2=20;

% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma(I) = sma1signal(I) - sma2signal(I); % calculate

price - sma10

techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma(I);
end
startpt = N2;
case (3)
% set parameters of awesome oscillator
N1= 5;
N2=34;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator

techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = aweosc(I);
end
startpt = N2

case(4) % accelerator oscillator
% set parameters of awesome oscillator and accelerator oscillator
N1= 5;
N2=34;
N3=5;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator
end
N2PN3 = N2+N3;
for I = N2PN3 : NN+1
signalline(I) = 0;
for J = 1:N3
signalline(I) = signalline(I ) + 1/N3 * aweosc(I+1 - J);
end
end
for I = N2PN3 : NN+1
accelosc (I) = aweosc(I) - signalline(I); %calculate acelerator
oscillator
techsignal1(I) = aweosc(I);
techsignal2(I) = signalline(I);
techsignal(I) = accelosc(I);
end

startpt = N2PN3
case(5)
% tactic = 5, calculate MACD
M1=12;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(6)
% tactic = 6, calculate MACDH
M1=12;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);

for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
case(7)
% tactic = 7, calculate MACDH1
M1=1;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end

case(8)
% tactic = 8, calculate price minus ema3 of price
M1=1;
alpha1=2/(M1+1);
M2= 3;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(9)
% tactic = 9, calculate price minus ema6 of price
M1=1;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end

case(10)
% tactic = 10, calculate ema3 of price minus ema6 of price
M1=3;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(11)
% tactic = 11, calculate emaaccel = (ema3 - ema6) - ema9(ema3 - ema6)
M1=3 ;
alpha1=2/(M1+1);
M2= 6 ;
alpha2=2/(M2+1);
M3=9 ;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);

ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
end
% To calculate buy price and sell price, and profit of a trading tactic
B = 0; % Buy originally set to 0
totalB = 0;
totalS= 0; %total number of times to sell
profit = 0; % set original profit = 0
for I = startpt: NN
if

B == 0

& (techsignal(I) < 0

& techsignal(I + 1) > 0 )

B = 1;
totalB = totalB + B
I ,
here,

ybuy = yvector(I + 1) %

n in Figure equal to I printed

e.g., n=19 is equivalent to I+1=20

Bvector(totalB) = I ; % not I +1
profitvectorB (totalB) = profit;
else
if B == 1

&

( techsignal(I) > 0

& techsignal(I + 1) <

0 )
I ,

ysell = yvector(I + 1)

totalS = totalS + B; % Number of times of selling
profitloss(totalS) = ysell - ybuy ; % calculate profit/loss
of each trade
profit0 = ysell - ybuy
profit = profit + (ysell - ybuy)
Svector(totalS) = I ; % not I +1
profitvectorS(totalS) = profit;
B=0;
end
end
end
'Number of times selling', totalS
profitpercentage = profit/(maxprice - minprice) * 100

figure(1)
subplot(2,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price')
title (' FTSE 100 ')
subplot(2,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',

xvector, zero, 'k' )
xlabel(' n ')
switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA100 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
figure(2)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' FTSE 100 ')
subplot(3,1, 2)

plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' , xvector, zero, 'k' )
xlabel('n')
ylabel('total profit ')
title ('

')

figure(3)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' FTSE 100 ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',

xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' ,

Svector, profitloss, 'go' , xvector, zero, 'k' )

xlabel('n')
ylabel('T profit,profit/trade')
title ('

')
```


## D.36 tradehangseng


```matlab
% tradehangseng,

trade Hang Seng index using different trading tactics

clear
tactic = 2

; %6, cf 9

% tactic = 1, sma1msma10
% tactic = 2, sma1msma20
% tactic = 3

awesome oscillator

% tactic = 4, accelerator oscillator
% tactic = 5, MACD
% tactic = 6, MACDH
% tactic = 7, MACDH1
% tactic = 8 , price - ema3 of price
% tactic = 9 , price - ema6 of price
% tactic = 10 , ema3 of price - ema6 of price
% tactic = 11 , emaaccel
NN = 107; % Hang seng from March 1, 2019 to Aug 12, 2019, 108 data points
yvector = [ 28812 28959 28961 29037 28779 28228 28503 28920
28807 28851 29012 29409 29466 29320 29071 29113 28523 28567
28728 28775 29051 29562 29624 29986 29936 30077 30157 30119
29839 29909 29810 30129 30124 29963 29963 29805 29549 29605
29892 29699 29209 29363 29003 28311 28550 28122 28268 28275
27946 27787 27657 27705 27267 27353 27268 27390 27235 27114
26901 26893 26761 26895 26965 27578 27789 27308 27294 27118
27227 27498 28202 28550 28473 28513 28185 28221 28621
28875 28855 28795 28774 28331 28116 28204

28542

28431 28471 28554

28619 28593 28461 28765 28371 28466 28524 28594 28397 28106
28146 27777 27505 26918 26151 25976 25997 26120 25939 25824 ];
% NN = length(yvector) - 1
maxprice = max(yvector)
minprice = min(yvector)
range=maxprice-minprice
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
switch tactic
case (1)
% set parameters of price - simple moving average with N = 10
N1= 1;
N2=10;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end

for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end

end
for I = N2 : NN+1
pmsma10(I) = sma1signal(I) - sma2signal(I); % calculate

price -

sma10
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma10(I);
end
startpt = N2;
case (2)
% set parameters of price - simple moving average with N = 20
N1= 1;
N2=20;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma(I) = sma1signal(I) - sma2signal(I); % calculate
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma(I);
end
startpt = N2;

price - sma10

case (3)
% set parameters of awesome oscillator
N1= 5;
N2=34;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = aweosc(I);
end
startpt = N2
case(4) % accelerator oscillator
% set parameters of awesome oscillator and accelerator oscillator
N1= 5;
N2=34;
N3=5;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end

for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome

oscillator
end
N2PN3 = N2+N3;
for I = N2PN3 : NN+1
signalline(I) = 0;
for J = 1:N3
signalline(I) = signalline(I ) + 1/N3 * aweosc(I+1 - J);
end
end
for I = N2PN3 : NN+1
accelosc (I) = aweosc(I) - signalline(I); %calculate acelerator
oscillator
techsignal1(I) = aweosc(I);
techsignal2(I) = signalline(I);
techsignal(I) = accelosc(I);
end
startpt = N2PN3
case(5)
% tactic = 5, calculate MACD
M1=12;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);

for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(6)
% tactic = 6, calculate MACDH
M1=12;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end

case(7)
% tactic = 7, calculate MACDH1
M1=1;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
case(8)
% tactic = 8, calculate price minus ema3 of price
M1=1;
alpha1=2/(M1+1);
M2= 3;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);

ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(9)
% tactic = 9, calculate price minus ema6 of price
M1=1;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(10)
% tactic = 10, calculate ema3 of price minus ema6 of price
M1=3;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);

for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(11)
% tactic = 11, calculate emaaccel = (ema3 - ema6) - ema9(ema3 - ema6)
M1=3 ;
alpha1=2/(M1+1);
M2= 6 ;
alpha2=2/(M2+1);
M3=9 ;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
end

% To calculate buy price and sell price, and profit of a trading tactic
B = 0; % Buy originally set to 0
totalB = 0;
totalS= 0; %total number of times to sell
profit = 0; % set original profit = 0
for I = startpt: NN
if

B == 0

& (techsignal(I) < 0

& techsignal(I + 1) > 0 )

B = 1;
totalB = totalB + B
I ,
here,

ybuy = yvector(I + 1) %

n in Figure equal to I printed

e.g., n=19 is equivalent to I+1=20

Bvector(totalB) = I ; % not I +1
profitvectorB (totalB) = profit;
else
if B == 1

&

( techsignal(I) > 0

& techsignal(I + 1) <

0 )
I ,

ysell = yvector(I + 1)

totalS = totalS + B; % Number of times of selling
profitloss(totalS) = ysell - ybuy ; % calculate profit/loss
of each trade
profit0 = ysell - ybuy
profit = profit + (ysell - ybuy)
Svector(totalS) = I ; % not I +1
profitvectorS(totalS) = profit;
B=0;
end
end
end
'Number of times selling', totalS
profitpercentage = profit/(maxprice - minprice) * 100
figure(1)
subplot(2,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price')
title (' Hang Seng ')
subplot(2,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )

xlabel(' n ')
switch tactic
case(1)

ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA100 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
figure(2)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' Hang Seng ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )

case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' , xvector, zero, 'k' )
xlabel('n')
ylabel('total profit ')
title ('

')

figure(3)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' Hang Seng ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )

case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')

case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' ,

Svector, profitloss, 'go' , xvector, zero, 'k' )

xlabel('n')
ylabel('T profit,profit/trade')
title ('

')
```


## D.37 tradesp500


```matlab
% tradesp500,
%

S&P500

trade S & P 500 index using different trading tactics

from April 24, 19 to Aug 12, 19

% n = 0 corresponds to April 24, 19, n = 76 corresponds to Aug 12. 19
clear
tactic = 1 ; %
% tactic = 1, sma1msma10
% tactic = 2, sma1msma20
% tactic = 3

awesome oscillator

% tactic = 4, accelerator oscillator
% tactic = 5, MACD
% tactic = 6, MACDH

% tactic = 7, MACDH1
% tactic = 8 , price - ema3 of price
% tactic = 9 , price - ema6 of price
% tactic = 10 , ema3 of price - ema6 of price
% tactic = 11 , emaaccel

NN = 76; % S& P500 from April 24, 2019 to Aug 12, 2019, 77 data points
% NN = Number of data points - 1
yvector = [2927.25 2926.17 2939.88 2943.03 2945.83 2923.73
2917.52 2945.64 2932.47 2884.05 2879.42 2870.72 2881.40 2811.87
2834.41 2850.96 2876.32 2859.53 2840.23 2864.36 2856.27 2822.24
2826.06 2802.39 2783.02 2788.86 2752.06 2744.45 2803.27 2826.15
2843.49 2873.34 2886.73 2885.72 2879.84 2891.64 2886.98 2889.67
2917.75 2926.46 2954.18 2950.46 2945.35 2917.38 2913.78 2924.92
2941.76 2964.33 2973.01 2995.82 2990.41 2975.95

2979.63

2993.07 2999.91 3013.77 3014.30 3004.04 2984.42 2995.11 2976.61
2995.03 3005.47 3019.56 3003.67 3025.86 3020.97 3013.18 2980.38
2953.56 2932.05 2844.74 2881.77 2883.98 2938.09 2918.65
2882.70 ];
% NN = length(yvector) - 1
maxprice = max(yvector)
minprice = min(yvector)
range=maxprice-minprice
for I= 1: NN+1
zero(I)=0;
xvector(I) = I-1;
end
switch tactic
case (1)
% set parameters of price - simple moving average with N = 10
N1= 1;
N2=10;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end

for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma10(I) = sma1signal(I) - sma2signal(I); % calculate

price -

sma10
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma10(I);
end
startpt = N2;
case (2)
% set parameters of price - simple moving average with N = 20
N1= 1;
N2=20;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
pmsma(I) = sma1signal(I) - sma2signal(I); % calculate
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = pmsma(I);
end

price - sma10

startpt = N2;
case (3)
% set parameters of awesome oscillator
N1= 5;
N2=34;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome
oscillator
techsignal1(I) = sma1signal(I);
techsignal2(I) = sma2signal(I);
techsignal(I) = aweosc(I);
end
startpt = N2
case(4) % accelerator oscillator
% set parameters of awesome oscillator and accelerator oscillator
N1= 5;
N2=34;
N3=5;
% calculate technical indicators on signal
for I = N1 : NN+1
sma1signal(I) = 0;
for J = 1:N1
sma1signal(I) = sma1signal(I ) + 1/N1 * yvector(I+1 - J);
end
end

for I = N2 : NN+1
sma2signal(I) = 0;
for J = 1:N2
sma2signal(I) = sma2signal(I ) + 1/N2 * yvector(I+1 - J);
end
end
for I = N2 : NN+1
aweosc(I) = sma1signal(I) - sma2signal(I); % calculate awesome

oscillator
end
N2PN3 = N2+N3;
for I = N2PN3 : NN+1
signalline(I) = 0;
for J = 1:N3
signalline(I) = signalline(I ) + 1/N3 * aweosc(I+1 - J);
end
end
for I = N2PN3 : NN+1
accelosc (I) = aweosc(I) - signalline(I); %calculate acelerator
oscillator
techsignal1(I) = aweosc(I);
techsignal2(I) = signalline(I);
techsignal(I) = accelosc(I);
end
startpt = N2PN3
case(5)
% tactic = 5, calculate MACD
M1=12;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;

ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(6)
% tactic = 6, calculate MACDH
M1=12;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);

macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);

end
case(7)
% tactic = 7, calculate MACDH1
M1=1;
alpha1=2/(M1+1);
M2= 26;
alpha2=2/(M2+1);
M3=9;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
case(8)
% tactic = 8, calculate price minus ema3 of price
M1=1;
alpha1=2/(M1+1);
M2= 3;
alpha2=2/(M2+1);

startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(9)
% tactic = 9, calculate price minus ema6 of price
M1=1;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);
startpt = 15;

ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);

for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end

case(10)
% tactic = 10, calculate ema3 of price minus ema6 of price
M1=3;
alpha1=2/(M1+1);
M2= 6;
alpha2=2/(M2+1);

startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
techsignal1(I) = ema1signal(I);
techsignal2(I) = ema2signal(I);
techsignal(I) = macdsignal(I);
end
case(11)
% tactic = 11, calculate emaaccel = (ema3 - ema6) - ema9(ema3 - ema6)
M1=3 ;
alpha1=2/(M1+1);
M2= 6 ;
alpha2=2/(M2+1);
M3=9 ;
alpha3=2/(M3+1);
startpt = 15;
ema1signal(1) = yvector(1);
ema2signal(1) = yvector(1);
macdsignal(1) = ema1signal(1) - ema2signal(1);
ema3macd(1) = macdsignal(1);

for I = 2: NN+1
ema1signal(I) = alpha1 * yvector(I) + (1 - alpha1) * ema1signal(I
- 1);
ema2signal(I) = alpha2 * yvector(I) + (1 - alpha2) * ema2signal(I
- 1);
macdsignal(I) = ema1signal(I) - ema2signal(I);
ema3macd(I) = alpha3 * macdsignal(I) + (1 - alpha3) * ema3macd(I
- 1);
macdhsignal(I) = macdsignal(I) - ema3macd(I);
techsignal1(I) = macdsignal(I);
techsignal2(I) = ema3macd(I);
techsignal(I) = macdhsignal(I);
end
end
% To calculate buy price and sell price, and profit of a trading tactic
B = 0; % Buy originally set to 0
totalB = 0;
totalS= 0; %total number of times to sell
profit = 0; % set original profit = 0
for I = startpt: NN
if

B == 0

& (techsignal(I) < 0

& techsignal(I + 1) > 0 )

B = 1;
totalB = totalB + B
I ,
here,

ybuy = yvector(I + 1) %

n in Figure equal to I printed

e.g., n=19 is equivalent to I+1=20

Bvector(totalB) = I ; % not I +1
profitvectorB (totalB) = profit;
else
if B == 1

&

( techsignal(I) > 0

& techsignal(I + 1) <

0 )
I ,

ysell = yvector(I + 1)

totalS = totalS + B; % Number of times of selling
profitloss(totalS) = ysell - ybuy ; % calculate profit/loss
of each trade

profit0 = ysell - ybuy
profit = profit + (ysell - ybuy)
Svector(totalS) = I ; % not I +1
profitvectorS(totalS) = profit;
B=0;
end
end
end

'Number of times selling', totalS
profitpercentage = profit/(maxprice - minprice) * 100
figure(1)
subplot(2,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel('n')
ylabel('price')
title (' S & P500 ')
subplot(2,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel(' n ')
switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA100 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')

case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end

figure(2)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' S & P500 ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )
case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')

case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')

case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end
subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' , xvector, zero, 'k' )
xlabel('n')
ylabel('total profit ')
title ('

')

figure(3)
subplot(3,1, 1)
plot(xvector, yvector, 'k+-' )
xlabel(' ')
ylabel('price')
title (' S & P500 ')
subplot(3,1, 2)
plot( xvector(startpt : NN+1), techsignal(startpt : NN+1), 'k.-',
xvector, zero, 'k' )
xlabel('

')

switch tactic
case(1)
ylabel(' price - SMA10 of price' )
case(2)
ylabel(' price - SMA20 of price' )
case(3)
ylabel('awesome osc of price' )
case(4)
ylabel('accel osc of price' )

case(5)
ylabel('MACD of price')
case(6)
ylabel('MACDH of price')
case(7)
ylabel(' MACDH1 of price')
case(8)
ylabel('price - ema3 of price')
case(9)
ylabel('price - ema6 of price')
case(10)
ylabel('ema3 of price - ema6 of price')
case(11)
ylabel('emaaccel')
end

subplot(3,1, 3)
plot( Bvector, profitvectorB, 'kx' , Svector, profitvectorS,
'k+' ,

Svector, profitloss, 'go' , xvector, zero, 'k' )

xlabel('n')
ylabel('T profit,profit/trade')
title ('

')
```


## D.38 unsure


```matlab
%unsure, to plot profit percentage versus mu, the phase shift of the price
signal due to sampling.
clear
% omega and phi are given
omega = pi/6
phi =

pi/4

% phi = phase lead of velocity indicator, e.g., pi/2

N = 1440;
NN = 2*N;
piint = 2*pi/NN;

for I= 1: NN+1
zero(I)=0;
muvector(I) = -pi +(I-1)*piint;
theta0vector(I) = omega - muvector(I);
nbuyvector(I) = fix( (2*pi - theta0vector(I) - phi)/omega ) + 1 ;
buypricevector(I) = sin ( nbuyvector(I) *omega +
theta0vector(I) ) ;
profitvector(I)= -2*buypricevector(I);
profitpervector(I) = profitvector(I)/2*100;
end

%draw figure
figure(1)
subplot(1,1, 1)

plot ( muvector, zero, 'k-', muvector, profitpervector, 'k.-' )
xlabel(' mu ')
ylabel(' profit percentage ')
title (' Artificial data ')

```
