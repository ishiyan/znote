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
            this.pBild = new System.Windows.Forms.Panel();
            this.GResult = new System.Windows.Forms.DataGridView();
            this.Index = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Value = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Column1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.label1 = new System.Windows.Forms.Label();
            this.cBWaveshape = new System.Windows.Forms.ComboBox();
            ((System.ComponentModel.ISupportInitialize)(this.GResult)).BeginInit();
            this.SuspendLayout();
            // 
            // pBild
            // 
            this.pBild.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.pBild.Location = new System.Drawing.Point(12, 12);
            this.pBild.Name = "pBild";
            this.pBild.Size = new System.Drawing.Size(569, 248);
            this.pBild.TabIndex = 1;
            this.pBild.Paint += new System.Windows.Forms.PaintEventHandler(this.pGraph_Paint);
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
            this.GResult.Size = new System.Drawing.Size(569, 250);
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
            this.label1.Location = new System.Drawing.Point(325, 271);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(68, 13);
            this.label1.TabIndex = 5;
            this.label1.Text = "Wave shape";
            // 
            // cBWaveshape
            // 
            this.cBWaveshape.FormattingEnabled = true;
            this.cBWaveshape.Items.AddRange(new object[] {
            "Rectangle",
            "Triangle",
            "Sawtooth"});
            this.cBWaveshape.Location = new System.Drawing.Point(412, 268);
            this.cBWaveshape.Name = "cBWaveshape";
            this.cBWaveshape.Size = new System.Drawing.Size(169, 21);
            this.cBWaveshape.TabIndex = 6;
            this.cBWaveshape.Text = "Rectangle";
            this.cBWaveshape.SelectedIndexChanged += new System.EventHandler(this.cBWaveshape_SelectedIndexChanged);
            // 
            // MainWin
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(590, 564);
            this.Controls.Add(this.cBWaveshape);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.GResult);
            this.Controls.Add(this.pBild);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "MainWin";
            this.Text = "Goertzel 1";
            this.Load += new System.EventHandler(this.MainWin_Load);
            ((System.ComponentModel.ISupportInitialize)(this.GResult)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Panel pBild;
        private System.Windows.Forms.DataGridView GResult;
        private System.Windows.Forms.DataGridViewTextBoxColumn Index;
        private System.Windows.Forms.DataGridViewTextBoxColumn Value;
        private System.Windows.Forms.DataGridViewTextBoxColumn Column1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ComboBox cBWaveshape;
    }
}

