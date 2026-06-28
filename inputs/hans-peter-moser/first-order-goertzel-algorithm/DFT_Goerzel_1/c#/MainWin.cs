
using System;
using System.Drawing;
using System.Windows.Forms;
using System.Diagnostics;

/*       First order Goertzel DFT           */
/*         www.mosismath.com                */

namespace WindowsFormsApplication1
{
   
    public struct TComplex
    {
        public double real;
        public double imag;
    }

    public partial class MainWin : Form
    {
        int order = 1000;

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

            public TDftAlgorithm(int order)
            {
                N = order;
                w = new TComplex[N+1];
                y = new TComplex[N + 1];
                c = new TComplex[N + 1];
                xw = new double[N + 1];
            }

        
          public void CalcGoerzel() /* First order Goerzel algorithm */
          {
              int k, n;
              TComplex w;
              if (N > 0)
              {
                  for (k = 0; k < N; k++)
                  {
                      c[k].real = y[0].real;
                      c[k].imag = y[0].imag;
                      w.real = -Math.Cos((double)(2.0 * Math.PI * (double)(k) / (double)(N)));
                      w.imag = Math.Sin((double)(2.0 * Math.PI * (double)(k) / (double)(N)));
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
                        xw[k] = xw[k] + (c[i].real * Math.Cos(2.0 * Math.PI * (double)(i * k) / (double)(N)) +
                                         c[i].imag * Math.Sin(2.0 * Math.PI * (double)(i * k) / (double)(N)));
                    }
                }
            }
        }

        TDftAlgorithm dft;

        public MainWin()
        {
            InitializeComponent();
        }

        //  Create some signals for testing
 
        private void InitRectangle(TDftAlgorithm dft)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                dft.y[j].real = 20.0;
                dft.y[j].imag = 0.0;
                dft.y[j + 501].real = -20.0;
                dft.y[j + 501].imag = 0.0;
            }
            dft.y[0].real = 0.0;
            dft.y[0].imag = 0.0;
            dft.y[500].real = 0.0;
            dft.y[500].imag = 0.0;
            dft.y[1000].real = 0.0;
            dft.y[1000].imag = 0.0;
        }

        private void InitTryangle(TDftAlgorithm dft)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                dft.y[j].real = 20 - (double)(j) * 40.0 / 500.0;
                dft.y[j].imag = 0.0;
                dft.y[j + 501].real = -20.0 + ((double)(j) * 40.0 / 500.0);
                dft.y[j + 501].imag = 0.0;
            }
            dft.y[0].real = 20.0;
            dft.y[0].imag = 0.0;
            dft.y[500].real = -20.0;
            dft.y[500].imag = 0.0;
            dft.y[1000].real = 20.0;
            dft.y[1000].imag = 0.0;
        }

        private void InitSaw(TDftAlgorithm dft)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                dft.y[j].real = (double)(j) * 20.0 / 500.0;
                dft.y[j].imag = 0.0;
                dft.y[j + 501].real = -(double)(500 - j) * 20.0 / 500.0;
                dft.y[j + 501].imag = 0.0;
            }
            dft.y[0].real = 0.0;
            dft.y[0].imag = 0.0;
            dft.y[500].real = 20.0;
            dft.y[500].imag = 0.0;
            dft.y[1000].real = 0.0;
            dft.y[1000].imag = 0.0;
        }

        private void MainWin_Load(object sender, EventArgs e)
        {
           int j;
           dft = new TDftAlgorithm(order);
           Stopwatch timer = new Stopwatch();
           DataGridViewCell cell;
           InitRectangle(dft);
           dft.CalcGoerzel();
           dft.InvDFT();
           GResult.RowCount = 30;  // DataGridView
           for (j = 0; j < GResult.RowCount; j++)
            {
              cell = GResult[0, j];  // get cell to access
              cell.Value = j;
              cell = GResult[1, j];
              cell.Value = dft.c[j].real;
              cell = GResult[2, j];
              cell.Value = dft.c[j].imag;
            }
        }

        
        private void cBWaveshape_SelectedIndexChanged(object sender, EventArgs e)
        {
            int j;
            DataGridViewCell cell;
            switch (cBWaveshape.SelectedIndex)
            {
                case 0:
                    InitRectangle(dft);
                    break;
                case 1:
                    InitTryangle(dft);
                    break;
                case 2:
                    InitSaw(dft);
                    break;
            }
            dft.CalcGoerzel();
            dft.InvDFT();
            GResult.RowCount = 30;            // DataGridView for data display 30 Fourier components
            for (j = 0; j < GResult.RowCount; j++)        // put values into the DataGrid
            {
                cell = GResult[0, j];  // get cell to access
                cell.Value = j;
                cell = GResult[1, j];
                cell.Value = dft.c[j].real; // the real value is the cosinus part
                cell = GResult[2, j];
                cell.Value = dft.c[j].imag; // the imag value is the sinus part
            }
            pGraph_Paint(this, null);
        }

        private void pGraph_Paint(object sender, PaintEventArgs e)
        {
            Point p1, p2;                                         // red for rebuild shape  
            int j;
            p1 = new Point();
            p2 = new Point();
            Graphics g = pBild.CreateGraphics();
            g.Clear(Color.White);
            Pen bluePen = new Pen(Color.Blue, 2);
            Pen redPen = new Pen(Color.Red, 2);
            Pen blackPen = new Pen(Color.Black, 2);
            bluePen.Width = 1;
            redPen.Width = 1;
            blackPen.Width = 1;
            p1.X = 0;
            p1.Y = (pBild.Height / 2);
            p2.X = pBild.Width;
            p2.Y = (pBild.Height / 2);
            g.DrawLine(blackPen, p1, p2);
            if (order > 0)
            {
                for (j = 0; j < order; j++)
                {
                    p1.X = Convert.ToInt32(j / 2);
                    p1.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(dft.y[j].real * 5.0));
                    p2.X = Convert.ToInt32(j / 2 + 1);
                    p2.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(dft.y[j + 1].real * 5.0));
                    g.DrawLine(bluePen, p1, p2);
                    p1.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(dft.xw[j] * 5.0));
                    p2.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(dft.xw[j + 1] * 5.0));
                    g.DrawLine(redPen, p1, p2);
                }
            }
            g.Dispose();
        }
    }
}
