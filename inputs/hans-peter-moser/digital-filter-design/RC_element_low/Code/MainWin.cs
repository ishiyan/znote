
using System;
using System.Drawing;
using System.Windows.Forms;

/*                             Digital RC low pass filter                    */
/*                               www.mosismath.com                           */

namespace WindowsFormsApplication1
{

    public partial class MainWin : Form
    {
        public const int datapoints = 500; // number of datapoints for the interpolation
      
        public TextBox[,] tbm;
        public TextBox[] tbs;
        public TextBox[] tbx;

        double[] a = new double[2];
        double[] b = new double[2];
        double[] z_a = new double[2];
        double[] z_b = new double[2];
        double[] t_in = new double[datapoints];
        double[] y_in = new double[datapoints];
        double[] y_out = new double[datapoints];
        
        double fs = 10000.0;
        double f = 200.0 ;
        double fc = 300.0;


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
            int i;
            double t;
            double[] a = new double[2];
            double[] b = new double[2];
           
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

            // Calculate T
            t = Math.PI * fc / fs;

            // Create an input singal
            for (i = 0; i < datapoints; i++)
            {
                t_in[i] = i / fs;
                y_in[i] = 20.0 * Math.Sin(2.0 * Math.PI * t_in[i] * f);
            }

            // Build filter parameters
            b[0] = 1 / (1.0 + 1.0 / t);
            b[1] = b[0];
            a[0] = 1.0;
            a[1] = (1.0 - 1.0 / t ) / (1.0 + 1.0 / t );

            // Process the singal and compute the output
            y_out[0] = 0;
            for (i = 1; i < datapoints; i++)
            {
                y_out[i] = y_in[i] * b[0] + y_in[i-1] * b[1] - y_out[i-1] * a[1];
            }
            DrawGraph(datapoints, 0, t_in[datapoints - 1], true);
        }

        private void pGraph_Paint(object sender, PaintEventArgs e)
        {
            DrawGraph(datapoints, 0, t_in[datapoints - 1], false);
        }  
    }
}
