
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
        public const int order = 2000;

        public class TFftAlgorithm
        {
            int N;
            public TKomplex[] w;
            public TKomplex[] y;
            public TKomplex[] c;


            public TFftAlgorithm()
            {
                w = new TKomplex[order];
                y = new TKomplex[order];
                c = new TKomplex[order];
            }
            

        
        public void CalcReinsch(int N) // Reinsch algorithm for DFT
          {
              int k, n;
              TKomplex b1, a1, v0, v1, v2;
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
                      b1.real = Math.Cos((double)(2.0 * Math.PI * (double)(k) / (double)(N)));
                      b1.imag = -Math.Sin((double)(2.0 * Math.PI * (double)(k) / (double)(N)));
                      if (b1.real > 0) 
                      {
                          a1.real = -4 * Math.Pow(Math.Sin((double)(Math.PI * (double)(k) / (double)(N))), 2.0);
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
                          a1.real = 4 * Math.Pow(Math.Cos((double)(Math.PI * (double)(k) / (double)(N))), 2.0);
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
        } 

        TFftAlgorithm fft;

        public MainWin()
        {
            InitializeComponent();
        }

        //  Create some signals for testing

        private void InitRectangle(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < order; j++)
            {
                if (j < (order / 2))
                {
                    fft.y[j].real = 20.0;
                    fft.y[j].imag = 0.0;
                }
                else
                {
                    fft.y[j].real = -20.0;
                    fft.y[j].imag = 0.0;
                }
            }
        }

        private void InitTrytangle(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < (order / 2); j++)
            {
                fft.y[j].real = (double)(j) * 20.0 / (double)(order / 2);
                fft.y[j].imag = 0.0;
                fft.y[j + (order / 2)].real = 20.0 - ((double)(j) * 20.0 / (double)(order / 2));
                fft.y[j + (order / 2)].imag = 0.0;
            }
            fft.y[0].real = 0.0;
            fft.y[0].imag = 0.0;
            fft.y[order / 2].real = 20.0;
            fft.y[order / 2].imag = 0.0;
            fft.y[order-1].real = 0.0;
            fft.y[order-1].imag = 0.0;
        }

        private void InitSaw(TFftAlgorithm fft)
        {
            int j;
            for (j = 0; j < (order / 2); j++)
            {
                fft.y[j].real = (double)(j) * 20.0 / (double)(order / 2);
                fft.y[j].imag = 0.0;
                fft.y[j + (order / 2)].real = -(double)(500 - j) * 20.0 / (double)(order / 2);
                fft.y[j + (order / 2)].imag = 0.0;
            }
            fft.y[0].real = 0.0;
            fft.y[0].imag = 0.0;
            fft.y[(order / 2)].real = 20.0;
            fft.y[(order / 2)].imag = 0.0;
            fft.y[order - 1].real = 0.0;
            fft.y[order - 1].imag = 0.0;
        }

        private void MainWin_Load(object sender, EventArgs e)
        {
           int j;
           fft = new TFftAlgorithm();
           Stopwatch timer = new Stopwatch();
           DataGridViewCell cell;
           InitRectangle(fft);
           //InitSaw(fft);
           //InitTrytangle(fft);
           timer.Start();
           fft.CalcReinsch(order);
           timer.Stop();
           tbTime.Text = timer.ElapsedMilliseconds.ToString();
           GResult.RowCount = 30;  // DataGridView
           for (j = 0; j < GResult.RowCount; j++)
            {
              cell = GResult[0, j];  // get cell to access
              cell.Value = j;
              cell = GResult[1, j];
              cell.Value = fft.c[j].real;
              cell = GResult[2, j];
              cell.Value = fft.c[j].imag;
            }
        }

        private void pBild_Paint(object sender, PaintEventArgs e)
        {
            Point p1, p2;
            int i, j;
            p1 = new Point();
            p2 = new Point();
            double y1, y2, scaleX;
            Graphics g = pGraph.CreateGraphics();
            Pen bluePen = new Pen(Color.Blue, 1);
            Pen redPen = new Pen(Color.Red, 1);
            Pen blackPen = new Pen(Color.Black, 1);
            bluePen.Width = 1;
            scaleX = (double)(pGraph.Width - 40) / (double)(order);
            // draw zero line
            p1.X = 0;
            p1.Y = (pGraph.Height / 2);
            p2.X = pGraph.Width;
            p2.Y = (pGraph.Height / 2);
            g.DrawLine(blackPen, p1, p2);
            if (order > 0)
            {
                for (j = 0; j < order - 1; j++)
                {
                    // draw reverence signal in blue
                    p1.X = Convert.ToInt32((double)(j) * scaleX);
                    p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(fft.y[j].real * 5.0));
                    p2.X = Convert.ToInt32((double)(j + 1) * scaleX + 1);
                    p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(fft.y[j + 1].real * 5.0));
                    g.DrawLine(bluePen, p1, p2);
                    y1 = 0;
                    y2 = 0;
                    // reconstruct signal from harmonics and draw red
                    for (i = 0; i < 50; i++)
                    {
                        y1 = y1 + (fft.c[i].real * Math.Cos(2.0 * 3.141592654 * (double)(i * j) / (double)(order)) +
                                   fft.c[i].imag * Math.Sin(2.0 * 3.141592654 * (double)(i * j) / (double)(order)));
                        y2 = y2 + (fft.c[i].real * Math.Cos(2.0 * 3.141592654 * (double)(i * (j + 1)) / (double)(order)) +
                                   fft.c[i].imag * Math.Sin(2.0 * 3.141592654 * (double)(i * (j + 1)) / (double)(order)));
                    }
                    p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y1 * 5.0));
                    p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y2 * 5.0));
                    g.DrawLine(redPen, p1, p2);
                }
            }
            g.Dispose();
        }

    }
}
