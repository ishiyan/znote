
using System;
using System.Drawing;
using System.Windows.Forms;

/*               Reinsch DFT               */
/*             www.mosismath.com           */


namespace WindowsFormsApplication1
{

    public struct TComplex
    {
        public double real;
        public double imag;
    }

    public partial class MainWin : Form
    {
        public const int order = 1000;

        public class TDftAlgorithm
        {
            int N;
            public TComplex[] w;
            public TComplex[] y;
            public TComplex[] c;
            public double[] xw;


            public TDftAlgorithm(int order)
            {
                N = order;
                w = new TComplex[N + 1];
                y = new TComplex[N + 1];
                c = new TComplex[N + 1];
                xw = new double[N + 1];
            }

            public void CalcReinsch() // Reinsch algorithm for DFT
            {
                int k, n;
                TComplex b1, a1, v0, v1, v2;
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
            for (j = 0; j < order; j++)
            {
                if (j < (order / 2))
                {
                    dft.y[j].real = 20.0;
                    dft.y[j].imag = 0.0;
                }
                else
                {
                    dft.y[j].real = -20.0;
                    dft.y[j].imag = 0.0;
                }
            }
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
            for (j = 0; j < (order / 2); j++)
            {
                dft.y[j].real = (double)(j) * 20.0 / (double)(order / 2);
                dft.y[j].imag = 0.0;
                dft.y[j + (order / 2)].real = -(double)(500 - j) * 20.0 / (double)(order / 2);
                dft.y[j + (order / 2)].imag = 0.0;
            }
            dft.y[0].real = 0.0;
            dft.y[0].imag = 0.0;
            dft.y[(order / 2)].real = 20.0;
            dft.y[(order / 2)].imag = 0.0;
            dft.y[order - 1].real = 0.0;
            dft.y[order - 1].imag = 0.0;
        }


        private void MainWin_Load(object sender, EventArgs e)
        {
            int j;
            dft = new TDftAlgorithm(order);
            DataGridViewCell cell;
            InitRectangle(dft);
            dft.CalcReinsch();
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
            dft.CalcReinsch();
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
                    p1.X = Convert.ToInt32(j / 2);
                    p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(dft.y[j].real * 5.0));
                    p2.X = Convert.ToInt32(j / 2 + 1);
                    p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(dft.y[j + 1].real * 5.0));
                    g.DrawLine(bluePen, p1, p2);
                    p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(dft.xw[j] * 5.0));
                    p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(dft.xw[j + 1] * 5.0));
                    g.DrawLine(redPen, p1, p2);
                }
            }
            g.Dispose();
        }
    }
}
