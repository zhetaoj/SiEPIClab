<img src="https://github.com/SiEPIC/SiEPIClab/blob/master/SiEPIClab_Color.png" width="300">
# SiEPIClab, formerly pyOptomip
Copyright (c) 2015 originally started by Michael Caverley, at The University of British Columbia.

Python code for <a href="https://siepic.ubc.ca/silicon-photonics-design-book/automated-probe-station/">Silicon Photonics Automated Probe stations
	
To build you own probe station, view instructions [here](https://github.com/SiEPIC/pyOptomip/blob/d737b29963befef6f050b565618b35107469369b/Documentation/Assembly%20Instructions.pdf)
  
## Installation Instructions:

1. Download Anaconda 64 bit Python 3.9 - **wxpython currently does not work on anything above 3.10**:

    Download from: http://continuum.io/downloads
	
2. In a command prompt, run 
	```
	python -m pip install -U wxPython
	pip install pyvisa=="1.11.3"
	pip install comtypes=="1.1.11"
	pip install scipy=="1.9.0"
	pip install matplotlib=="3.4.3"
	pip install numpy=="1.20.3"
	pip install keithley2600
	pip install thorlabs_apt_device
	pip install opencv-python=="4.4.0.46"
	```
	
	**Make sure the correct versions are downloaded and the previous versions have been uninstalled**
	
3. Install NI max, including all suggested driver downloads on initial install. After install, open NI Package Manager and download NIvisa and NI 488.2:
	
	Download from: https://www.ni.com/en-ca/support/downloads/drivers/download.system-configuration.html#371210
	
4. Install Keysight 816x Instrument driver version 4.6.3 (has support for 64-bit):
	
	Download from: https://www.keysight.com/ca/en/lib/software-detail/driver/816x-vxi-plugplay-driver-112417.html

5. Install APT 64-bit software:

	Download from: https://www.thorlabs.com/software_pages/viewsoftwarepage.cfm?code=Motion_Control
        
## Instructions for Running the GUI Software:

**Option 1**: To run from within Spyder, add the pyOptomip folder to the PYTHONPATH. Then, run the pyOptomip.pyw script.

**Option 2**: To run as a standalone application, set the file association so that pyOptomip.pyw opens with pythonw.exe (found in C:\Anaconda). This
is the preferred way of running the program.

**Option 3**: Another way to run as a standalone application is to create a batch file with the following contents:
	
	
	@echo off
	"path to python.exe""path to pyOptomip.pyw"
	
---
	
[PyOptomip User's Guide](https://github.com/SiEPIC/pyOptomip/blob/72af126364ec208976772012d3e816e65cc302cc/Documentation/PyOptomip%20User's%20Guide.pdf)

[TroubleShooting Guide](https://github.com/SiEPIC/pyOptomip/blob/d737b29963befef6f050b565618b35107469369b/Documentation/Troubleshooting%20Guide.pdf)

[Instrument Information and Manuals](https://github.com/SiEPIC/pyOptomip/blob/63262baa5816f8d54ecf7973b19f55c323bdb13e/Documentation/Instrument%20Information.pdf)

---

### Known Issues:

When using hp816x_N77Det, if there are any detectors plugged into the 8163 or 8164 mainframe, the detectors listed on the Instrument Control 
window will not correspond to the labels on the detectors. This can cause unexpected sweep measurement results. The workaround is to unplug 
all detectors from the mainframe when using the N77xx detectors.

When not using the N77xx detector, if there is a detector plugged into the mainframe which stores less than 20001 datapoints (e.g. 81634A),
then stitching will not work.
=======


