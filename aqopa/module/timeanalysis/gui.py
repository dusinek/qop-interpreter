'''
Created on 06-09-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import wx
from aqopa.model import name_indexes
import re

class OneVersionPanel(wx.Panel):
    """ 
    Frame presenting results for one simulation.  
    Simulator may be retrived from module, 
    because each module has its own simulator.
    """
    
    def __init__(self, module, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.module = module
        self.versionSimulator = {}

        self.hostChoosePanels       = []  # Panels used to choose hosts for times results
        self.checkBoxInformations   = []  # Tuples with host name, and index ranges widget
        self.hostCheckBoxes         = []  # List of checkboxes with hosts names used for hosts' selection

        self.timeResultsPanel       = None

        #################
        # VERSION BOX
        #################
        
        versionBox = wx.StaticBox(self, label="Version")
        self.versionsList = wx.ComboBox(self, style=wx.TE_READONLY)
        self.versionsList.Bind(wx.EVT_COMBOBOX, self.OnVersionChanged)
        
        versionBoxSizer = wx.StaticBoxSizer(versionBox, wx.VERTICAL)
        versionBoxSizer.Add(self.versionsList, 1, wx.ALL | wx.ALIGN_CENTER, 5)

        #################
        # TOTAL TIME BOX
        #################
        
        self.totalTimeBox = wx.StaticBox(self, label="Total time")
        self.totalTimeLabel = wx.StaticText(self, label="---")
        
        totalTimeBoxSizer = wx.StaticBoxSizer(self.totalTimeBox, wx.VERTICAL)
        totalTimeBoxSizer.Add(self.totalTimeLabel, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        
        #################
        # TIMES BOX
        #################
        
        self.timesBox = wx.StaticBox(self, label="Times")

        operationBox, operationBoxSizer = self._BuildOperationsBoxAndSizer()
        hostsBox, hostsBoxSizer = self._BuildHostsBoxAndSizer()

        timesBoxSizer = wx.StaticBoxSizer(self.timesBox, wx.VERTICAL)
        
        timesHBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        timesHBoxSizer.Add(operationBoxSizer, 0, wx.ALL | wx.EXPAND)
        timesHBoxSizer.Add(hostsBoxSizer, 1, wx.ALL | wx.EXPAND)
        
        self.showTimeBtn = wx.Button(self, label="Show time")
        self.showTimeBtn.Bind(wx.EVT_BUTTON, self.OnShowTimeButtonClicked)
        
        self.timesResultBox = wx.StaticBox(self, label="Results")
        self.timesResultBoxSizer = wx.StaticBoxSizer(self.timesResultBox, wx.VERTICAL)
        
        timesBoxSizer.Add(timesHBoxSizer, 0, wx.ALL | wx.EXPAND)
        timesBoxSizer.Add(self.showTimeBtn, 0, wx.ALL | wx.EXPAND)
        timesBoxSizer.Add(self.timesResultBoxSizer, 1, wx.ALL | wx.EXPAND)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(versionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(totalTimeBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(timesBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.SetVersionsResultsVisibility(False)
        
    #################
    # REACTIONS
    #################
        
    def AddFinishedSimulation(self, simulator):
        """ """
        version = simulator.context.version
        self.versionsList.Append(version.name)
        
        self.versionSimulator[version.name] = simulator
        
    def OnVersionChanged(self, event):
        """ """
        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        
        totalTime = self.GetTotalTime(simulator)
        self.totalTimeLabel.SetLabel("%.2f ms" % totalTime)
        
        self._BuildHostsChoosePanel(simulator)
        
        self.SetVersionsResultsVisibility(True)
        
    def OnShowTimeButtonClicked(self, event):
        """ """
        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        hosts = self._GetSelectedHosts(simulator)
        if self.oneTimeRB.GetValue():
            self.ShowHostsTimes(simulator, hosts)
        elif self.avgTimeRB.GetValue():
            self.ShowAverageHostsTime(simulator, hosts)
        elif self.minTimeRB.GetValue():
            self.ShowMinimalHostsTime(simulator, hosts)
        elif self.maxTimeRB.GetValue():
            self.ShowMaximalHostsTime(simulator, hosts)
        
    #################
    # LAYOUT
    #################
    
    def _BuildOperationsBoxAndSizer(self):
        """ """
        self.operationBox = wx.StaticBox(self, label="Operation")
        
        self.oneTimeRB = wx.RadioButton(self, label="One host's time")
        self.avgTimeRB = wx.RadioButton(self, label="Average hosts' time")
        self.minTimeRB = wx.RadioButton(self, label="Minimal hosts' time")
        self.maxTimeRB = wx.RadioButton(self, label="Maximal hosts' time")
        
        operationBoxSizer = wx.StaticBoxSizer(self.operationBox, wx.VERTICAL)
        operationBoxSizer.Add(self.oneTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.avgTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.minTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.maxTimeRB, 0, wx.ALL)
        
        return self.operationBox, operationBoxSizer
    
    def _BuildHostsBoxAndSizer(self):
        """ """
        self.hostsBox = wx.StaticBox(self, label="Host(s)")
        self.hostsBoxSizer = wx.StaticBoxSizer(self.hostsBox, wx.VERTICAL)
        return self.hostsBox, self.hostsBoxSizer
    
    def _BuildHostsChoosePanel(self, simulator):
        """ """
        for p in self.hostChoosePanels:
            p.Destroy()
        self.hostChoosePanels = []
        self.checkBoxInformations = {}
        self.hostCheckBoxes = []
        
        self.hostsBoxSizer.Layout()
        
        hosts = simulator.context.hosts
        hostsIndexes = {} 
        for h in hosts:
            name = h.original_name()
            indexes = name_indexes(h.name)
            index = indexes[0]
            
            if name not in hostsIndexes or index > hostsIndexes[name]:
                hostsIndexes[name] = index
                
        for hostName in hostsIndexes:
            
            panel = wx.Panel(self)
            panelSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            ch = wx.CheckBox(panel, label=hostName, size=(120, 20))
            textCtrl = wx.TextCtrl(panel)
            textCtrl.SetValue("0")
            
            rangeLabel = "Available range: 0"
            if hostsIndexes[hostName] > 0:
                rangeLabel += " - %d" % hostsIndexes[hostName] 
            maxLbl = wx.StaticText(panel, label=rangeLabel)
            
            panelSizer.Add(ch, 0, wx.ALL | wx.ALIGN_CENTER)
            panelSizer.Add(textCtrl, 0, wx.ALL | wx.ALIGN_CENTER)
            panelSizer.Add(maxLbl, 0, wx.ALL | wx.ALIGN_CENTER)
            panel.SetSizer(panelSizer)
            self.hostsBoxSizer.Add(panel, 1, wx.ALL)
            
            self.checkBoxInformations[ch] = (hostName, textCtrl)
            self.hostChoosePanels.append(panel)
            self.hostCheckBoxes.append(ch)
            
        self.hostsBoxSizer.Layout()
        self.Layout()

    def SetVersionsResultsVisibility(self, visible):
        """ """
        widgets = []
        widgets.append(self.timesBox)
        widgets.append(self.totalTimeBox)
        widgets.append(self.totalTimeLabel)
        widgets.append(self.operationBox)
        widgets.append(self.oneTimeRB)
        widgets.append(self.avgTimeRB)
        widgets.append(self.minTimeRB)
        widgets.append(self.maxTimeRB)
        widgets.append(self.hostsBox)
        widgets.append(self.showTimeBtn)
        widgets.append(self.timesResultBox)
        
        for w in widgets:
            if visible:
                w.Show()
            else:
                w.Hide()
                
        self.Layout()
    
    #################
    # STATISTICS
    #################
        
    def _GetSelectedHosts(self, simulator):
        """ Returns list of hosts selected by user """
        
        def ValidateHostsRange(indexesRange):
            """ """
            return re.match(r'\d(-\d)?(,\d(-\d)?)*', indexesRange)
        
        def GetIndexesFromRange(indexesRange):
            """ Extracts numbers list of hosts from range text """
            indexes = []
            ranges = indexesRange.split(',')
            for r in ranges:
                parts = r.split('-')
                if len(parts) == 1:
                    indexes.append(int(parts[0]))
                else:
                    for i in range(int(parts[0]), int(parts[1])+1):
                        indexes.append(i)
            return indexes
        
        hosts = []
        for ch in self.hostCheckBoxes:
            if not ch.IsChecked():
                continue
            hostName, hostRangeTextCtrl = self.checkBoxInformations[ch]
            indexesRange = hostRangeTextCtrl.GetValue()
            if not ValidateHostsRange(indexesRange):
                wx.MessageBox("Range '%s' for host '%s' is invalid. Valid example: 0,12,20-25,30." 
                              % (indexesRange, hostName), 'Error', wx.OK | wx.ICON_ERROR)
                break
            else:
                indexes = GetIndexesFromRange(indexesRange)
                for h in simulator.context.hosts:
                    hostIndexes = name_indexes(h.name)
                    if h.original_name() == hostName and hostIndexes[0] in indexes:
                        hosts.append(h)
        return hosts
        
    def GetTotalTime(self, simulator):
        """ Return total time of simulated version. """
        totalTime = 0
        hosts = simulator.context.hosts
        for h in hosts:
            t = self.module.get_current_time(simulator, h)
            if t > totalTime:
                totalTime = t
        return totalTime 
    
    def ShowHostsTimes(self, simulator, hosts):
        """ """
        if self.timeResultsPanel:
            self.timeResultsPanel.Destroy()
            self.timeResultsPanel = None
            
        self.timeResultsPanel = wx.Panel(self)
        self.timesResultBoxSizer.Add(self.timeResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        if len(hosts) == 0:
            lbl = wx.StaticText(self.timeResultsPanel, label="No hosts selected")
            sizer.Add(lbl)     
        else:
            for h in hosts:
                
                lblText = "%s: %.2f ms" % (h.name,self.module.get_current_time(simulator, h))
                
                error = h.get_finish_error()
                if error is not None:
                    lblText += " (Not Finished - %s)" % error
                
                lbl = wx.StaticText(self.timeResultsPanel, label=lblText)
                sizer.Add(lbl)
        
        self.timeResultsPanel.SetSizer(sizer)
        self.Layout()
    
    def ShowAverageHostsTime(self, simulator, hosts):
        """ """
        def GetVal(simulator, hosts):
            sum = 0.0
            n = len(hosts)
            for h in hosts:
                sum += self.module.get_current_time(simulator, h)
            return sum / float(n)
        
        if self.timeResultsPanel:
            self.timeResultsPanel.Destroy()
            
        self.timeResultsPanel = wx.Panel(self)
        self.timesResultBoxSizer.Add(self.timeResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        lblText = ""
        if len(hosts) == 0:
            lblText = "---"
        else:
            avg = GetVal(simulator, hosts)
            lblText = "Average: %.2f ms" % avg
        lbl = wx.StaticText(self.timeResultsPanel, label=lblText)        
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.timeResultsPanel.SetSizer(sizer)
        self.Layout()
        
    def ShowMinimalHostsTime(self, simulator, hosts):
        """ """
        def GetVal(simulator, hosts):
            val = None 
            for h in hosts:
                t = self.module.get_current_time(simulator, h)
                if val is None or t < val:
                    val = t
            return val
        
        if self.timeResultsPanel:
            self.timeResultsPanel.Destroy()
            
        self.timeResultsPanel = wx.Panel(self)
        self.timesResultBoxSizer.Add(self.timeResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        lblText = ""
        if len(hosts) == 0:
            lblText = "---"
        else:
            val = GetVal(simulator, hosts)
            lblText = "Minimum: %.2f ms" % val
        lbl = wx.StaticText(self.timeResultsPanel, label=lblText)        
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.timeResultsPanel.SetSizer(sizer)
        self.Layout()
    
    def ShowMaximalHostsTime(self, simulator, hosts):
        """ """
        def GetVal(simulator, hosts):
            val = 0.0 
            for h in hosts:
                t = self.module.get_current_time(simulator, h)
                if t > val:
                    val = t
            return val
        
        if self.timeResultsPanel:
            self.timeResultsPanel.Destroy()
            
        self.timeResultsPanel = wx.Panel(self)
        self.timesResultBoxSizer.Add(self.timeResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        lblText = ""
        if len(hosts) == 0:
            lblText = "---"
        else:
            val = GetVal(simulator, hosts)
            lblText = "Maximum: %.2f ms" % val
        lbl = wx.StaticText(self.timeResultsPanel, label=lblText)     
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.timeResultsPanel.SetSizer(sizer)
        self.Layout()
        
class MainResultsNotebook(wx.Notebook):
    """ """
    def __init__(self, module, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)
        
        self.module = module
        
        self.oneVersionTab = OneVersionPanel(self.module, self)
        self.oneVersionTab.Layout()
        self.AddPage(self.oneVersionTab, "Version Results")
        
        self.compareTab = wx.Panel(self)
        self.compareTab.Layout()
        self.AddPage(self.compareTab, "Compare Versions")
        
    def OnSimulationFinished(self, simulator):
        """ """
        self.oneVersionTab.AddFinishedSimulation(simulator)
        
    def OnAllSimulationsFinished(self, simulators):
        """ """
        pass
        
class ModuleGui(object):
    """
    Class used by GUI version of AQoPA.
    """
    
    def __init__(self, module):
        """ """
        self.module = module
        self.mainResultNotebook = None
        
    def get_name(self):
        return "Time Analysis"
    
    def get_configuration_panel(self, parent):
        """ Returns WX panel with configuration controls. """
        
        panel = wx.Panel(parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(panel, label="Module does not need to be configured.") 
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        text = wx.StaticText(panel, label="All result options will be available after results are calculated.") 
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        
        panel.SetSizer(sizer)
        return panel
    
    def get_results_panel(self, parent):
        """
        Create main result panel existing from the beginning 
        which will be extended when versions' simulations are finished.
        """
        self.mainResultNotebook = MainResultsNotebook(self.module, parent)
        return self.mainResultNotebook
    
    def on_finished_simulation(self, simulator):
        """ """
        self.mainResultNotebook.OnSimulationFinished(simulator)
    
    def on_finished_all_simulations(self, simulators):
        """ 
        Called once for all simulations after all of them are finished.
        """
        self.mainResultNotebook.OnAllSimulationsFinished(simulators)
        

        
        
        
        