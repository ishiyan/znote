
using System;
using System.Drawing;
using System.Windows.Forms;

/* Discrete Hartley Transformation for different sample shapes                    */
/*                              www.mosismath.com                                 */

namespace WindowsFormsApplication1
{

    public partial class MainWin : Form
    {

        int order = 1000;

        public class TDHTAlgorithm
        {
            public int N;
            public double[] y;
            public double[] hk;
            public double[] xw;

           
            public TDHTAlgorithm(int order)
            {
                N = order;
                y = new double[N + 1];
                hk = new double[N + 1];
                xw = new double[N + 1];
            }


            public void CalcDHT()
            {
                int k, n;
                if (N > 0)
                {
                    for (k = 0; k < N; k++)
                    {
                        hk[k] = 0;
                        for (n = 0; n < N; n++)
                        {
                            hk[k] += y[n] * Math.Cos((double)(2 * Math.PI * n * k / N - Math.PI / 4));
                        }
                        hk[k] *= 2.0 * Math.Sqrt(2.0)/N;
                    }
                }
            }


            public void InvDHT()    // invers Hartley transformation
            {                       // rebuild the signal
                int t, n;
                for (n = 0; n <= N; n++)
                {
                    xw[n] = 0;
                    for (t = 0; t < 30; t++)    // we only take the first 30 harmonics
                    {
                        xw[n] = xw[n] + (hk[t] + hk[N - t]) / 2 * Math.Cos(2.0 * Math.PI * t * n / N) +   //even part
                                        (hk[t] - hk[N - t]) / 2 * Math.Sin(2.0 * Math.PI * t * n / N);  // odd part
                    }
                }
            }
        }

        TDHTAlgorithm dht;

        public MainWin()
        {
            InitializeComponent();
        }

        private void InitRectangle(TDHTAlgorithm dht)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                dht.y[j] = 20.0;
                dht.y[j + 501] = -20.0;
            }
            dht.y[0] = 0.0;
            dht.y[500] = 0.0;
            dht.y[1000] = 0.0;
        }

        private void InitTryangle(TDHTAlgorithm dht)
        {
            int j;
            for (j = 0; j < 250; j++)
            {
                dht.y[j] = (double)(j) * 40.0 / 500.0;
                dht.y[j + 751] = -20.0 + ((double)(j) * 40.0 / 500.0);
            }
            for (j = 0; j < 500; j++)
            {
                dht.y[j+251] = 20 - (double)(j) * 40.0 / 500.0;
            }
        }


        private void InitSaw(TDHTAlgorithm dht)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                dht.y[j] = (double)(j) * 20.0 / 500.0;
                dht.y[j + 501] = 0.0 - (double)(500 - j) * 20.0 / 500.0;
            }
            dht.y[0] = 0.0;
            dht.y[500] = 20.0;
            dht.y[1000] = 0.0;
        }

        private void InitSinus(TDHTAlgorithm dht)
        {
            int j;
            for (j = 0; j < 500; j++)
            {
                if (j > 100)
                {
                    dht.y[j] = 20.0 * Math.Sin((double)(j) / 500.0 * Math.PI);
                    dht.y[j + 501] = dht.y[j];
                }
                else
                {
                    dht.y[j] = 0;
                    dht.y[j + 501] = 0;
                }
            }
            dht.y[0] = 0.0;
            dht.y[500] = 0.0;
            dht.y[1000] = 0.0;
        }

        private void MainWin_Load(object sender, EventArgs e)
        {
            int j;
            dht = new TDHTAlgorithm(order);
            DataGridViewCell cell;
            InitRectangle(dht);
            dht.CalcDHT();
            dht.InvDHT();
            GResult.RowCount = 30;  // DataGridView
            for (j = 0; j < GResult.RowCount; j++)
            {
                cell = GResult[0, j];  // get cell to access
                cell.Value = j;
                cell = GResult[1, j];
                cell.Value = dht.hk[j];
                cell = GResult[2, j];
                cell.Value = (dht.hk[j] + dht.hk[dht.N - j])/2 ;
                cell = GResult[3, j];
                cell.Value = (dht.hk[j] - dht.hk[dht.N - j])/2 ;
            }
        }


        private void cBWaveshape_SelectedIndexChanged(object sender, EventArgs e)
        {
            int j;
            DataGridViewCell cell;
            switch (cBWaveshape.SelectedIndex)
            {
                case 0:
                    InitRectangle(dht);
                    break;
                case 1:
                    InitTryangle(dht);
                    break;
                case 2:
                    InitSaw(dht);
                    break;
                case 3:
                    InitSinus(dht);
                    break;
            }
            dht.CalcDHT();
            dht.InvDHT();
            GResult.RowCount = 30;            // DataGridView for data display 30 Fourier components
            for (j = 0; j < GResult.RowCount; j++)        // put values into the DataGrid
            {
                cell = GResult[0, j];  // get cell to access
                cell.Value = j;
                cell = GResult[1, j];
                cell.Value = dht.hk[j];
                cell = GResult[2, j];
                cell.Value = (dht.hk[j] + dht.hk[dht.N - j]) / 2; 
                cell = GResult[3, j];
                cell.Value = (dht.hk[j] - dht.hk[dht.N - j]) / 2;
            }
            pGraph_Paint(this, null);
        }

        private void pGraph_Paint(object sender, PaintEventArgs e)
        {
            Point p1, p2;                                         // red for rebuild shape  
            int j;
            int offsetX = 50;
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
            if (order > 0)
            {
                for (j = 0; j < order; j++)
                {
                    p1.X = offsetX + Convert.ToInt32(j / 2);
                    p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(dht.y[j] * 5.0));
                    p2.X = offsetX + Convert.ToInt32(j / 2 + 1);
                    p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(dht.y[j + 1] * 5.0));
                    g.DrawLine(bluePen, p1, p2);
                    p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(dht.xw[j] * 5.0));
                    p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(dht.xw[j + 1] * 5.0));
                    g.DrawLine(redPen, p1, p2);
                }
            }
            g.Dispose();
        }
    }
}
