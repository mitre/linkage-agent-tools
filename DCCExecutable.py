import validate, match, linkids, dataownerids
import json
import wx
from multiprocessing import freeze_support
from importlib import resources
import os
import socket
import subprocess
import atexit
import time
import sys

#pyinstaller DCCExecutable.py  --add-data anonlink-entity-service;anonlink-entity-service --add-data config.json;config.json


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
print(os.getcwd())
atexit.register(subprocess.run, "docker-compose -p anonlink -f anonlink-entity-service/tools/docker-compose.yml down")
atexit.register(os.remove, "results.json")
try:
    os.remove("results.json")
except:
    pass

with open("config.json") as f:
    config = json.load(f)
    ownerNames = config['systems']

class CSVManager(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(CSVManager, self).__init__(*args, **kwargs)
        self.schemaDir = ""
        self.inboxDir = ""
        self.outputDir = ""
        self.saltPath = ""
        self.txt1 = None
        self.txt2 = None
        self.txt3 = None
        self.txt4 = None
        self.txt5 = None
        self.txt6 = None
        self.txt7 = None
        self.txt8 = None
        self.txt9 = None
        self.txt10 = None
        self.InitUI()
        self.PingService(True)

    def InitUI(self):
        panel = wx.Panel(self)

        hbox = wx.BoxSizer()
        sizer = wx.GridSizer(8, 2, 10, 300)

        btn1 = wx.Button(panel, label='Select Schema Folder')
        btn2 = wx.Button(panel, label='Select Inbox Folder')
        btn3 = wx.Button(panel, label='Select Output Folder')
        btn4 = wx.Button(panel, label='Validate Inbox')
        btn5 = wx.Button(panel, label='Start Service')
        btn6 = wx.Button(panel, label='Match Records')

        self.txt1 = wx.StaticText(panel, label="Enter Data Owner Names (comma seperated)")
        self.txt2 = wx.TextCtrl(panel, value=str(ownerNames).replace("[", "").replace("]", "").replace("'", ""))
        self.txt3 = wx.StaticText(panel, label=config['schema_folder'])
        self.txt4 = wx.StaticText(panel, label=config['inbox_folder'])
        self.txt5 = wx.StaticText(panel, label=config['output_folder'])
        self.txt6 = wx.StaticText(panel, label="Enter matching threshold")
        self.txt7 = wx.TextCtrl(panel, value=str(config["matching_threshold"]))
        self.txt8 = wx.StaticText(panel, label="")
        self.txt9 = wx.StaticText(panel, label="")
        self.txt10 = wx.StaticText(panel, label="Make Sure Docker is Running!")

        sizer.AddMany([self.txt1, self.txt2, self.txt3, btn1, self.txt4, btn2, self.txt5, btn3, self.txt6, self.txt7, self.txt8, btn4, self.txt9, btn5, self.txt10, btn6])

        hbox.Add(sizer, 0, wx.ALL, 15)
        panel.SetSizer(hbox)

        btn1.Bind(wx.EVT_BUTTON, self.OnOpenSchema)
        btn2.Bind(wx.EVT_BUTTON, self.OnOpenInbox)
        btn3.Bind(wx.EVT_BUTTON, self.OnOpenOutput)
        btn4.Bind(wx.EVT_BUTTON, self.StartValidate)
        btn5.Bind(wx.EVT_BUTTON, self.StartService)
        btn6.Bind(wx.EVT_BUTTON, self.StartMatch)

        self.txt2.Bind(wx.EVT_TEXT, self.UpdateOwners)
        self.txt7.Bind(wx.EVT_TEXT, self.UpdateThreshold)

        self.SetSize((850, 300))
        self.SetTitle('Messages')
        self.Centre()

    def PingService(self, init):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8851))
        if result == 0:
            self.txt9.SetLabel("Port is open")
            self.txt9.SetForegroundColour((0, 150, 0))
            sock.close()
            return True
        else:
            self.txt9.SetLabel("Port is not open")
            if init:
                self.txt9.SetForegroundColour((150, 0, 0))
            else:
                self.txt9.SetForegroundColour((150, 150, 0))
            sock.close()
            return False


    def StartService(self, event):
        subprocess.Popen("docker-compose -p anonlink -f anonlink-entity-service/tools/docker-compose.yml up")
        while not self.PingService(False):
            pass

    def StartValidate(self, event):
        msg = validate.validate()
        self.txt8.SetLabel(msg)
        if msg == "All necessary input is present":
            self.txt8.SetForegroundColour((0, 150, 0))
        else:
            self.txt8.SetForegroundColour((150, 0, 0))

    def StartMatch(self, event):
        self.txt10.SetLabel("Matching Entries...")
        self.txt10.SetForegroundColour((150, 150, 0))
        self.Update()
        time.sleep(5)
        match.match()
        linkids.linkids()
        dataownerids.data_owner_ids()
        self.txt10.SetLabel(f"Linkids written to {config['output_folder']}")
        self.txt10.SetForegroundColour((0, 150, 0))
        self.Update()
        try:
            os.remove("results.json")
        except:
            pass

    def UpdateJson(self):
        global config
        with open("config.json", "w") as f:
            json.dump(config, f)
        with open("config.json") as f:
            config = json.load(f)
            ownerNames = [owner + ", " for owner in config['systems']]

    def UpdateOwners(self, event):
        config['systems'] = [owner.strip(" ") for owner in self.txt2.GetLineText(0).split(",")]
        self.UpdateJson()


    def UpdateThreshold(self, event):
        config['matching_threshold'] = float(self.txt7.GetLineText(0))
        self.UpdateJson()


    def OnOpenSchema(self, event):
        with wx.DirDialog(self, "Choose Schema Directory", style=wx.FD_OPEN | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.schemaDir = dirDialog.GetPath()
            self.txt3.SetLabel(self.schemaDir)
            config['schema_folder'] = self.schemaDir
            self.UpdateJson()


    def OnOpenInbox(self, event):
        with wx.DirDialog(self, "Choose Inbox Directory", style=wx.FD_OPEN | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.inboxDir = dirDialog.GetPath()
            self.txt4.SetLabel(self.inboxDir)
            config['inbox_folder'] = self.inboxDir
            self.UpdateJson()

    def OnOpenOutput(self, event):
        with wx.DirDialog(self, "Choose Output Directory", style=wx.FD_OPEN | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.outputDir = dirDialog.GetPath()
            self.txt5.SetLabel(self.outputDir)
            config['output_folder'] = self.outputDir
            config['matching_results_folder'] = self.outputDir
            self.UpdateJson()




def main():
    app = wx.App()
    ex = CSVManager(None)
    ex.Show()
    app.MainLoop()



if __name__ == '__main__':
    freeze_support()
    main()

