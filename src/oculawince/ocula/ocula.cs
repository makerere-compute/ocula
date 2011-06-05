/***
 * @author Mistaguy
 * ****/
using System;
using System.Linq;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using Microsoft.WindowsMobile.Forms;
using System.Runtime.InteropServices;
using System.IO;
using System.Threading;

namespace ocula
{
    public partial class frmocula : Form
    {
        private short taskStatus = -1;
        private DateTime taskStartTime;
        private List<String> taskParams = new List<string>();
        private CameraCaptureDialog camera;
        private SelectPictureDialog library;
        string  ParasiteStoreLocation;
        public frmocula()
        {
            InitializeComponent();

            camera = new CameraCaptureDialog();
            camera.Owner = this;
            camera.Mode = CameraCaptureMode.Still;
            camera.Resolution = new Size(640, 480);
            camera.StillQuality = CameraCaptureStillQuality.Low;
            camera.Title = "ocula - Camera";

            library = new SelectPictureDialog();
            library.Title = "ocula - Photo Library";
            library.CameraAccess = false;
            library.Filter = "JPG Files (*.JPG)|*.JPG";
            library.Owner = this;
            ParasiteStoreLocation = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().GetName().CodeBase) + @"\parasite.jpg";


        }

        private void mnuImage_Click(object sender, EventArgs e)
        {
            String filename = null;

            lblStart.Visible = false;

            // Try using a camera if the device supports it
            try
            {
                if (camera.ShowDialog() == DialogResult.OK)
                {
                    filename = camera.FileName;
                }
                else
                {
                    // If camera shot is aborted throw an exception
                    // to trigger the image library dialog to be displayed
                    throw new Exception();
                }
            }
            catch (Exception) 
            {
                // If there is a camera error or if the device
                // does not support a camera, pull up the image
                // library instead
                
                if (library.ShowDialog() == DialogResult.OK)
                {
                    filename = library.FileName;
                }
            }

            // A valid filename is required
            if (filename != null)
            {
                if (imgImage.Image != null)
                {
                    imgImage.Image.Dispose();
                    imgImage.Image = null;
                }
                imgImage.Image = new Bitmap(filename);

              

                // Create an asynchronous thread to process the image
                // without freezing up the interface
                taskParams.Add(filename);
                taskParams.Add(ParasiteStoreLocation);
                timer.Enabled = true;
                pnlLoading.Visible = true;
                mnuImage.Enabled = false;
                mnuExit.Enabled = false;
                WaitCallback w = new WaitCallback(ProcessImage);
                ThreadPool.QueueUserWorkItem(w, taskParams);

            }
            
        }
        
        private void ProcessImage(object state)
        {
            List<String> stack = state as List<String>;
            String filename = stack[0];
            String tempfile = stack[1];
            taskStartTime = DateTime.Now;
            Utilities.SetMatchThreshold(20);
            short stat = Utilities.DetectParasite(filename);
            taskStatus = stat;
        }

        private void mnuExit_Click(object sender, EventArgs e)
        {
            // Exit
            this.Close();
        }

        private void timer_Tick(object sender, EventArgs e)
        {
            // We don't really know how long it will take
            // so just emulate progress
            progressBar.Value = (progressBar.Value + 1) % progressBar.Maximum;

            // When image processed
            if (taskStatus > 0)
            {
                // Prepare for another decoding
                timer.Enabled = false;
                pnlLoading.Visible = false;
                progressBar.Value = 0;
                lblStart.Visible = true;
                imgImage.Image.Dispose();
                imgImage.Image = null;
                mnuImage.Enabled = true;
                mnuExit.Enabled = true;
                short stat = taskStatus;
                taskStatus = -1;

                String filename = taskParams[0];
                String tempfile = taskParams[1];
                taskParams.Clear();
                
                // Check that returned status is 0x2???
                if ((stat>0))
                {
                    String msg;
                    if (Utilities.GetMatches() > 0)
                    {
                      msg = "Plasmodium Positive " + Utilities.GetMatches() + " Parasites";
                    }
                    else
                    {
                        msg = "Plasmodium Negative " + " No Parasites"; 
                    }
                    if(File.Exists(tempfile)){
                        // Display modal form with decoded message and 
                        // status information.
                        new parsite(ParasiteStoreLocation,Utilities.GetMatches(), msg, DateTime.Now.Subtract(taskStartTime), stat).ShowDialog();
                    }else
                        stat = 0;
                }
                try
                {
                    File.Delete(tempfile); // delete temporary file
                    File.Delete(ParasiteStoreLocation); // delete temporary file
                }
                catch { }

            }
        }
    }
}