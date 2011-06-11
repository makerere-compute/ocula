/***
 * @author Mistaguy
 * 
 * ***/
using System;
using System.Linq;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;

namespace ocula
{
    sealed class Utilities
    {
        
       
        /**
         * Imports C++ DLL functions
         */
        #region DLL Imports
       
        //directshow functions
        [DllImport("CameraCaptureDLL.DLL")]
        private static extern bool CaptureVideo();

        [DllImport("CameraCaptureDLL.DLL")]
        private static extern bool StopVideo();

        [DllImport("CameraCaptureDLL.DLL")]
        private static extern bool CaptureStill(string Path);

        [DllImport("CameraCaptureDLL.DLL")]
        private static extern bool InitializeGraph(IntPtr hWnd);
        //Opencv Diagnosis functions
        [DllImport("DLL.DLL")]
        private static extern short detectParasite(byte[] in_file);

        [DllImport("DLL.DLL")]
        private static extern void setMatchThreshold(int t);

        [DllImport("DLL.DLL")]
        private static extern int getMatchThreshold();

        [DllImport("DLL.DLL")]
        private static extern int getMatches();

        [DllImport("DLL.DLL")]
        private static extern int getFeatures();

        [DllImport("DLL", EntryPoint="disposeDLL")]
        private static extern void _DisposeDLL();
        #endregion

        /**
         * Some wrapper methods to simplify the usability of
         * the DLL Imports
         */
        #region DLL Wrapper Methods

        public static short DetectParasite(string in_file)
        {
            return detectParasite(StringToASCIIByteArray(in_file));
        }


        public static void SetMatchThreshold(int t)
        {
            setMatchThreshold(t);
        }


        public static int GetMatchThreshold()
        {
            return getMatchThreshold();
        }


        public static int GetMatches()
        {
            return getMatches();
        }


        public static int GetFeatures()
        {
            return getFeatures();
        }

        #endregion

        /**
         * Useful functions for marshaling and the like
         */
        #region Useful Functions
        public static byte[] StringToASCIIByteArray(string str)
        {
            return Encoding.ASCII.GetBytes(str + "\0");
        }

        public static string StringFromASCIIPtr(IntPtr str)
        {
            List<byte> bytes = new List<byte>();
            byte b = 0;
            int c = 0;
            do
            {
                b = Marshal.ReadByte(str, c);
                bytes.Add(b);
                c++;
            } while (b != 0);
            return Encoding.ASCII.GetString(bytes.ToArray(), 0, bytes.Count);
        }
        #endregion
    }
}
