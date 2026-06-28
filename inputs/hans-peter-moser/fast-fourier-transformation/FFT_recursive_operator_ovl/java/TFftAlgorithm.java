
 public class TFftAlgorithm
 {
	 public int N;
	 public double[] xw;
	 public TComplex[] y, x;
	 public TComplex[] we;

	 public TComplex ksum(TComplex a, TComplex b)
	 {
		 TComplex res = new TComplex();
		 res.real = a.real + b.real;
		 res.imag = a.imag + b.imag;
		 return (res);
	 }

	 public TComplex kdiff(TComplex a, TComplex b)
	 {
		 TComplex res = new TComplex();
		 res.real = a.real - b.real;
		 res.imag = a.imag - b.imag;
		 return (res);
	 }

	 public TComplex kprod(TComplex a, TComplex b)
	 {
		 TComplex res = new TComplex();
		 res.real = a.real * b.real - a.imag * b.imag;
		 res.imag = a.real * b.imag + a.imag * b.real;
		 return (res);
	 }

	 public TFftAlgorithm(int nbOfSamples)
	 {
		 int i;
		 N = nbOfSamples;
		 x = new TComplex[N + 1];
		 y = new TComplex[N + 1];
		 xw = new double[N + 1];
		 we = new TComplex[N / 2];
		 for (i = 0; i <= N; i++)
		 {
			 x[i] = new TComplex();
			 y[i] = new TComplex();
		 }
		 
		 for (i = 0; i < (N / 2); i++)  // Init look up table for sine and cosine values
		 {
			 we[i] = new TComplex();
			 we[i].real = Math.cos(2* Math.PI * (double)(i) / (double)(N));
			 we[i].imag = Math.sin(2* Math.PI * (double)(i) / (double)(N));
		 }
	 }
	
	 public void BitInvert(TComplex[] a, int n)
	 {  // invert bits for each index. n is number of samples and a the array of the samples
		 int i, mv = n/2;
		 int k, rev = 0;
		 TComplex b;
		 for (i = 1; i < n; i++) // run tru all the indexes from 1 to n
		 {
			 k = i;
			 mv = n / 2;
			 rev = 0;
			 while (k > 0) // invert the actual index
			 {
				 if ((k % 2) > 0)
					 rev = rev + mv;
				 k = k / 2;
				 mv = mv / 2; 
			 }
			 
			 // switch the actual sample and the bitinverted one
			 if (i < rev)
			 {
				 b = a[rev];
				 a[rev] = a[i];
				 a[i] = b;
			 }	
		 }
	 }


	 public void CalcSubFFT(TComplex[] a, int n)
	 {
		 int i, k, m;
		 TComplex w = new TComplex();
		 TComplex v= new TComplex();
		 TComplex h= new TComplex();
		 k = 1;
		 while (k <= n/2)
		 {
			 m = 0;
			 while (m <= (n-2*k))
			 {
				 for (i = m; i < m + k; i++)
				 {
					 // sine and cosine values from look up table
					 w.real = we[((i-m)*N / k/ 2)].real;
					 w.imag = we[((i-m)*N / k / 2)].imag;
					 // classic calculation of sine and cosine values
					 //w.real = Math.Cos( Math.PI * (double)(i-m) / (double)(k));
					 //w.imag = Math.Sin( Math.PI * (double)(i-m) / (double)(k));
					 h = kprod(a[i + k], w);
					 v = a[i];
					 a[i] = ksum(a[i], h);
					 a[i + k] = kdiff(v, h);
				 }
				 m = m + 2 * k;
			 }
			 k = k * 2;
		 }
	 }
	
	 public void CalcFFT()
	 {
		 int i;
		 BitInvert(y, N);
		 CalcSubFFT(y, N);
		 for (i = 0; i < N; i++)
		 {
			 y[i].imag = y[i].imag / (double)N * 2.0;
			 y[i].real = y[i].real / (double)N * 2.0;
		 }
		 y[0].imag = y[0].imag / 2.0;
		 y[0].real = y[0].real / 2.0;
	 }

	 public void InvFFT()    // invers Fourier transformation
	 {                       // rebuild the signal in real numbers
		 int i, k;
		 for (k = 0; k <= N; k++)
		 {
			 xw[k] = 0;
			 for (i = 0; i < 30; i++)    // we only take the first 30 fourier components
			 {
				 xw[k] = xw[k] + (y[i].real * Math.cos(2.0 * Math.PI * (double)(i * k) / (double)(N)) +
						 y[i].imag * Math.sin(2.0 * Math.PI * (double)(i * k) / (double)(N)));
			 }
		 }
	 }
 }
