public class TFftAlgorithm
{
	public int N;
	public double[] xw;
	public TComplex[] y, x;
	public TComplex[] we;

	public TComplex ksum(TComplex a, TComplex b)
	{
		TComplex res= new TComplex();
		res.real = a.real + b.real;
		res.imag = a.imag + b.imag;
		return (res);
	}

	public TComplex kdiff(TComplex a, TComplex b)
	{
		TComplex res= new TComplex();
		res.real = a.real - b.real;
		res.imag = a.imag - b.imag;
		return (res);
	}

	public TComplex kprod(TComplex a, TComplex b)
	{
		TComplex res= new TComplex();
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
		for (i = 0; i < (N + 1); i++)
		{      
			x[i] = new TComplex();
			y[i] = new TComplex();
		}
		for (i = 0; i < (N / 2); i++)
		{                           // Init look up table for sine and cosine values
			we[i] = new TComplex();
			we[i].real = Math.cos(2.0 * Math.PI * (double)(i) / (double)(N));
			we[i].imag = Math.sin(2.0 * Math.PI * (double)(i) / (double)(N));
		}
	}

	public void Shuffle(TComplex[] a, int n, int lo)
	{
		if (n > 2)
		{
			int i, m = n / 2;
			TComplex[] b = new TComplex[m];
			for (i = 0; i < m; i++)
				b[i] = a[i * 2 + lo + 1];
			for (i = 0; i < m; i++)
				a[i + lo] = a[i * 2 + lo];
			for (i = 0; i < m; i++)
				a[i + lo + m] = b[i];
		}
	}


	public void CalcSubFFT(TComplex[] a, int n, int lo)
	{
		int i, m;
		TComplex w = new TComplex();
		TComplex v= new TComplex();
		TComplex h= new TComplex();
		if (n > 1)
		{
			Shuffle(a, n, lo);
			m = n / 2;
			CalcSubFFT(a, m, lo);
			CalcSubFFT(a, m, lo + m);
			for (i = lo; i < lo + m; i++)
			{
				// sine and cosine values from look up table
				w.real = we[(i - lo) * N / n].real;
				w.imag = we[(i - lo) * N / n].imag;
				// classic calculation of sine and cosine values
				//w.real = Math.Cos(2.0 * Math.PI * (double)(i - lo) / (double)(n));
				//w.imag = Math.Sin(2.0 * Math.PI * (double)(i - lo) / (double)(n));
				h = kprod(a[i + m], w);
				v = a[i];
				a[i] = ksum(a[i], h);
				a[i + m] = kdiff(v, h);
			}
		}
	}

	public void CalcFFT()
	{
		int i;
		CalcSubFFT(y, N, 0);
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