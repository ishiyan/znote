
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
            public double[] y;
            public double[] xw;
            public double[] a;
            public double[] b;
            public double[] sine;
            public double[] cosine;


            public TFftAlgorithm(int order)
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
                sine[0]   = 0;      //                        and sin(0) = 0
                for (k = 1; k < N; k++) //  init vectors of unit circle
                {
                    cosine[k] = Math.Cos((2.0 * Math.PI * (double)(k) / (double)(N)));
                    sine[k] = Math.Sin((2.0 * Math.PI * (double)(k) / (double)(N)));
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
                for (k = 0; k < N; k++)
                {
                    xw[k] = 0;
                    for (i = 0; i < 30; i++)    // we only take the first 30 fourier components
                    {
                        xw[k] = xw[k] + (a[i] * Math.Cos(2.0 * Math.PI * (double)(i * k) / (double)(N)) +
                                         b[i] * Math.Sin(2.0 * Math.PI * (double)(i * k) / (double)(N)));
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
                fft.y[j] = 20.0;
                fft.y[j + 501] = -20.0;
            }
            fft.y[0] = 0.0;
            fft.y[500] = 0.0;
            fft.y[1000] = 0.0;
        }

        private void InitTrytangle(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
              fft.y[j] = (double)(j) * 20.0 / 500.0;
              fft.y[j + 501] = 20.0 - ((double)(j) * 20.0 / 500.0);
            }
           fft.y[0] = 0.0;
           fft.y[500] = 20.0;
           fft.y[1000] = 0.0;
        }

        private void InitSaw(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                fft.y[j] = (double)(j) * 20.0 / 500.0;
                fft.y[j + 501] = -(double)(500-j) * 20.0 / 500.0;
            }
            fft.y[0] = 0.0;
            fft.y[500] = 20.0;
            fft.y[1000] = 0.0;
        }

        private void InitRSine(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                fft.y[j] = Math.Sin((double)(j)*Math.PI / 500.0) * 20.0;
                fft.y[j + 501] = 0.0;
            }
            fft.y[0] = 0.0;
            fft.y[1000] = 0.0;
        }


        private void MainWin_Load(object sender, EventArgs e)
        {
           int j;
           fft = new TFftAlgorithm(order);       // initialise fft class for 1000 samples
           Stopwatch timer = new Stopwatch();
           DataGridViewCell cell;
           //InitRectangle(fft);
           //InitTrytangle(fft);
           //InitSaw(fft);
           InitRSine(fft);
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
               cell.Value = fft.a[j]; // the real value is the cosinus part
               cell = GResult[2, j + 1];
               cell.Value = fft.b[j]; // the imag value is the sinus part
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
                    p1.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(fft.y[j] * 5.0));
                    p2.X = Convert.ToInt32(j / 2 + 1);
                    p2.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(fft.y[j + 1] * 5.0));
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
