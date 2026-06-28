
public class TDftAlgorithm
{
	int N;
	public TComplex[] we;
	public TComplex[] w;
	public TComplex[] y;
	public TComplex[] c;
	public double[] xw;

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

            public TDftAlgorithm(int order)
            {
            	int i;
                N = order;
                w = new TComplex[N + 1];
                y = new TComplex[N + 1];
                c = new TComplex[N + 1];
                xw = new double[N + 1];
                for(i = 0; i < N+1; i++)
                {
                	  w[i] = new TComplex();
                      y[i] = new TComplex();
                      c[i] = new TComplex();
                }
                
            }

        
          public void CalcGoerzel() /* First order Goerzel algorithm */
          {
              int k, n;
              TComplex w = new TComplex();
              if (N > 0)
              {
                  for (k = 0; k < N; k++)
                  {
                      c[k].real = y[0].real;
                      c[k].imag = y[0].imag;
                      w.real = -Math.cos((double)(2.0 * Math.PI * (double)(k) / (double)(N)));
                      w.imag = Math.sin((double)(2.0 * Math.PI * (double)(k) / (double)(N)));
                      for (n = 1; n <= N; n++)
                          c[k] = kdiff(y[n], kprod(c[k], w));
                      c[k] = kprod(c[k], w);
                      c[k].real = -c[k].real / (double)(N) * 2.0;
                      c[k].imag = -c[k].imag / (double)(N) * 2.0;
                  }
              }
              c[0].real = c[0].real / 2;
              c[0].imag = c[0].imag / 2;
            }

            public void InvDFT()    // invers Fourier transformation
            {                       // rebuild the signal in real numbers
                int i, k;
                
                for (k = 0; k <= N; k++)
                {
                    xw[k] = 0;
                    for (i = 0; i < 30; i++)    // we only take the first 30 fourier components
                    {
                        xw[k] = xw[k] + (c[i].real * Math.cos(2.0 * Math.PI * (double)(i * k) / (double)(N)) +
                                         c[i].imag * Math.sin(2.0 * Math.PI * (double)(i * k) / (double)(N)));
                    }
                }
            }
        }
