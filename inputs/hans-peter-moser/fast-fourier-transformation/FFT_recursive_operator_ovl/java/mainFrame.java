import java.awt.Canvas;
import java.awt.Color;
import java.awt.EventQueue;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Point;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;

import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.border.BevelBorder;
import javax.swing.table.TableColumnModel;


public class mainFrame {

	private JFrame frame;
	private JPanel pGraph;
	TDataGrid tableData;
	private JTable tDataTable;
	JComboBox comboBox;
	
	
	TFftAlgorithm fft;
	
	
	public class myCanvas extends Canvas {
    	
		private static final long serialVersionUID = 1L;
		
		public void paint(Graphics g) { 		 			              
			drawGraph(g);
		}
    }
	
	private void InitRectangle(TFftAlgorithm fft)
    {
        int j;
        for (j = 0; j < 2048; j++)
        {
            fft.y[j].real = 20.0;
            fft.y[j].imag = 0.0;
            fft.y[j + 2048].real = -20.0;
            fft.y[j + 2048].imag = 0.0;
        }
        fft.y[0].real = 0.0;
        fft.y[0].imag = 0.0;
        fft.y[4096].real = 0.0;
        fft.y[4096].imag = 0.0;
        fft.y[4096].real = 0.0;
        fft.y[4096].imag = 0.0;
        for (j = 0; j <= 4096; j++)
            fft.x[j] = fft.y[j];
    }

    private void InitTryangle(TFftAlgorithm fft)
    {
        int j;
        for (j = 0; j < 2048; j++)
        {
            fft.y[j].real = 20 - (double)(j) * 40.0 / 2048;
            fft.y[j].imag = 0.0;
            fft.y[j + 2049].real = -20.0 + ((double)(j) * 40.0 / 2048);
            fft.y[j + 2049].imag = 0.0;
        }
        fft.y[0].real = 20.0;
        fft.y[0].imag = 0.0;
        fft.y[2048].real = -20.0;
        fft.y[2048].imag = 0.0;
        fft.y[4096].real = 20.0;
        fft.y[4096].imag = 0.0;
        for (j = 0; j <= 4096; j++)
            fft.x[j] = fft.y[j];
    }

    private void InitSaw(TFftAlgorithm fft)
    {
        int j;
        for (j = 0; j < 2048; j++)
        {
            fft.y[j].real = (double)(j) * 20.0 / 2048.0;
            fft.y[j].imag = 0.0;
            fft.y[j + 2049].real = -(double)(2048 - j) * 20.0 / 2048.0;
            fft.y[j + 2049].imag = 0.0;
        }
        fft.y[0].real = 0.0;
        fft.y[0].imag = 0.0;
        fft.y[2048].real = 20.0;
        fft.y[2048].imag = 0.0;
        fft.y[4096].real = 0.0;
        fft.y[4096].imag = 0.0;
        for (j = 0; j <= 4096; j++)
            fft.x[j] = fft.y[j];
    }

    public void  drawGraph(Graphics g)
    {
        Point p1, p2;                                         // red for rebuild shape  
        int j;
        p1 = new Point();
        p2 = new Point();
        p1.x = 0;
        p1.y = (pGraph.getHeight() / 2);
        p2.x = pGraph.getWidth();
        p2.y = (pGraph.getHeight() / 2);
        g.setColor(new Color(0, 0, 0));
        g.drawLine((int)Math.round(p1.x),(int)Math.round(p1.y),(int)Math.round( p2.x),(int)Math.round(p2.y)); 
        if (4096 > 0)
        {
            for (j = 0; j < 4096; j++)
            {
                p1.x = (int)Math.round(j / 8);
                p1.y = (pGraph.getHeight() / 2) - (int)Math.round(fft.x[j].real * 5.0);
                p2.x = (int)Math.round(j / 8 + 1);
                p2.y = (pGraph.getHeight() / 2) - (int)Math.round(fft.x[j + 1].real * 5.0);
                g.setColor(new Color(0, 0, 255));
                g.drawLine((int)Math.round(p1.x),(int)Math.round(p1.y),(int)Math.round( p2.x),(int)Math.round(p2.y)); 
                p1.y = (pGraph.getHeight() / 2) -(int)Math.round(fft.xw[j] * 5.0);
                p2.y = (pGraph.getHeight() / 2) - (int)Math.round(fft.xw[j + 1] * 5.0);
                g.setColor(new Color(255, 0, 0));
                g.drawLine((int)Math.round(p1.x),(int)Math.round(p1.y),(int)Math.round( p2.x),(int)Math.round(p2.y)); 
            }
        }
    }

    
    private void SelectionChanged()
    {
    	int j;
    	switch(comboBox.getSelectedIndex())
    	{
    	case 0: InitRectangle(fft);
    	break;
    	case 1: InitTryangle(fft);
    	break;
    	case 2: InitSaw(fft);
    	break;
    	}
    	fft.CalcFFT();
        fft.InvFFT();
         for (j = 0; j < 30; j++)        // put values into the DataGrid
         {
         	 String str = Integer.toString(j);
              tableData.setValueAt(str, j, 0);
              str = Double.toString(Math.round(fft.y[j].real*10000)/10000.0);
              tableData.setValueAt(str, j, 1);
              str = Double.toString(Math.round(fft.y[j].imag*10000)/10000.0);
              tableData.setValueAt(str, j, 2);
         }
    }

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					mainFrame window = new mainFrame();
					window.frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public mainFrame() {
		int j;
		initialize();
        fft = new TFftAlgorithm(4096);       // initialise fft class for 1000 samples
        InitRectangle(fft);
        fft.CalcFFT();
        fft.InvFFT();
        for (j = 0; j < 30; j++)        // put values into the DataGrid
        {
        	 String str = Integer.toString(j);
             tableData.setValueAt(str, j, 0);
             str = Double.toString(Math.round(fft.y[j].real*10000)/10000.0);
             tableData.setValueAt(str, j, 1);
             str = Double.toString(Math.round(fft.y[j].imag*10000)/10000.0);
             tableData.setValueAt(str, j, 2);
        }
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frame = new JFrame();
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setBounds(100, 100, 597, 580);
		frame.getContentPane().setLayout(null);
		pGraph = new JPanel();
		final Canvas canvas = new myCanvas();
		canvas.setBackground(Color.WHITE);
		pGraph.addComponentListener(new ComponentAdapter() {
			@Override
			public void componentResized(ComponentEvent arg0) {
				canvas.setBounds(0, 0, pGraph.getWidth(), pGraph.getHeight());
			}
		});
		pGraph.setBackground(Color.WHITE);
		pGraph.setBounds(10, 11, 561, 255);
		frame.getContentPane().add(pGraph);
		pGraph.add(canvas);
		pGraph.setLayout(null);
		
		tableData = new TDataGrid(3, 30); 
		tDataTable = new JTable(tableData);
		tDataTable.setRowHeight(25);
		tDataTable.setBorder(new BevelBorder(BevelBorder.LOWERED, null, null, null, null));
		tDataTable.setFont(new Font("Tahoma", Font.PLAIN, 14));
		tDataTable.setBounds(20, 25, 477, 750);
		frame.getContentPane().add(tDataTable);
		JScrollPane scroll = new JScrollPane(tDataTable);
	    scroll.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		scroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
		frame.getContentPane().add(scroll);
	    scroll.setBounds(10, 310, 561, 221);
	    
	    String[] elements= {"Rectangle","Triangle","Sawtooth"};
	    comboBox = new JComboBox(elements);
	    comboBox.addItemListener(new ItemListener() {
	    	public void itemStateChanged(ItemEvent e) {
	    		SelectionChanged();
	    		canvas.repaint();
	    	}
	    });
	    comboBox.setBounds(404, 277, 167, 22);
	    frame.getContentPane().add(comboBox);
	    TableColumnModel columnModel = tDataTable.getColumnModel();
	    columnModel.getColumn(0).setHeaderValue("order");
	    columnModel.getColumn(1).setHeaderValue("Real");
	    columnModel.getColumn(2).setHeaderValue("Im");	   
	}

}
