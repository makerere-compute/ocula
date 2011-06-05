using System;
using System.Linq;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Text.RegularExpressions;

namespace ocula
{
    public partial class parsite : Form
    {
        public parsite(String imageFilename,int match, String message, TimeSpan elapsed, short status)
        {
            InitializeComponent();

            imgCode.Image = new Bitmap(imageFilename);
            txtMessage.Text = message;
          //  txtStatus.Text = String.Format("{0:X}", status);
            txtTime.Text = String.Format("{0} sec", elapsed.TotalSeconds);
            if (match > 0)
            {
                txtMessage.ForeColor = Color.Red;
            }
            else
            {
                txtMessage.ForeColor = Color.Green;
            }

        }

        private void btnBack_Click(object sender, EventArgs e)
        {
            imgCode.Image.Dispose();
            this.Close();
        }

        private void btnBrowse_Click(object sender, EventArgs e)
        {
            
            System.Diagnostics.Process.Start(txtMessage.Text,"");
        }
    }
}