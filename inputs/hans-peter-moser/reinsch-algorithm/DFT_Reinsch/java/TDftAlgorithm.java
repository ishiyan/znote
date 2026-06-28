    public class TDftAlgorithm
        {
            int N;
            public TComplex[] w;
            public TComplex[] y;
            public TComplex[] c;
            public double[] xw;


            public TDftAlgorithm(int order)
            {
            	int i;
                N = order;
                w = new TComplex[N + 1];
                y = new TComplex[N + 1];
                c = new TComplex[N + 1];
                xw = new double[N + 1];
                for (i = 0; i < N + 1; i++)
                {
                	 w[i] = new TComplex();
                     y[i] = new TComplex();
                     c[i] = new TComplex();
                }
            }

            public void CalcReinsch() // Reinsch algorithm for DFT
            {
                int k, n;
                TComplex b1 = new TComplex();
                TComplex a1 = new TComplex();
                TComplex v0 = new TComplex();
                TComplex v1 = new TComplex();
                TComplex v2 = new TComplex();
                double dW;
                if (N > 0)
                {
                    for (k = 0; k < N; k++)
                    {
                        v0.real = 0;
                        v0.imag = 0;
                        v1.real = y[1].real;
                        v1.imag = y[1].imag;
                        v2.real = y[0].real;
                        v2.imag = y[0].imag;
                        dW = 0;
                        b1.real = Math.cos((double)(2.0 * Math.PI * (double)(k) / (double)(N)));
                        b1.imag = -Math.sin((double)(2.0 * Math.PI * (double)(k) / (double)(N)));
                        if (b1.real > 0)
                        {
                            a1.real = -4 * Math.pow(Math.sin((double)(Math.PI * (double)(k) / (double)(N))), 2.0);
                            a1.imag = 0;
                            for (n = 0; n < N; n++)
                            {
                                dW = y[n].real + a1.real * v1.real + dW;
                                v0.real = dW + v1.real;
                                v1 = v0;
                            }
                            c[k].real = (dW - a1.real / 2.0 * v0.real) / (double)(N) * 2.0;
                            c[k].imag = (b1.imag * v1.real) / (double)(N) * 2.0;
                        }
                        else
                        {
                            a1.real = 4 * Math.pow(Math.cos((double)(Math.PI * (double)(k) / (double)(N))), 2.0);
                            a1.imag = 0;
                            for (n = 0; n < N; n++)
                            {
                                dW = y[n].real + a1.real * v1.real - dW;
                                v0.real = dW - v1.real;
                                v1 = v0;
                            }
                            c[k].real = (dW - a1.real / 2.0 * v0.real) / (double)(N) * 2.0;
                            c[k].imag = (b1.imag * v1.real) / (double)(N) * 2.0;
                        }
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