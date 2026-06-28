using System;
using System.Drawing;
using System.Windows.Forms;

/*  Fast Fourier transformation   */
/*       www.mosismath.com        */

namespace WindowsFormsApplication1
{    
    
    public partial class MainWin : Form
    {
     
        public class TFftAlgorithm
        {
            public int N;
            public double[] xw;
            public TComplex[] y, x;
            public TComplex[] we;

            public TComplex ksum(TComplex a, TComplex b)
            {
                TComplex res;
                res.real = a.real + b.real;
                res.imag = a.imag + b.imag;
                return (res);
            }

            public TComplex kdiff(TComplex a, TComplex b)
            {
                TComplex res;
                res.real = a.real - b.real;
                res.imag = a.imag - b.imag;
                return (res);
            }

            public TComplex kprod(TComplex a, TComplex b)
            {
                TComplex res;
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
                for (i = 0; i < (N / 2); i++)  // Init look up table for sine and cosine values
                {
                    we[i].real = Math.Cos(2* Math.PI * (double)(i) / (double)(N));
                    we[i].imag = Math.Sin(2* Math.PI * (double)(i) / (double)(N));
                }
            }

            public void BitInvert(TComplex[] a, int n)
            {  // invert bits for each index. n is number of samples and a the array of the samples
                int i, mv = n / 2;
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
                TComplex w;
                TComplex v;
                TComplex h;
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
                        xw[k] = xw[k] + (y[i].real * Math.Cos(2.0 * Math.PI * (double)(i * k) / (double)(N)) +
                                         y[i].imag * Math.Sin(2.0 * Math.PI * (double)(i * k) / (double)(N)));
                    }
                }
            }
        }

        private void InitRectangle(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < 2048; j++)
            {
                fft.y[j].real = 20.0;
                fft.y[j].imag = 0.0;
                fft.y[j + 2048].real = -20.0;
                fft.y[j + 2048].imag = 0.0;
            }
            fft.y[0].real = 0.0;
            fft.y[0].imag = 0.0;
            fft.y[4096].real = 0.0;
            fft.y[4096].imag = 0.0;
            fft.y[4096].real = 0.0;
            fft.y[4096].imag = 0.0;
            for (j = 0; j <= 4096; j++)
                fft.x[j] = fft.y[j];
        }

        private void InitTryangle(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < 2048; j++)
            {
                fft.y[j].real = 20 - (double)(j) * 40.0 / 2048;
                fft.y[j].imag = 0.0;
                fft.y[j + 2049].real = -20.0 + ((double)(j) * 40.0 / 2048);
                fft.y[j + 2049].imag = 0.0;
            }
            fft.y[0].real = 20.0;
            fft.y[0].imag = 0.0;
            fft.y[2048].real = -20.0;
            fft.y[2048].imag = 0.0;
            fft.y[4096].real = 20.0;
            fft.y[4096].imag = 0.0;
            for (j = 0; j <= 4096; j++)
                fft.x[j] = fft.y[j];
        }

        private void InitSaw(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < 2048; j++)
            {
                fft.y[j].real = (double)(j) * 20.0 / 2048.0;
                fft.y[j].imag = 0.0;
                fft.y[j + 2049].real = -(double)(2048 - j) * 20.0 / 2048.0;
                fft.y[j + 2049].imag = 0.0;
            }
            fft.y[0].real = 0.0;
            fft.y[0].imag = 0.0;
            fft.y[2048].real = 20.0;
            fft.y[2048].imag = 0.0;
            fft.y[4096].real = 0.0;
            fft.y[4096].imag = 0.0;
            for (j = 0; j <= 4096; j++)
                fft.x[j] = fft.y[j];
        }

        TFftAlgorithm fft;

        public MainWin()
        {
            InitializeComponent();        
        }

       

        private void Form1_Load(object sender, EventArgs e)
        {
           int j;
           fft = new TFftAlgorithm(4096);       // initialize fft class for 4096 samples
           DataGridViewCell cell;
           InitRectangle(fft);
           fft.CalcFFT();
           fft.InvFFT();
           GResult.RowCount = 30;            // DataGridView for data display 30 Fourier components
           for (j = 0; j < GResult.RowCount; j++)        // put values into the DataGrid
           {
               cell = GResult[0, j + 1];  // get cell to access
               cell.Value = j;
               cell = GResult[1, j + 1];
               cell.Value = fft.y[j].real; // the real value is the cosinus part
               cell = GResult[2, j + 1];
               cell.Value = fft.y[j].imag; // the imag value is the sinus part
           }
        }
       

        private void cBWaveshape_SelectedIndexChanged(object sender, EventArgs e)
        {
            int j;
            DataGridViewCell cell;
            switch (cBWaveshape.SelectedIndex)
            {
                case 0:
                    InitRectangle(fft);
                    break;
                case 1:
                    InitTryangle(fft);
                    break;
                case 2:
                    InitSaw(fft);
                    break;
            }
            fft.CalcFFT();
            fft.InvFFT();
            GResult.RowCount = 30;            // DataGridView for data display 30 Fourier components
            for (j = 0; j < GResult.RowCount; j++)        // put values into the DataGrid
            {
                cell = GResult[0, j];  // get cell to access
                cell.Value = j;
                cell = GResult[1, j];
                cell.Value = fft.y[j].real; // the real value is the cosinus part
                cell = GResult[2, j];
                cell.Value = fft.y[j].imag; // the imag value is the sinus part
            }
            pGraph_Paint(this, null);
        }

        private void pGraph_Paint(object sender, PaintEventArgs e)
        {
            Point p1, p2;                                         
            int j;
            p1 = new Point();
            p2 = new Point();
            Graphics g = pGraph.CreateGraphics();
            g.Clear(Color.White);
            Pen bluePen = new Pen(Color.Blue, 2);
            Pen redPen = new Pen(Color.Red, 2);
            Pen blackPen = new Pen(Color.Black, 2);
            bluePen.Width = 1;
            redPen.Width = 1;
            blackPen.Width = 1;
            p1.X = 0;
            p1.Y = (pGraph.Height / 2);
            p2.X = pGraph.Width;
            p2.Y = (pGraph.Height / 2);
            g.DrawLine(blackPen, p1, p2);
            if (fft.N > 0)
            {
                for (j = 0; j < fft.N; j++)
                {
                    p1.X = Convert.ToInt32(j / 8);
                    p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(fft.x[j].real * 5.0));
                    p2.X = Convert.ToInt32((j / 8) + 1);
                    p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(fft.x[j + 1].real * 5.0));
                    g.DrawLine(bluePen, p1, p2);
                    p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(fft.xw[j] * 5.0));
                    p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(fft.xw[j + 1] * 5.0));
                    g.DrawLine(redPen, p1, p2);
                }
            }
            g.Dispose();
        }
    }
}
