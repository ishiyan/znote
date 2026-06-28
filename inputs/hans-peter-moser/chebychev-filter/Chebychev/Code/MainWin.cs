
using System;
using System.Linq;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;



namespace WindowsFormsApplication1
{

    public partial class MainWin : Form
    {
        public int order = 3;
        public const int datapoints = 500; // number of datapoints for the interpolation
        public double f = 200.0;
        public double fs = 10000.0;
        public double fc = 300.0;

        double[] t_in = new double[datapoints];
        double[] y_in = new double[datapoints];
        double[] y_out = new double[datapoints];

        public double[] a;
        public double[] b;

        class TChebychev
        {
            private int order;
            public double[] a_z;
            public double[] b_z;
            private double[] a_s;
            private double tc = 1.0;
            private double b_s = 1.0;
            private double e = 0.14;
                      
            public TChebychev(int iOrder, double dTc, double ripple)
            {
                int i;
                e = Math.Sqrt(Math.Pow(10, 0.1 * ripple)-1);
                order = iOrder;
                tc =  dTc;
                a_z = new double[order + 1];
                b_z = new double[1];
            }

            private double Fact(double value)
            {
                int i;
                double res = 1;
                if (value != 0)
                {
                    for (i = (int)(Math.Round(value)); i > 0; i--)
                    {
                        res = res * value;
                        value--;
                    }
                }
                return res;
            }

          
            public void CalcChebychev(int order, double t)
            {
                int i = 1;
                double[] poly = new double[3];
                double[] poly2 = new double[2];
                double nu = Math.Log(1.0 / e + Math.Sqrt(1.0 / e * e + 1.0)) / order;
                double sigma;
                double omega;
                a_s = new double[1];
                a_s[0] = 1.0;
                b_s = 1.0;

                // The denominator of the transfer function
                if (order % 2 == 0)
                {
                    poly[0] = 1.0;
                    for (i = 0; i < order / 2; i++)
                    {
                        sigma = Math.Sinh(nu) * Math.Sin(Math.PI * (2.0 * i + 1.0) / 2.0 / order);
                        omega = Math.Cosh(nu) * Math.Cos(Math.PI * (2.0 * i + 1.0) / 2.0 / order);
                        poly[1] = 2.0 * sigma;
                        poly[2] = sigma * sigma + omega * omega;
                        a_s = Poly.Mult(a_s, poly);
                        // the enumerator part
                        b_s = b_s * sigma * sigma + omega * omega;
                    }
                }
                else
                {
                    poly[0] = 1.0;
                    for (i = 0; i < (order + 1) / 2; i++)
                    {
                        sigma = -Math.Sinh(nu) * Math.Sin(Math.PI * (2.0 * i + 1.0) / 2.0 / order);
                        omega = Math.Cosh(nu) * Math.Cos(Math.PI * (2.0 * i + 1.0) / 2.0 / order);
                        if (i < (order) / 2)
                        {
                            poly[1] = -2.0 * sigma;
                            poly[2] = sigma * sigma + omega * omega;
                            a_s = Poly.Mult(a_s, poly);
                            // the enumerator part
                            b_s = b_s * sigma * sigma + omega * omega;
                        }
                        else
                        {
                            poly2[0] = 1;
                            poly2[1] = -sigma;
                            a_s = Poly.Mult(a_s, poly2);
                            // the enumerator part
                            b_s = b_s * sigma;
                        }
                    }
                }
                // the amplification in the enumerator
                if (order % 2 == 0)
                    b_s = -b_s * Math.Sqrt(1.0 + e * e);
                else
                    b_s = -b_s;
            }


            public void TransformToZPlane(bool bHighPass)
            {
                int i, j;
                List<double[]> aa = new List<double[]>();
                for (i = 0; i <= order; i++)
                {
                    aa.Add(new double[] { 1.0, -1.0 });
                }
                double[] tempA = { 1.0, 1.0 };

                tempA[0] = 1;
                if (bHighPass)
                {
                    tempA[1] = -1;
                    b_z = Poly.Power(tempA, order);
                    b_z = Poly.Mult(b_z, Math.Pow(2.0 / tc, order));
                    double[] temp = new double[a_z.Length];
                    for (i = 0; i < a_s.Length; i++)
                        temp[i] = a_s[a_s.Length - 1 - i];
                    for (i = 0; i < a_s.Length; i++)
                        a_s[i] = temp[i];
                }
                else
                {
                    tempA[1] = 1;
                    b_z = Poly.Power(tempA, order);
                }
                b_z = Poly.Mult(b_z, b_s);
                tempA[1] = 1;
               
                for (i = 0; i <= order; i++)
                {
                    double[] tempEl = aa.ElementAt(i);
                    tempEl = Poly.Mult(Poly.Power(tempA, i), Poly.Power(tempEl, order - i));
                    tempEl = Poly.Mult(tempEl, a_s[i] * Math.Pow(2.0 / tc, order - i));
                    aa.RemoveAt(i);
                    aa.Insert(i, tempEl);
                }
                for (i = 0; i <= order; i++)
                {
                    a_z[i] = 0;
                    for (j = 0; j <= order; j++)
                        a_z[i] = a_z[i] + aa.ElementAt(j)[i];
                }
                for (i =0; i < b_z.Length; i++)
                {
                    b_z[i] = b_z[i] / a_z[0];
                }
                for (i = a_z.Length-1; i >= 0; i--)
                {
                    a_z[i] = a_z[i] / a_z[0];
                }       
            }
        }
       

        public MainWin()
        {
            InitializeComponent();
            tbSampleF.Text = Math.Round(fs, 1).ToString();
            tbCutoffF.Text = Math.Round(fc, 1).ToString();
            tbSign.Text = Math.Round(f, 1).ToString();
        }

 
        public void DrawGraph(int maxPoints, double minX, double maxX, bool doClear)
        {
            Point p1, p2;
            int j;
            double maxTime = -1.0;
            double maxVal = -1.0;
            double minVal = 1.0;
            double scalefactor;
            bool drawCeroline;
            for (j = 0; j < maxPoints - 1; j++)
            {
                if ((t_in[j] >= minX) && (t_in[j] <= maxX))
                {
                    if (maxTime < t_in[j])
                        maxTime = t_in[j];
                    if (maxVal < y_in[j])
                        maxVal = y_in[j];
                    if (minVal > y_in[j])
                        minVal = y_in[j];
                }
            }
            maxTime = maxTime * 1.05;
            maxTime = maxTime * 1.05;
            if (minVal < 0)
            {
                if (maxVal > 0)
                {
                    if (maxVal > Math.Abs(minVal))
                        scalefactor = pGraph.Height / maxVal / 2.4;
                    else
                        scalefactor = pGraph.Height / Math.Abs(minVal) / 2.4;
                }
                else
                    scalefactor = 5.0;
                drawCeroline = true;
            }
            else
            {
                scalefactor = pGraph.Height / (maxVal) / 1.2;
                drawCeroline = false;
            }
            p1 = new Point();
            p2 = new Point();
            Graphics g = pGraph.CreateGraphics();
            if (doClear)
                g.Clear(Color.White);
            Pen bluePen = new Pen(Color.Blue, 2);
            Pen redPen = new Pen(Color.Red, 2);
            Pen blackPen = new Pen(Color.Black, 2);
            if (drawCeroline)
            {
                p1.X = 0;
                p1.Y = (pGraph.Height / 2);
                p2.X = pGraph.Width;
                p2.Y = (pGraph.Height / 2);
                g.DrawLine(blackPen, p1, p2);
            }
            bluePen.Width = 1;
            if (maxTime > 0) // draw interpolated graph
            {
                for (j = 0; j < maxPoints - 1; j++)
                {
                    if ((t_in[j] >= minX) && (t_in[j] <= maxX))
                    {
                        p1.X = Convert.ToInt32(t_in[j] * pGraph.Width / (double)maxTime);
                        p2.X = Convert.ToInt32(t_in[j + 1] * pGraph.Width / (double)maxTime);
                        if (drawCeroline)
                        {
                            p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y_in[j] * scalefactor));
                            p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y_in[j + 1] * scalefactor));
                        }
                        else
                        {
                            p1.Y = (pGraph.Height) - Convert.ToInt32(Math.Round(y_in[j] * scalefactor));
                            p2.Y = (pGraph.Height) - Convert.ToInt32(Math.Round(y_in[j + 1] * scalefactor));
                        }
                        if (p2.X > p1.X)
                            g.DrawLine(redPen, p1, p2);
                    }
                }

                for (j = 0; j < maxPoints - 1; j++)
                {
                    if ((t_in[j] >= minX) && (t_in[j] <= maxX))
                    {
                        p1.X = Convert.ToInt32(t_in[j] * pGraph.Width / (double)maxTime);
                        p2.X = Convert.ToInt32(t_in[j + 1] * pGraph.Width / (double)maxTime);
                        if (drawCeroline)
                        {
                            p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y_out[j] * scalefactor));
                            p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y_out[j + 1] * scalefactor));
                        }
                        else
                        {
                            p1.Y = (pGraph.Height) - Convert.ToInt32(Math.Round(y_out[j] * scalefactor));
                            p2.Y = (pGraph.Height) - Convert.ToInt32(Math.Round(y_out[j + 1] * scalefactor));
                        }
                        if (p2.X > p1.X)
                            g.DrawLine(bluePen, p1, p2);
                    }
                }
            }
            g.Dispose();
        }


        private void button1_Click(object sender, EventArgs e)
        {
            int i, j;
            double t;
            try
            {
                fs = Convert.ToDouble(tbSampleF.Text);
                fc = Convert.ToDouble(tbCutoffF.Text);
                f = Convert.ToDouble(tbSign.Text);
                if (fc > fs)
                {
                    MessageBox.Show("Cut off frequency must be smaller then sample frequency!");
                    fc = fs;
                    tbCutoffF.Text = Math.Round(fc, 1).ToString();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

            // compute filter parameters
            t = 2.0 * Math.PI * fc / fs;
            TChebychev cheb = new TChebychev(order, t, 0.2);
            cheb.CalcChebychev(order, t);
            cheb.TransformToZPlane(cbHighPass.Checked == true);
            
            a = cheb.a_z;
            b = cheb.b_z;

            // create the sample signal
            for (i = 0; i < datapoints; i++)
            {
                t_in[i] = i / fs;
                y_in[i] = 20.0 * Math.Sin(2.0 * Math.PI * t_in[i] * f);
            }

            // process the samlpe signal
            for (i = 0; i < a.Length; i++)
            {
                y_out[i] = 0;
                for (j = 0; j <= i; j++)
                {
                    y_out[i] = y_out[i] + y_in[i-j] * b[j];
                }
                for (j = 1; j <= i; j++)
                {
                    y_out[i] = y_out[i] - y_out[i-j] * a[j];
                }
            }
            for (i = a.Length; i < datapoints; i++)
            {
                y_out[i] = 0;
                for (j = 0; j < a.Length; j++)
                {
                    y_out[i] = y_out[i] + y_in[i - j] * b[j];
                }
                for (j = 1; j < a.Length; j++)
                {
                    y_out[i] = y_out[i] - y_out[i - j] * a[j];
                }
            }
            DrawGraph(datapoints, 0, t_in[datapoints - 1], true);
        }

        private void pGraph_Paint(object sender, PaintEventArgs e)
        {
            DrawGraph(datapoints, 0, t_in[datapoints - 1], false);
        }  
    }
}
