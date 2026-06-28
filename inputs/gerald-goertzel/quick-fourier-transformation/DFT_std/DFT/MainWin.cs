
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
       
        public class TFftAlgorithm
        {
            int N; 
            public TKomplex[] we;
            public TKomplex[] w;
            public TKomplex[] y;
            public TKomplex[] c;

            public TKomplex ksum(TKomplex a, TKomplex b)
            {
                TKomplex res;
                res.real = a.real + b.real;
                res.imag = a.imag + b.imag;
                return (res);
            }

            public TKomplex kdiff(TKomplex a, TKomplex b)
            {
                TKomplex res;
                res.real = a.real - b.real;
                res.imag = a.imag - b.imag;
                return (res);
            }

            public TKomplex kprod(TKomplex a, TKomplex b)
            {
                TKomplex res;
                res.real = a.real * b.real - a.imag * b.imag;
                res.imag = a.real * b.imag + a.imag * b.real;
                return (res);
            }

             public TFftAlgorithm()
            {
                w = new TKomplex[1001];
                y = new TKomplex[1001];
                c = new TKomplex[1001];
            }

            public void CalcW(int index, int order)   // Komplexe Richtungsvektoren w zum Index
            {
                int i;
                for (i = 0; i < order; i++)
                {
                    w[i].real = Math.Cos((double)(2.0 * Math.PI * (double)(i * index) / (double)(order)));
                    w[i].imag = Math.Sin((double)(2.0 * Math.PI * (double)(i * index) / (double)(order)));
                }
            }

            public void CalcDFT(int N)
            {
                int k, n;
                TKomplex w;
                if (N > 0)
                {
                    for (k = 0; k < N; k++)
                    {
                       // CalcW(k, order);
                        c[k].real = 0;
                        c[k].imag = 0;
                        for (n = 0; n < N; n++)
                        {
                            w.real = Math.Cos((double)(2.0 * Math.PI * (double)(k * n) / (double)(N)));
                            w.imag = -Math.Sin((double)(2.0 * Math.PI * (double)(k * n) / (double)(N)));
                            c[k] = ksum(c[k], kprod(w, y[n]));
                        }
                        c[k].real = c[k].real / (double)(N) * 2.0;
                        c[k].imag = -c[k].imag / (double)(N) * 2.0;
                    }
                }
                c[0].real = c[0].real / 2;
                c[0].imag = c[0].imag / 2;
            }
        }

        TFftAlgorithm fft;

        public MainWin()
        {
            InitializeComponent();
        }

        private void InitRectangle(TFftAlgorithm fft)
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
                fft.y[j + 501].real = 0.0; // -(double)(500 - j) * 20.0 / 500.0;
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
           fft = new TFftAlgorithm();
           Stopwatch timer = new Stopwatch();
           DataGridViewCell cell;
           InitRectangle(fft);
          // InitSaw(fft);
          // InitTrytangle(fft);
           timer.Start();
           fft.CalcDFT(1001);
           timer.Stop();
           tbTime.Text = timer.ElapsedMilliseconds.ToString();
           GResult.RowCount = 30;  // DataGridView
           for (j = 0; j < GResult.RowCount; j++)
            {
              cell = GResult[0, j + 1];  // get cell to access
              cell.Value = j;
              cell = GResult[1, j + 1];
              cell.Value = fft.c[j].real;
              cell = GResult[2, j + 1];
              cell.Value = fft.c[j].imag;
            }
        }

        private void pBild_Paint(object sender, PaintEventArgs e)
        {
            Point p1, p2;
            int order = 1001;
            int i, j;
            p1 = new Point();
            p2 = new Point();
            double y1, y2;
            Graphics g = pBild.CreateGraphics();
            Pen bluePen = new Pen(Color.Blue, 2);
            Pen redPen = new Pen(Color.Red, 2);
            bluePen.Width = 1;
            if (order > 0)
            {
                for (j = 0; j < order - 1; j++)
                {
                    p1.X = Convert.ToInt32(j / 2);
                    p1.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(fft.y[j].real * 5.0));
                    p2.X = Convert.ToInt32(j / 2 + 1);
                    p2.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(fft.y[j + 1].real * 5.0));
                    g.DrawLine(bluePen, p1, p2);
                    y1 = 0;
                    y2 = 0;
                    for (i = 0; i < 50; i++)
                    {
                        y1 = y1 + (fft.c[i].real * Math.Cos(2.0 * 3.141592654 * (double)(i * j)  / (double)(order)) +
                                   fft.c[i].imag * Math.Sin(2.0 * 3.141592654 * (double)(i * j) / (double)(order)));
                        y2 = y2 + (fft.c[i].real * Math.Cos(2.0 * 3.141592654 * (double)(i * (j + 1)) / (double)(order)) +
                                   fft.c[i].imag * Math.Sin(2.0 * 3.141592654 * (double)(i * (j + 1)) / (double)(order)));
                    }
                    p1.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(y1 * 5.0));
                    p2.Y = (pBild.Height / 2) - Convert.ToInt32(Math.Round(y2 * 5.0));
                    g.DrawLine(redPen, p1, p2);
                }
            }
            g.Dispose();
        }

    }
}
