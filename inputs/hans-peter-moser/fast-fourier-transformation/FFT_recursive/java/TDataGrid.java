import java.util.ArrayList;

import javax.swing.table.AbstractTableModel;

public class TDataGrid extends AbstractTableModel {
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	String[][] matrix; 
	String[] title; 
	
	int iWidth;
	int iHeight;
	
	public TDataGrid(int w, int h) {
		int i,j;
		matrix = new String[h][w] ;
		title = new String[w];
		for(i=0; i < h; i++)
		{
			for(j=0; j < w;j++)
				matrix[i][j]  = "";
		}
		for(j=0; j < w;j++)
			title[j] = "x";
		iWidth = w;
		iHeight = h;
	}

	@Override
	public int getRowCount() {
		// TODO Auto-generated method stub
		return iHeight;
	}

	@Override
	public int getColumnCount() {
		// TODO Auto-generated method stub
		return iWidth;
	}

	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {
		// TODO Auto-generated method stub
		return matrix[rowIndex][columnIndex];
	}
	
	public void setValueAt(String obj, int rowIndex, int columnIndex) {
		// TODO Auto-generated method stub
		matrix[rowIndex][columnIndex] = obj;
		fireTableDataChanged();
	}
	
	public void setTitleAt(String obj, int columnIndex) {
		// TODO Auto-generated method stub
		title[columnIndex] = obj;
		fireTableDataChanged();
	}
}
