namespace WindowsFormsApplication1
{
    partial class MainWin
    {
        /// <summary>
        /// Erforderliche Designervariable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Verwendete Ressourcen bereinigen.
        /// </summary>
        /// <param name="disposing">True, wenn verwaltete Ressourcen gelöscht werden sollen; andernfalls False.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Vom Windows Form-Designer generierter Code

        /// <summary>
        /// Erforderliche Methode für die Designerunterstützung.
        /// Der Inhalt der Methode darf nicht mit dem Code-Editor geändert werden.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainWin));
            this.pGraph = new System.Windows.Forms.Panel();
            this.GResult = new System.Windows.Forms.DataGridView();
            this.Index = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Value = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Column1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.label1 = new System.Windows.Forms.Label();
            this.cBWaveshape = new System.Windows.Forms.ComboBox();
            ((System.ComponentModel.ISupportInitialize)(this.GResult)).BeginInit();
            this.SuspendLayout();
            // 
            // pGraph
            // 
            this.pGraph.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.pGraph.Location = new System.Drawing.Point(12, 12);
            this.pGraph.Name = "pGraph";
            this.pGraph.Size = new System.Drawing.Size(555, 248);
            this.pGraph.TabIndex = 1;
            this.pGraph.Paint += new System.Windows.Forms.PaintEventHandler(this.pGraph_Paint);
            // 
            // GResult
            // 
            this.GResult.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.GResult.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.Index,
            this.Value,
            this.Column1});
            this.GResult.Location = new System.Drawing.Point(12, 302);
            this.GResult.Name = "GResult";
            this.GResult.Size = new System.Drawing.Size(555, 250);
            this.GResult.TabIndex = 2;
            // 
            // Index
            // 
            this.Index.HeaderText = "Order";
            this.Index.Name = "Index";
            // 
            // Value
            // 
            this.Value.HeaderText = "Real";
            this.Value.Name = "Value";
            this.Value.Width = 150;
            // 
            // Column1
            // 
            this.Column1.HeaderText = "Im";
            this.Column1.Name = "Column1";
            this.Column1.Width = 150;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(327, 269);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(68, 13);
            this.label1.TabIndex = 6;
            this.label1.Text = "Wave shape";
            // 
            // cBWaveshape
            // 
            this.cBWaveshape.FormattingEnabled = true;
            this.cBWaveshape.Items.AddRange(new object[] {
            "Rectangle",
            "Triangle",
            "Sawtooth"});
            this.cBWaveshape.Location = new System.Drawing.Point(398, 266);
            this.cBWaveshape.Name = "cBWaveshape";
            this.cBWaveshape.Size = new System.Drawing.Size(169, 21);
            this.cBWaveshape.TabIndex = 5;
            this.cBWaveshape.Text = "Rectangle";
            this.cBWaveshape.SelectedIndexChanged += new System.EventHandler(this.cBWaveshape_SelectedIndexChanged);
            // 
            // MainWin
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(577, 564);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.cBWaveshape);
            this.Controls.Add(this.GResult);
            this.Controls.Add(this.pGraph);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "MainWin";
            this.Text = "Reinsch";
            this.Load += new System.EventHandler(this.MainWin_Load);
            ((System.ComponentModel.ISupportInitialize)(this.GResult)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Panel pGraph;
        private System.Windows.Forms.DataGridView GResult;
        private System.Windows.Forms.DataGridViewTextBoxColumn Index;
        private System.Windows.Forms.DataGridViewTextBoxColumn Value;
        private System.Windows.Forms.DataGridViewTextBoxColumn Column1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ComboBox cBWaveshape;
    }
}

