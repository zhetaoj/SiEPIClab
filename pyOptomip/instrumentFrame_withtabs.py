# The MIT License (MIT)

# Copyright (c) 2015 Michael Caverley

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import wx
from outputlogPanel import outputlogPanel
import sys
from fineAlign import fineAlign
from fineAlignPanel import fineAlignPanel
import traceback
from logWriter import logWriter, logWriterError
from autoMeasurePanel import autoMeasurePanel
from autoMeasure import autoMeasure
import laserPanel
from laserPanel import detectorPanel
from laserPanel import tlsPanel
from hp816x_N77Det_instr import hp816x_N77Det
import myMatplotlibPanel
from matplotlib import pyplot as plt
import pyvisa as visa
from TestParameters import testParameters
from TestParameters import TopPanel
import cv
import cv2
import numpy as np
from PIL import Image
import multiprocessing
import threading
import time

homebox = wx.BoxSizer(wx.HORIZONTAL)


class BackgroundTasks(threading.Thread):
    def run(self, *args, **kwargs):
        cap = cv2.VideoCapture(0)
        a = 0
        b = 0
        while cap.isOpened():
            ret, frame = cap.read()

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            h, s, v = cv2.split(hsv)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                if a <= 254:
                    a = a + 1
                print(a)

            if cv2.waitKey(1) & 0xFF == ord('w'):
                if a > 0:
                    a = a - 1
                print(a)

            if cv2.waitKey(1) & 0xFF == ord('e'):
                b = b - 1
                cap.set(cv2.CAP_PROP_EXPOSURE, b)
                print(b)

            if cv2.waitKey(1) & 0xFF == ord('r'):
                b = b + 1
                cap.set(cv2.CAP_PROP_EXPOSURE, b)
                print(b)

            #hsv[:, 2, :] = s  # Changes the V value

            s = s + a

            #print(s)

            hsv = cv2.merge([h,s,v])

            frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # show Image
            cv2.imshow('Webcam', frame)

            #im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #x = im_rgb.shape

            #bitmap1 = wx.Bitmap.FromBuffer(x[1], x[0], im_rgb)
            #bitmap = wx.StaticBitmap(HomeTab, bitmap=bitmap1)
            #homebox.Add(bitmap, flag=wx.EXPAND, border=0, proportion=1)

            # checks whether q has been hit and stops the loop
            if cv2.waitKey(1) & 0xFF == ord('f'):
                break

# Define the tab content as classes:
class HomeTab(wx.Panel):
    def __init__(self, parent, instList):
        """

        Args:
            parent:
            instList:
        """
        wx.Panel.__init__(self, parent)
        self.instList = instList
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        homeVbox = wx.BoxSizer(wx.VERTICAL)

        #p1 = multiprocessing.Process(target=self.test)
        #p1 = multiprocessing.Process(target=self.camerarunning(self.hbox))
        #p1.start()

        #x = threading.Thread(target=BackgroundTasks, args=(self.hbox,), daemon=True)
        #x.start()

        t = BackgroundTasks()
        t.start()


        #self.graph = myMatplotlibPanel.myMatplotlibPanel(self)  # use for regular mymatplotlib file
        #hbox.Add(self.graph, flag=wx.EXPAND, border=0, proportion=1)
        #self.hbox.Add(self.bitmap, flag=wx.EXPAND, border=0, proportion=1)

        for inst in self.instList:
            # if inst.isSMU:
            # panel = inst.panelClass(self)
            # else:
            if inst.isDetect:
                panel = inst.panelClass(self, inst, True, False)
            elif inst.isLaser:
                panel = inst.panelClass(self, inst, True, True)
            else:
                panel = inst.panelClass(self, inst)

            # homeVbox = wx.BoxSizer(wx.VERTICAL)
            if inst.isMotor and not inst.isElec:
                homeVbox.Add(panel, proportion=0, border=0, flag=wx.EXPAND)

            if (inst.isMotor and not inst.isElec) and self.laserFound():
                self.fineAlign = fineAlign(self.getLasers()[0], self.getMotors()[0])
                try:
                    self.fineAlignPanel = fineAlignPanel(self, self.fineAlign)
                except Exception as e:
                    dial = wx.MessageDialog(None, 'Could not initiate instrument control. ' + traceback.format_exc(),
                                            'Error', wx.ICON_ERROR)
                    dial.ShowModal()
                homeVbox.Add(self.fineAlignPanel, proportion=0, flag=wx.EXPAND)
                # if self.motorFound():
                #   hbox.Add(homeVbox)
            if inst.isDetect:
                homeVbox.Add(panel, proportion=0, border=0, flag=wx.EXPAND)
                # self.detectorPanel = detectorPanel(panel, inst.getNumPWMChannels(), inst)
                # detectVbox.Add(self.detectorPanel, proportion=0, border=0, flag=wx.EXPAND)
                # hbox.Add(homeVbox, flag=wx.EXPAND)
            if inst.isElec:
                homeVbox.Add(panel, proportion=0, border=0, flag=wx.EXPAND)
            # self.laser = hp816x_N77Det()
            #  detectVbox = wx.BoxSizer(wx.VERTICAL)
            #  detPanel = detectorPanel(tlsPanel, self.laser.getNumPWMChannels(), self.laser)
            #  detectVbox.Add(detPanel, proportion=0, border=0, flag=wx.EXPAND)
            #  hbox.Add(detectVbox)
            # else:
            #   hbox.Add(panel, proportion=1, border=0, flag=wx.EXPAND)
        self.hbox.Add(homeVbox)
        vbox.Add(self.hbox, 3, wx.EXPAND)
        # self.log = outputlogPanel(self)
        # vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)
        self.Layout()
        self.Show()

    def test(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()

            # show Image
            cv2.imshow('Webcam', frame)

            # checks whether q has been hit and stops the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    def camerarunning(self, hbox):

        # connect to capture device
        cap = cv2.VideoCapture(1)

        while cap.isOpened():
            ret, frame = cap.read()

            # show Image
            cv2.imshow('Webcam', frame)
            #im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #x = im_rgb.shape

            ##self.bitmap1 = wx.Bitmap.FromBuffer(x[1], x[0], im_rgb)
            #self.bitmap = wx.StaticBitmap(self, bitmap=self.bitmap1)
            #hbox.Add(self.bitmap, flag=wx.EXPAND, border=0, proportion=1)
            #print('Hello')

            # checks whether q has been hit and stops the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        #cap.release()
        #cv2.destroyAllWindows()

    def motorFound(self):
        """

        Returns:

        """
        motorFound = False
        for inst in self.instList:
            motorFound = motorFound | inst.isMotor
        return motorFound

    def laserFound(self):
        """

        Returns:

        """
        laserFound = False
        for inst in self.instList:
            laserFound = laserFound | inst.isLaser
        return laserFound

    def getLasers(self):
        """

        Returns:

        """
        laserList = []
        for inst in self.instList:
            if inst.isLaser:
                laserList.append(inst)
        return laserList

    def getMotors(self):
        """

        Returns:

        """
        motorList = []
        for inst in self.instList:
            if inst.isMotor:
                motorList.append(inst)
        return motorList

    def OnExitApp(self, event):
        """

        Args:
            event:
        """
        for inst in self.instList:
            inst.disconnect()
        self.Destroy()


class ElectricalTab(wx.Panel):
    def __init__(self, parent, instList):
        """

        Args:
            parent:
            instList:
        """
        wx.Panel.__init__(self, parent)
        self.instList = instList
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        for inst in self.instList:
            # if inst.isSMU:
            # panel = inst.panelClass(self, str(self.para1tc.GetValue()))
            # else:

            if inst.isDetect:
                panel = inst.panelClass(self, inst, True, True)
            elif inst.isLaser:
                panel = inst.panelClass(self, inst, True, True)
            else:
                panel = inst.panelClass(self, inst)

            if inst.isSMU:
                hbox.Add(panel, proportion=1, border=0, flag=wx.EXPAND)
            # else:
            #  hbox.Add(panel, proportion=1, border=0, flag=wx.EXPAND)

        vbox.Add(hbox, 3, wx.EXPAND)
        # self.log = outputlogPanel(self)
        # vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)
        self.Layout()
        self.Show()

    def motorFound(self):
        """

        Returns:

        """
        motorFound = False
        for inst in self.instList:
            motorFound = motorFound | inst.isMotor
        return motorFound

    def laserFound(self):
        """

        Returns:

        """
        laserFound = False
        for inst in self.instList:
            laserFound = laserFound | inst.isLaser
        return laserFound

    def getLasers(self):
        """

        Returns:

        """
        laserList = []
        for inst in self.instList:
            if inst.isLaser:
                laserList.append(inst)
        return laserList

    def getMotors(self):
        """

        Returns:

        """
        motorList = []
        for inst in self.instList:
            if inst.isMotor:
                motorList.append(inst)
        return motorList

    def OnExitApp(self, event):
        """

        Args:
            event:
        """
        for inst in self.instList:
            inst.disconnect()
        self.Destroy()


class OpticalTab(wx.Panel):
    def __init__(self, parent, instList):
        """

        Args:
            parent:
            instList:
        """
        wx.Panel.__init__(self, parent)
        self.instList = instList
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.instList = instList

        for inst in instList:
            if inst.isLaser:
                panel = inst.panelClass(self, inst, False, True)
            else:
                panel = inst.panelClass(self, inst)

            if inst.isLaser:
                laserVbox = wx.BoxSizer(wx.VERTICAL)
                laserVbox.Add(panel, proportion=0, border=0, flag=wx.EXPAND)
                hbox.Add(laserVbox)
            # else:
            #   hbox.Add(panel, proportion=1, border=0, flag=wx.EXPAND)

        vbox.Add(hbox, 3, wx.EXPAND)
        # self.log = outputlogPanel(self)
        # vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)
        self.Layout()
        self.Show()

    def motorFound(self):
        """

        Returns:

        """
        motorFound = False
        for inst in self.instList:
            motorFound = motorFound | inst.isMotor
        return motorFound

    def laserFound(self):
        """

        Returns:

        """
        laserFound = False
        for inst in self.instList:
            laserFound = laserFound | inst.isLaser
        return laserFound

    def getLasers(self):
        """

        Returns:

        """
        laserList = []
        for inst in self.instList:
            if inst.isLaser:
                laserList.append(inst)
        return laserList

    def getMotors(self):
        """

        Returns:

        """
        motorList = []
        for inst in self.instList:
            if inst.isMotor:
                motorList.append(inst)
        return motorList

    def OnExitApp(self, event):
        """

        Args:
            event:
        """
        for inst in self.instList:
            inst.disconnect()
        self.Destroy()


class AutoMeasureTab(wx.Panel):
    def __init__(self, parent, instList):
        """

        Args:
            parent:
            instList:
        """
        wx.Panel.__init__(self, parent)
        self.instList = instList
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.fineAlign = fineAlign(self.getLasers(), self.getMotorsOpt())
        try:
            self.fineAlignPanel = fineAlignPanel(self, self.fineAlign)
        except Exception as e:
            dial = wx.MessageDialog(None, 'Could not initiate instrument control. ' + traceback.format_exc(),
                                    'Error', wx.ICON_ERROR)
            dial.ShowModal()

        self.autoMeasure = autoMeasure(self.getLasers(), self.getMotorsOpt(), self.getMotorsElec(), self.getSMUs(),
                                       self.fineAlign)

        self.autoMeasurePanel = autoMeasurePanel(self, self.autoMeasure)

        vbox.Add(self.autoMeasurePanel, proportion=0, flag=wx.EXPAND)

        vbox.Add(hbox, 3, wx.EXPAND)
        # self.log = outputlogPanel(self)
        # vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)

        # sys.stdout = logWriter(self.log)
        # sys.stderr = logWriterError(self.log)

    def motorFound(self):
        """

        Returns:

        """
        motorFound = False
        for inst in self.instList:
            motorFound = motorFound | inst.isMotor
        return motorFound

    def laserFound(self):
        """

        Returns:

        """
        laserFound = False
        for inst in self.instList:
            laserFound = laserFound | inst.isLaser
        return laserFound

    def getLasers(self):
        """

        Returns:

        """
        laserList = []
        for inst in self.instList:
            if inst.isLaser:
                laserList.append(inst)
        return laserList

    def getMotorsOpt(self):
        """

        Returns:

        """
        motorList = []
        for inst in self.instList:
            if inst.isMotor and inst.isOpt:
                motorList.append(inst)
        if not motorList:
            return [0]
        else:
            return motorList[0]

    def getMotorsElec(self):
        """

        Returns:

        """
        motorList = []
        for inst in self.instList:
            if inst.isMotor and inst.isElec:
                motorList.append(inst)
        if not motorList:
            return [0]
        else:
            return motorList[0]

    def getSMUs(self):
        """

        Returns:

        """
        SMUList = []
        for inst in self.instList:
            if inst.isSMU:
                SMUList.append(inst)
        return SMUList

    def OnExitApp(self, event):
        """

        Args:
            event:
        """
        for inst in self.instList:
            inst.disconnect()
        self.Destroy()


class TestingparametersTab(wx.Panel):
    def __init__(self, parent, instList):
        """

        Args:
            parent:
            instList:
        """
        wx.Panel.__init__(self, parent)
        self.instList = instList
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.testingParameters = TopPanel(self)

        vbox.Add(self.testingParameters, proportion=0, flag=wx.EXPAND)

        vbox.Add(hbox, 3, wx.EXPAND)
        # self.log = outputlogPanel(self)
        # vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)

        # sys.stdout = logWriter(self.log)
        # sys.stderr = logWriterError(self.log)

    def motorFound(self):
        """

        Returns:

        """
        motorFound = False
        for inst in self.instList:
            motorFound = motorFound | inst.isMotor
        return motorFound

    def laserFound(self):
        """

        Returns:

        """
        laserFound = False
        for inst in self.instList:
            laserFound = laserFound | inst.isLaser
        return laserFound

    def getLasers(self):
        """

        Returns:

        """
        laserList = []
        for inst in self.instList:
            if inst.isLaser:
                laserList.append(inst)
        return laserList

    def getMotors(self):
        """

        Returns:

        """
        motorList = []
        for inst in self.instList:
            if inst.isMotor:
                motorList.append(inst)
        return motorList

    def OnExitApp(self, event):
        """

        Args:
            event:
        """
        for inst in self.instList:
            inst.disconnect()
        self.Destroy()


class instrumentFrame_withtabs(wx.Frame):

    def __init__(self, parent, instList):
        """

        Args:
            parent:
            instList:
        """
        displaySize = wx.DisplaySize()
        super(instrumentFrame_withtabs, self).__init__(parent, title='Instrument Control',
                                                       size=(displaySize[0] * 5 / 8.0, displaySize[1] * 3 / 4.0))

        self.instList = instList
        try:
            self.InitUI()
        except Exception as e:
            for inst in instList:
                inst.disconnect()
            self.Destroy()
            raise
        self.Centre()
        self.Show()

    def InitUI(self):
        """

        """
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)

        # c = wx.Panel(self)
        self.p = wx.Panel(self)
        nb = wx.Notebook(self.p)

        # Create the tab windows
        tab1 = HomeTab(nb, self.instList)
        tab2 = ElectricalTab(nb, self.instList)
        tab3 = OpticalTab(nb, self.instList)
        tab4 = AutoMeasureTab(nb, self.instList)
        tab5 = TestingparametersTab(nb, self.instList)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "Home")
        nb.AddPage(tab2, "Electrical")
        nb.AddPage(tab3, "Optical")
        nb.AddPage(tab4, "Automated Measurements")
        nb.AddPage(tab5, "Testing Parameters")

        outputlabel = wx.StaticBox(self, label='SMU Control')

        output = wx.StaticBoxSizer(outputlabel, wx.VERTICAL)

        print(self.instList)

        # Set notebook in a sizer to create the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 1, wx.ALL | wx.EXPAND)

        self.log = outputlogPanel(self.p)
        sizer.Add(self.log, 0, wx.ALL | wx.EXPAND)
        self.p.SetSizer(sizer)
        sys.stdout = logWriter(self.log)
        sys.stderr = logWriterError(self.log)

    def OnExitApp(self, event):
        """

        Args:
            event:
        """
        for inst in self.instList:
            inst.disconnect()
        self.Destroy()
