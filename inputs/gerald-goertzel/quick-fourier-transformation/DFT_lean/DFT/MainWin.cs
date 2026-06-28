
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Diagnostics;


namespace WindowsFormsApplication1
{

    public struct TKomplex
    {
        public double real;
        public double imag;
    }

    public partial class MainWin : Form
    {
        int order = 1000;

        public class TFftAlgorithm
        {
            int N;
            public TKomplex[] we;
            public TKomplex[] y;
            public double[] xw;
            public TKomplex[] c;

            public TKomplex ksum(TKomplex a, TKomplex b)
            {
                TKomplex res;
                res.real = a.real + b.real;
                res.imag = a.imag + b.imag;
                return (res);
            }


            public TKomplex kprod(TKomplex a, TKomplex b)
            {
                TKomplex res;
                res.real = a.real * b.real - a.imag * b.imag;
                res.imag = a.real * b.imag + a.imag * b.real;
                return (res);
            }

            public TFftAlgorithm(int order)
            {
                int k;
                N = order;
                y = new TKomplex[N + 1];
                xw = new double[N + 1];
                c = new TKomplex[N + 1];
                we = new TKomplex[N + 1];
                we[0].real = 1.0;    // we don't have to calculate cos(0) = 1
                we[0].imag = 0;      //                        and sin(0) = 0
                for (k = 1; k < N; k++) //  init vectors of unit circle
                {
                    we[k].real = Math.Cos((2.0 * Math.PI * (double)(k) / (double)(N)));
                    we[k].imag = -Math.Sin((2.0 * Math.PI * (double)(k) / (double)(N)));
                }
            }


            public void CalcDFT()   // Fourier transformation
            {                       // calculation of the Fourier components
                int k, n;
                if (N > 0)
                {
                    for (k = 0; k < N; k++)
                    {
                        c[k].real = 0;
                        c[k].imag = 0;
                        for (n = 0; n < (N - 1); n++)
                        {
                            c[k] = ksum(c[k], kprod(we[(k * n) % N], y[n]));
                        }
                        c[k].real = c[k].real / N * 2;
                        c[k].imag = -c[k].imag / N * 2;
                    }
                    c[0].real = c[0].real / 2;
                    c[0].imag = c[0].imag / 2;
                }
            }


            public void InvDFT()    // invers Fourier transformation
            {                       // rebuild the signal in real numbers
                int i, k;
                for (k = 0; k < N; k++)
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

        TFftAlgorithm fft;

        public MainWin()
        {
            InitializeComponent();
        }

        private void InitRectangle(TFftAlgorithm fft) // init  rectangle signal
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                fft.y[j].real = 20.0;
                fft.y[j].imag = 0.0;
                fft.y[j + 501].real = -20.0;
                fft.y[j + 501].imag = 0.0;
            }
            fft.y[0].real = 0.0;
            fft.y[0].imag = 0.0;
            fft.y[500].real = 0.0;
            fft.y[500].imag = 0.0;
            fft.y[1000].real = 0.0;
            fft.y[1000].imag = 0.0;
        }

        private void InitTrytangle(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
              fft.y[j].real = (double)(j) * 20.0 / 500.0;
              fft.y[j].imag =  0.0;
              fft.y[j + 501].real = 20.0 - ((double)(j) * 20.0 / 500.0);
              fft.y[j+501].imag = 0.0;
            }
           fft.y[0].real = 0.0;
           fft.y[0].imag = 0.0;
           fft.y[500].real = 20.0;
           fft.y[500].imag = 0.0;
           fft.y[1000].real = 0.0;
           fft.y[1000].imag = 0.0;
        }

        private void InitSaw(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                fft.y[j].real = (double)(j) * 20.0 / 500.0;
                fft.y[j].imag = 0.0;
                fft.y[j + 501].real = -(double)(500-j) * 20.0 / 500.0;
                fft.y[j + 501].imag = 0.0;
            }
            fft.y[0].real = 0.0;
            fft.y[0].imag = 0.0;
            fft.y[500].real = 20.0;
            fft.y[500].imag = 0.0;
            fft.y[1000].real = 0.0;
            fft.y[1000].imag = 0.0;
        }


        private void MainWin_Load(object sender, EventArgs e)
        {
           int j;
           fft = new TFftAlgorithm(order);       // initialise fft class for 1000 samples
           Stopwatch timer = new Stopwatch();
           DataGridViewCell cell;
           InitRectangle(fft);
           //InitTrytangle(fft);
           //InitSaw(fft);
           timer.Start();
           fft.CalcDFT();
           timer.Stop();
           tbTime.Text = timer.ElapsedMilliseconds.ToString();
           fft.InvDFT();
           GResult.RowCount = 30;            // DataGridView for data display 30 Fourier components
           for (j = 0; j < GResult.RowCount; j++)        // put values into the DataGrid
            {
               cell = GResult[0, j + 1];  // get cell to access
               cell.Value = j;
               cell = GResult[1, j + 1];
               cell.Value = fft.c[j].real; // the real value is the cosinus part
               cell = GResult[2, j + 1];
               cell.Value = fft.c[j].imag; // the imag value is the sinus part
            }
        }

       private void pBild_Paint(object sender, PaintEventArgs e)  // draw the shapes
        {                                                         // blue for initial signal  
            Point p1, p2;                                         // red for rebuild shape  
            int j;
            p1 = new Point();
            p2 = new Point();
            Graphics g = pBild.CreateGraphics();
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
                    p1.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(fft.y[j].real * 5.0));
                    p2.X = Convert.ToInt32(j / 2 + 1);
                    p2.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(fft.y[j + 1].real * 5.0));
                    g.DrawLine(bluePen, p1, p2);
                    p1.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(fft.xw[j] * 5.0));
                    p2.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(fft.xw[j+1] * 5.0));
                    g.DrawLine(redPen, p1, p2);
                }
            }
            g.Dispose();
        }

    }
}
