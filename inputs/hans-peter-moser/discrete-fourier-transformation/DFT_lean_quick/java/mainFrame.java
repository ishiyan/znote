import java.awt.Canvas;
import java.awt.Color;
import java.awt.EventQueue;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Point;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.border.BevelBorder;
import javax.swing.table.TableColumnModel;
import javax.swing.JComboBox;
import java.awt.event.ItemListener;
import java.awt.event.ItemEvent;


public class mainFrame {

	private JFrame frame;
	private JPanel pGraph;
	TDataGrid tableData;
	private JTable tDataTable;
	JComboBox comboBox;
	
	
	TDftAlgorithm dft;
	int order = 1000;
	
	public class myCanvas extends Canvas {
    	
		private static final long serialVersionUID = 1L;
		
		public void paint(Graphics g) { 		 			              
			drawGraph(g);
		}
    }
	
	private void InitRectangle(TDftAlgorithm dft) // init  rectangle signal
    {
        int j;
        for (j = 0; j < 500; j++)
        {
            dft.y[j] = 20.0;
            dft.y[j + 501] = -20.0;
        }
        dft.y[0] = 0.0;
        dft.y[500] = 0.0;
        dft.y[1000] = 0.0;
    }


    private void InitTrytangle(TDftAlgorithm dft)
    {
        int j;
        for (j = 0; j < 500; j++)
        {
            dft.y[j] = 20 - (double)(j) * 40.0 / 500.0;
            dft.y[j + 501] = -20.0 + ((double)(j) * 40.0 / 500.0);
        }
        dft.y[0] = 20.0;
        dft.y[500] = -20.0;
        dft.y[1000] = 20.0;
    }


    private void InitSaw(TDftAlgorithm dft)
    {
        int j;
        for (j = 0; j < 500; j++)
        {
            dft.y[j] = (double)(j) * 20.0 / 500.0;
            dft.y[j + 501] = -(double)(500 - j) * 20.0 / 500.0;
        }
        dft.y[0] = 0.0;
        dft.y[500] = 20.0;
        dft.y[1000] = 0.0;
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
        if (order > 0)
        {
            for (j = 0; j < order; j++)
            {
                p1.x = (int)Math.round(j / 2);
                p1.y = (pGraph.getHeight() / 2) - (int)Math.round(dft.y[j] * 5.0);
                p2.x = (int)Math.round(j / 2 + 1);
                p2.y = (pGraph.getHeight() / 2) - (int)Math.round(dft.y[j + 1] * 5.0);
                g.setColor(new Color(0, 0, 255));
                g.drawLine((int)Math.round(p1.x),(int)Math.round(p1.y),(int)Math.round( p2.x),(int)Math.round(p2.y)); 
                p1.y = (pGraph.getHeight() / 2) -(int)Math.round(dft.xw[j] * 5.0);
                p2.y = (pGraph.getHeight() / 2) - (int)Math.round(dft.xw[j + 1] * 5.0);
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
    	case 0: InitTrytangle(dft);
    	break;
    	case 1: InitTrytangle(dft);
    	break;
    	case 2: InitSaw(dft);
    	break;
    	}
    	 dft.CalcDFT();
         dft.InvDFT();
         for (j = 0; j < 30; j++)        // put values into the DataGrid
         {
         	 String str = Integer.toString(j);
              tableData.setValueAt(str, j, 0);
              str = Double.toString(Math.round(dft.a[j]*10000)/10000.0);
              tableData.setValueAt(str, j, 1);
              str = Double.toString(Math.round(dft.b[j]*10000)/10000.0);
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
        dft = new TDftAlgorithm(order);       // initialise fft class for 1000 samples
        InitRectangle(dft);
        dft.CalcDFT();
        dft.InvDFT();
        for (j = 0; j < 30; j++)        // put values into the DataGrid
        {
        	 String str = Integer.toString(j);
             tableData.setValueAt(str, j, 0);
             str = Double.toString(Math.round(dft.a[j]*10000)/10000.0);
             tableData.setValueAt(str, j, 1);
             str = Double.toString(Math.round(dft.b[j]*10000)/10000.0);
             tableData.setValueAt(str, j, 2);
        }
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frame = new JFrame();
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setBounds(100, 100, 597, 536);
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
		pGraph.setBounds(10, 11, 561, 213);
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
	    scroll.setBounds(10, 266, 561, 221);
	    
	    String[] elements= {"Rectangle","Triangle","Sawtooth"};
	    comboBox = new JComboBox(elements);
	    comboBox.addItemListener(new ItemListener() {
	    	public void itemStateChanged(ItemEvent e) {
	    		SelectionChanged();
	    		canvas.repaint();
	    	}
	    });
	    comboBox.setBounds(404, 235, 167, 22);
	    frame.getContentPane().add(comboBox);
	    TableColumnModel columnModel = tDataTable.getColumnModel();
	    columnModel.getColumn(0).setHeaderValue("order");
	    columnModel.getColumn(1).setHeaderValue("Real");
	    columnModel.getColumn(2).setHeaderValue("Im");	   	
	}
}
