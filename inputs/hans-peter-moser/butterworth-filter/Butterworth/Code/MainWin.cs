
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
        double f = 20.0;
        double fs = 10000.0;
        double fc = 300.0;

        double[] t_in = new double[datapoints];
        double[] y_in = new double[datapoints];
        double[] y_out = new double[datapoints];

        public double[] za;
        public double[] zb;

        class TButterworth
        {
            int order;
            public double[] a_z;
            public double[] b_z;
            private double[] a_s = { 1.0 };
            private double tc = 1.0;
           
            public TButterworth(int iOrder, double dTc)
            {
                order = iOrder;
                tc = dTc;
                a_z = new double[order + 1];
                b_z = new double[1];
            }


            public void CalcButterworth(int order)
            {
                int i = 1;
                double[] poly = new double[3];
                double[] poly2 = new double[2];
                poly[0] = 1.0;

                if (order % 2 == 0)
                {
                    poly[2] = 1.0;
                    for (i = 1; i <= order / 2; i++)
                    {
                        poly[1] = 2.0 * Math.Cos((2 * i - 1) * Math.PI / 2 / order);
                        a_s = Poly.Mult(a_s, poly);
                    }
                }
                else
                {
                    poly2[0] = 1.0;
                    poly2[1] = 1.0;
                    a_s = Poly.Mult(a_s, poly2);
                    poly[2] = 1.0;
                    for (i = 2; i <= (order + 1) / 2; i++)
                    {
                        poly[1] = 2.0 * Math.Cos((i - 1) * Math.PI / order);
                        a_s = Poly.Mult(a_s, poly);
                    }
                }
            }

            public void TransformToZPlane(bool bHighPass)
            {
                int i, j;
                double[] tempA = new double[2];
                List<double[]> aa = new List<double[]>();
                for (i = 0; i <= order; i++)
                {
                    aa.Add(new double[] { 1, -1 });
                }
                tempA[0] = 1;
                if (bHighPass)
                {
                    tempA[1] = -1;
                    b_z = Poly.Power(tempA, order);
                    b_z = Poly.Mult(b_z, Math.Pow(2.0 / tc, order));
                }
                else
                {
                    tempA[1] = 1;
                    b_z = Poly.Power(tempA, order);
                }
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
                for (i = order; i >= 0; i--)
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
                        scalefactor = pGraph.Height / maxVal / 2.2;
                    else
                        scalefactor = pGraph.Height / Math.Abs(minVal) / 2.2;
                }
                else
                    scalefactor = 5.0;
                drawCeroline = true;
            }
            else
            {
                scalefactor = pGraph.Height / (maxVal) / 1.1;
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

            double t = 2.0 * Math.PI * fc / fs;

            for (i = 0; i < datapoints; i++)
            {
                t_in[i] = i / fs;
                y_in[i] = 20.0 * Math.Sin(2.0 * Math.PI * t_in[i] * f);
            }

            TButterworth butter = new TButterworth(order, t);

            butter.CalcButterworth(order);
            butter.TransformToZPlane(cbHighPass.Checked == true);
            za = butter.a_z;
            zb = butter.b_z;

            for (i = 0; i < datapoints; i++)
            {
                t_in[i] = i / fs;
                y_in[i] = 20.0 * Math.Sin(2.0 * Math.PI * t_in[i] * f);
            }

            for (i = 0; i <= order; i++)
            {
                y_out[i] = 0;
                for (j = 0; j <= i; j++)
                {
                    y_out[i] = y_out[i] + y_in[i-j] * zb[j];
                }
                for (j = 1; j <= i; j++)
                {
                    y_out[i] = y_out[i] - y_out[i-j] * za[j];
                }
            }

            for (i = order + 1; i < datapoints; i++)
            {
                y_out[i] = 0;
                for (j = 0; j <= order; j++)
                {
                    y_out[i] = y_out[i] + y_in[i - j] * zb[j];
                }
                for (j = 1; j <= order; j++)
                {
                    y_out[i] = y_out[i] - y_out[i - j] * za[j];
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
