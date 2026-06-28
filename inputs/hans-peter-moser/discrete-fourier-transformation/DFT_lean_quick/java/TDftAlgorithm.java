
public class TDftAlgorithm
{
	int N;
	public double[] y;
	public double[] xw;
	public double[] a;
	public double[] b;
	public double[] sine;
	public double[] cosine;


	public TDftAlgorithm(int order)
	{
		int k;
		N = order;
		y = new double[N + 1];
		a = new double[N + 1];
		b = new double[N + 1];
		xw = new double[N + 1];
		sine = new double[N + 1];
		cosine = new double[N + 1];

		cosine[0] = 1.0;    // we don't have to calculate cos(0) = 1
		sine[0] = 0;      //                        and sin(0) = 0
		for (k = 1; k < N; k++) //  init vectors of unit circle
		{
			cosine[k] = Math.cos((2.0 * Math.PI * (double)(k) / (double)(N)));
			sine[k] = Math.sin((2.0 * Math.PI * (double)(k) / (double)(N)));
		}
	}


	public void CalcDFT()   // Fourier transformation
	{                       // calculation of the Fourier components
		int k, n;
		if (N > 0)
		{
			for (k = 0; k < N; k++)
			{
				a[k] = 0;
				b[k] = 0;
				for (n = 0; n < (N - 1); n++)
				{
					a[k] = a[k] + ((cosine[(k * n) % N] * y[n]));
					b[k] = b[k] + ((sine[(k * n) % N] * y[n]));
				}
				a[k] = a[k] / N * 2;
				b[k] = b[k] / N * 2;
			}
			a[0] = a[0] / 2;
			b[0] = b[0] / 2;
		}
	}


	public void InvDFT()    // invers Fourier transformation
	{                       // rebuild the signal in real numbers
		int i, k;
		for (k = 0; k <= N; k++)
		{
			xw[k] = 0;
			for (i = 0; i < 30; i++)    // we only take the first 30 fourier components
			{
				xw[k] = xw[k] + (a[i] * Math.cos(2.0 * Math.PI * (double)(i * k) / (double)(N)) +
						b[i] * Math.sin(2.0 * Math.PI * (double)(i * k) / (double)(N)));
			}
		}
	}
}
