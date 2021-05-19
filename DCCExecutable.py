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

#pyinstaller DCCExecutable.py  --add-data anonlink-entity-service;anonlink-entity-service --add-data config.json;.


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
        self.enter_owner_names_text = None
        self.owner_names_input = None
        self.open_schema_text = None
        self.open_inbox_text = None
        self.open_output_text = None
        self.threshold_text = None
        self.threshold_input = None
        self.inbox_text = None
        self.port_text = None
        self.match_text = None
        self.InitUI()
        self.PingService(True)

    def InitUI(self):
        panel = wx.Panel(self)

        hbox = wx.BoxSizer()
        sizer = wx.GridSizer(8, 2, 10, 300)

        schema_btn = wx.Button(panel, label='Select Schema Folder')
        inbox_btn = wx.Button(panel, label='Select Inbox Folder')
        output_btn = wx.Button(panel, label='Select Output Folder')
        validate_btn = wx.Button(panel, label='Validate Inbox')
        start_service_btn = wx.Button(panel, label='Start Service')
        match_btn = wx.Button(panel, label='Match Records')

        self.enter_owner_names_text = wx.StaticText(panel, label="Enter Data Owner Names (comma seperated)")
        self.owner_names_input = wx.TextCtrl(panel, value=str(ownerNames).replace("[", "").replace("]", "").replace("'", ""))
        self.open_schema_text = wx.StaticText(panel, label=config['schema_folder'])
        self.open_inbox_text = wx.StaticText(panel, label=config['inbox_folder'])
        self.open_output_text = wx.StaticText(panel, label=config['output_folder'])
        self.threshold_text = wx.StaticText(panel, label="Enter matching threshold")
        self.threshold_input = wx.TextCtrl(panel, value=str(config["matching_threshold"]))
        self.inbox_text = wx.StaticText(panel, label="")
        self.port_text = wx.StaticText(panel, label="")
        self.match_text = wx.StaticText(panel, label="")

        sizer.AddMany([self.enter_owner_names_text, self.owner_names_input, self.open_schema_text, schema_btn, self.open_inbox_text, inbox_btn, self.open_output_text, output_btn, self.threshold_text, self.threshold_input, self.inbox_text, validate_btn, self.port_text, start_service_btn, self.match_text, match_btn])

        hbox.Add(sizer, 0, wx.ALL, 15)
        panel.SetSizer(hbox)

        schema_btn.Bind(wx.EVT_BUTTON, self.OnOpenSchema)
        inbox_btn.Bind(wx.EVT_BUTTON, self.OnOpenInbox)
        output_btn.Bind(wx.EVT_BUTTON, self.OnOpenOutput)
        validate_btn.Bind(wx.EVT_BUTTON, self.StartValidate)
        start_service_btn.Bind(wx.EVT_BUTTON, self.StartService)
        match_btn.Bind(wx.EVT_BUTTON, self.StartMatch)

        self.owner_names_input.Bind(wx.EVT_TEXT, self.UpdateOwners)
        self.threshold_input.Bind(wx.EVT_TEXT, self.UpdateThreshold)

        self.SetSize((850, 300))
        self.SetTitle('Messages')
        self.Centre()

    def PingService(self, init):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8851))
        if result == 0:
            self.port_text.SetLabel("Port is open")
            self.port_text.SetForegroundColour((0, 150, 0))
            sock.close()
            return True
        else:
            self.port_text.SetLabel("Port is not open")
            if init:
                self.port_text.SetForegroundColour((150, 0, 0))
            else:
                self.port_text.SetForegroundColour((150, 150, 0))
            sock.close()
            return False


    def StartService(self, event):
        subprocess.Popen("docker-compose -p anonlink -f anonlink-entity-service/tools/docker-compose.yml up")
        while not self.PingService(False):
            pass

    def StartValidate(self, event):
        msg = validate.validate()
        self.inbox_text.SetLabel(msg)
        if msg == "All necessary input is present":
            self.inbox_text.SetForegroundColour((0, 150, 0))
        else:
            self.inbox_text.SetForegroundColour((150, 0, 0))

    def StartMatch(self, event):
        self.match_text.SetLabel("Matching Entries...")
        self.match_text.SetForegroundColour((150, 150, 0))
        self.Update()
        time.sleep(5)
        match.match()
        linkids.linkids()
        dataownerids.data_owner_ids()
        self.match_text.SetLabel(f"Linkids written to {config['output_folder']}")
        self.match_text.SetForegroundColour((0, 150, 0))
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
        config['systems'] = [owner.strip(" ") for owner in self.owner_names_input.GetLineText(0).split(",")]
        self.UpdateJson()


    def UpdateThreshold(self, event):
        config['matching_threshold'] = float(self.threshold_input.GetLineText(0))
        self.UpdateJson()


    def OnOpenSchema(self, event):
        with wx.DirDialog(self, "Choose Schema Directory", style=wx.FD_OPEN | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.schemaDir = dirDialog.GetPath()
            self.open_schema_text.SetLabel(self.schemaDir)
            config['schema_folder'] = self.schemaDir
            self.UpdateJson()


    def OnOpenInbox(self, event):
        with wx.DirDialog(self, "Choose Inbox Directory", style=wx.FD_OPEN | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.inboxDir = dirDialog.GetPath()
            self.open_inbox_text.SetLabel(self.inboxDir)
            config['inbox_folder'] = self.inboxDir
            self.UpdateJson()

    def OnOpenOutput(self, event):
        with wx.DirDialog(self, "Choose Output Directory", style=wx.FD_OPEN | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.outputDir = dirDialog.GetPath()
            self.open_output_text.SetLabel(self.outputDir)
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

