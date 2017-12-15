import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
import ttk
import tkFileDialog as dlg
import tkMessageBox as msg
from collections import OrderedDict

import math
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from shutil import copyfile
from time import *

LARGE_FONT= ("Verdana", 15)
style.use("ggplot")

def main():
    '''Creates an instance of the RFQ application that runs the main TK inter
    function and creates all of the applications pages in its original frame.'''
    app = RFQ_Application()
    app.mainloop()

class RFQ_Application(tk.Tk):
    ''''''
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "RFQ Application")
        ico_file = "C:/Users/njanzen/Documents/RFQ Application/triumf_logo.ico"
        tk.Tk.iconbitmap(self, default=ico_file)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        self.LoadDeafaultFiles()
        self.AddMenu(container)
        self.frames = {}
        for page in (HomePage, Electrodes, RF_Settings, VacuumSystems):
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

        self.SetWindowSize(590,1080)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        # frame.canvas.draw_idle()

    def GraphWindow(self, Page):
        plot = Page(self)

    def OpenTopLevel(self, Page, options=range(5)):
        Popup = Page(self, options)

    def SetWindowSize(self, h, w):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def AddMenu(self, container):
        menubar = tk.Menu(container)

        filemenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save",
            command=lambda:self.OpenTopLevel(SavePage))
        filemenu.add_command(label="Load Setting",
            command=lambda:self.OpenTopLevel(LoadPage))
        filemenu.add_command(label="Reset Settings to Default",
            command=lambda:self.ResetVals())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)

        editmenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="Edit", menu=editmenu)
        editmenu.add_command(label="Electrode Settings",
            command=lambda:self.show_frame(Electrodes))
        editmenu.add_command(label="RF Settings",
            command=lambda:self.show_frame(RF_Settings))
        editmenu.add_command(label="Vacuum Controls",
            command=lambda:self.show_frame(VacuumSystems))
        editmenu.add_command(label="Buncher Options", command=Empty)
        editmenu.add_command(label="Change Default Files",
            command=lambda:self.OverWrite())

        graphmenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="Graphs", menu=graphmenu)
        graphmenu.add_command(label="Pressure Readouts",
            command=lambda:self.GraphWindow(PressurePlot))
        graphmenu.add_command(label="Temperature Readouts",
            command=lambda:self.GraphWindow(TemperaturePlot))
        graphmenu.add_command(label="Potential Readouts",
            command=lambda:self.GraphWindow(ElectrodePlots))
        graphmenu.add_command(label="RF Forward Power Readouts",
            command=lambda:self.GraphWindow(RF_Forward_Power_Plot))
        graphmenu.add_command(label="RF Reflected Power Readouts",
            command=lambda:self.GraphWindow(RF_Reflected_Power_Plot))
        graphmenu.add_command(label="RF Phase Readouts",
            command=lambda:self.GraphWindow(RF_Phase_Plot))

        tk.Tk.config(self, menu=menubar)

    def OverWrite(self):
        self.OpenTopLevel(OverwritePage)
        self.LoadDeafaultFiles(False)

    def LoadDeafaultFiles(self, UpdateCurrent=True):
        '''Load all deafault data files to the application. Creates golbal data
        arrays for both the default and the current settings.'''

        loc = "C:/Users/njanzen/Documents/RFQ Application/Default Files/"
        files = ("Trap", "Transfer", "Extraction", "RFSettings", "DeviceSettings","ElectrodeVoltages")
        de = "_Default.txt"

        self.DefaultAppData = OrderedDict()
        self.DefaultAppData["Trapping Electrodes"] = np.loadtxt(loc+files[0]+de, delimiter=',')
        self.DefaultAppData["Transfer Electrodes"] = np.loadtxt(loc+files[1]+de, delimiter=',')
        self.DefaultAppData["Extraction Electrodes"] = np.loadtxt(loc+files[2]+de, delimiter=',')
        self.DefaultAppData["RF Settings"] = np.loadtxt(loc+files[3]+de, delimiter=',')
        self.DefaultAppData["Device Settings"] = np.loadtxt(loc+files[4]+de, delimiter=',')
        self.DefaultAppData["Electrode Voltages"] = np.loadtxt(loc+files[5]+de, delimiter=',')
        if UpdateCurrent:
            self.AppData = OrderedDict()
            for key in self.DefaultAppData:
                self.AppData[key] = self.DefaultAppData[key]

    def ResetVals(self):
        if msg.askokcancel('',"Reset all values to default?"):
            self.AppData = OrderedDict()
            for key in self.DefaultAppData:
                self.AppData[key] = self.DefaultAppData[key]

            frame1 = self.frames[HomePage]
            frame1.get_settings(self)
            frame2 = self.frames[Electrodes]
            frame2.SetElecVals("Trapping Electrodes")

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        self.controller = controller
        self.get_settings(controller)
        self.AddLabels()
        self.AddPressure()
        self.AddTemperature()

    def AddLabels(self):
        ttk.Button(self, text='Apply', command=lambda:
            Empty).grid(row=7, column=0, pady=4)
        ttk.Button(self, text='Reset', command=lambda:
            Empty).grid(row=7, column=1, pady=4)
        ttk.Button(self, text='Browse', command=lambda:
            Empty).grid(row=8, column=1, pady=4)
        tk.Label(self,text="RFQ Outputs",font =("Verdana",16),
        padx = 40).grid(row=1, column=3, pady=4, columnspan=10)

    def AddPressure(self):
        self.PresFile = 'C:/Users/njanzen/Documents/RFQ Application/SampleData.txt'
        self.PressurePlot = PlotFrame(self,self.controller,
                                file_name=self.PresFile, toolbar=False)
        self.PressurePlot.grid(row=2,column=3,rowspan=3,columnspan=3,sticky='nsew')
        self.PressurePlot.a.set_title("Pressure")
        self.PressurePlot.a.set_xlim([0, 100])
        self.PressurePlot.a.set_ylim([0, 1])
        self.PressurePlot.line.set_color('blue')
        self.Pres_press = self.PressurePlot.canvas.mpl_connect('button_press_event',self.ViewPres)
        self.popup_Pres = tk.Menu(self.controller, tearoff=0)
        self.popup_Pres.add_command(label="View Graph",
            command=lambda:self.controller.GraphWindow(PressurePlot))

    def ViewPres(self, event):
        frame_pos_x = self.PressurePlot.winfo_rootx()
        frame_pos_y = self.PressurePlot.winfo_rooty()
        frame_height = self.PressurePlot.winfo_height()

        x_loc = int(frame_pos_x + event.x)
        y_loc = int(frame_pos_y + frame_height - event.y-35)
        if event.button == 3:
            self.popup_Pres.post(x_loc, y_loc)

    def AddTemperature(self):
        self.TempFile = 'C:/Users/njanzen/Documents/RFQ Application/SampleData2.txt'
        self.TemperaturePlot = PlotFrame(self,self.controller,
                                file_name=self.TempFile, toolbar=False)
        self.TemperaturePlot.grid(row=5,column=3,rowspan=3,columnspan=3,sticky='nsew')
        self.TemperaturePlot.a.set_title("Temperature")
        self.TemperaturePlot.a.set_xlim([0, 100])
        self.TemperaturePlot.a.set_ylim([-3, 3])
        self.TemperaturePlot.line.set_color('orange')
        self.Temp_press = self.TemperaturePlot.canvas.mpl_connect('button_press_event',self.ViewTemp)
        self.popup_Temp = tk.Menu(self.controller, tearoff=0)
        self.popup_Temp.add_command(label="View Graph",
        command=lambda:self.controller.GraphWindow(TemperaturePlot))

    def ViewTemp(self, event):
        frame_pos_x = self.TemperaturePlot.winfo_rootx()
        frame_pos_y = self.TemperaturePlot.winfo_rooty()
        frame_height = self.TemperaturePlot.winfo_height()
        x_loc = int(frame_pos_x + event.x)
        y_loc = int(frame_pos_y + frame_height - event.y-35)
        if event.button == 3:
            self.popup_Temp.post(x_loc, y_loc)

    def get_settings(self, controller):
        DeviceFields = ("Pressure (Bar)","Temperature (K)","Bunch Time (ms)",
            "RF Frequency (MHz)","RF Amplitude")
        InitSettings = np.array([1,1,1,1,1])
        self.ents = makeform(self,DeviceFields,InitSettings,2)

class Electrodes(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Electrode Settings", font=LARGE_FONT)
        label.grid(row=0, columnspan=5)
        self.controller = controller
        self.ElectrodeTypes = ["Trapping Electrodes",
            "Transfer Electrodes","Extraction Electrodes"]
        self.fields = ('E1', 'E2A', 'E2B', 'E2C','E2D','E3', 'E4A', 'E4B', 'E4C', 'E4D',
            'E5', 'Hyperboloid', 'Cone', 'Immersion', 'Ground', 'DragField')
        self.numents = len(self.fields)
        self.DrawPotential("Trapping Electrodes", controller.AppData)
        self.UpdateElectrodePage("Trapping Electrodes",controller.AppData)
        self.radio_button = tk.StringVar(self)
        DisplayLabel = tk.Label(self,text="Electrode Configuration",
                    padx = 40).grid(row=1, column=3, pady=4)
        i = 0
        for key in self.ElectrodeTypes:
            tk.Radiobutton(self,text=key,padx=5,
                command=lambda: self.UpdateElectrodePage(self.radio_button.get(), controller.AppData),
                variable=self.radio_button,
                value=key).grid(row=2, column=i+3, pady=4)
            i = i+1

        self.radio_button.set("Trapping Electrodes")

        button1 = ttk.Button(self, text='Edit Potentials',
            command=lambda:EditElectrode(controller, self))
        button1.grid(row=self.numents+1,column=0, pady=15)
        button4 = ttk.Button(self, text="Back to Home",
            command=lambda:controller.show_frame(HomePage))
        button4.grid(row=self.numents+1,column=1, columnspan=2)

        gif = "C:/Users/njanzen/Documents/RFQ Application/Electrodes.gif"
        image = tk.PhotoImage(file=gif, master=controller)
        label = tk.Label(self,image=image)
        label.image = image
        label.grid(column=3,columnspan=3,row=self.numents-2, rowspan=4)

    def DrawLabels(self, config, DataSource):
        is_on = DataSource[config]
        for i in range(self.numents):
            label1 = tk.Label(self,text=self.fields[i])
            label1.grid(row=1+i)
            label2 = tk.Label(self,text=DataSource["Electrode Voltages"][0,i],width=9)
            label2.grid(row=1+i,column=1)
            label3 = tk.Label(self,text=DataSource["Electrode Voltages"][1,i],width=9)
            label3.grid(row=1+i,column=2)
            if is_on[i]:
                label2.config(bg='pale violet red')
            else: label3.config(bg='pale violet red')

    def UpdateElectrodePage(self, config, DataSource):
        self.DrawLabels(config, DataSource)
        for i in range(3):
            if config == self.ElectrodeTypes[i]:
                confignum = i
        self.HighlightLine(confignum)

    def DrawPotential(self, config, DataSource):
        ElectrodeData = np.zeros([3,self.numents])
        for i in range(3):
            data = DataSource[self.ElectrodeTypes[i]]
            for j in range(self.numents):
                if data[j]:
                    ElectrodeData[i,j] = DataSource["Electrode Voltages"][0,j]
                else: ElectrodeData[i,j] = DataSource["Electrode Voltages"][1,j]

        TotPotential1 = self.ScalePotential(ElectrodeData[0,:])
        plot_data = [self.Location,TotPotential1[0:750]]
        self.plot_frame = PlotFrame(self,self.controller,data=plot_data,
            figsize=(8,3), add_label=False, ani_func=False)
        self.plot_frame.grid(row=3,column=3,rowspan=self.numents-5,columnspan=3)
        self.plot_frame.a.set_xlim([0,75])
        self.plot_frame.a.set_ylim([-25,30])
        self.plot_frame.line.set_alpha(0.25)

        TotPotential2 = self.ScalePotential(ElectrodeData[1,:])
        self.plot_frame.a2 = self.plot_frame.f.add_subplot(111)
        lin2, = self.plot_frame.a2.plot([], [], color="blue", alpha=0.25)
        self.plot_frame.line2 = lin2
        self.plot_frame.line2.set_xdata(self.Location)
        self.plot_frame.line2.set_ydata(TotPotential2[0:750])

        TotPotential3 = self.ScalePotential(ElectrodeData[2,:])
        self.plot_frame.a3 = self.plot_frame.f.add_subplot(111)
        lin3, = self.plot_frame.a3.plot([], [], color="blue", alpha=0.25)
        self.plot_frame.line3 = lin3
        self.plot_frame.line3.set_xdata(self.Location)
        self.plot_frame.line3.set_ydata(TotPotential3[0:750])

    def HighlightLine(self,confignum):
        self.plot_frame.line.set_alpha(0.25)
        self.plot_frame.line2.set_alpha(0.25)
        self.plot_frame.line3.set_alpha(0.25)
        if confignum == 0:
            self.plot_frame.line.set_alpha(1)
        elif confignum == 1:
            self.plot_frame.line2.set_alpha(1)
        else:
            self.plot_frame.line3.set_alpha(1)
        self.plot_frame.f.canvas.draw()

    def ScalePotential(self,ElectrodeData):
        # Opens a text file containing the default electrode settings then
        # runs a function to adjust any of the voltage settings
        DataFile = "C:/Users/njanzen/Documents/RFQ Application/VoltageScaling.txt"
        Data = np.loadtxt(DataFile, delimiter=',')
        Location = Data[:,0]
        self.Location = Location[0:750]
        VoltageScaling = Data[:,1::]

        # Based on the set electrode voltages, calculates the total potential on the Z
        # axis by scaling the VoltageScaling array
        PotentialArray = np.zeros(VoltageScaling.shape, dtype = float)
        for i in range(11):
            scaled = VoltageScaling[:,i*2:i*2+2] * ElectrodeData[i]
            PotentialArray[:,i*2:i*2+2] = scaled

        for i in range(5):
            scaled = VoltageScaling[:,i+22] * ElectrodeData[i+11]
            PotentialArray[:,i+22] = scaled

        TotPotential = map(sum, PotentialArray)
        return TotPotential

class RF_Settings(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        label1 = tk.Label(self,text='Resulting RF Settings',font=("verdana", 13))
        label1.grid(row=6,columnspan=2,column=0)
        label2 = tk.Label(self,text='RF Frequency (MHz)',font=("verdana", 12))
        label2.grid(row=7,column=0)
        self.label3 = tk.Label(self,text='',font=("verdana", 12))
        self.label3.grid(row=7,column=1)
        label4 = tk.Label(self,text='RF Amplitude (V)',font=("verdana", 12))
        label4.grid(row=8,column=0)
        self.label5 = tk.Label(self,text='',font=("verdana", 12))
        self.label5.grid(row=8,column=1)
        label6 = tk.Label(self,text='Stability Parameter: q',font=("verdana", 12))
        label6.grid(row=9,column=0)
        self.label7 = tk.Label(self,text='',font=("verdana", 12))
        self.label7.grid(row=9,column=1)

        tk.Frame(self,height=30).grid(row=11,column=0)
        ttk.Button(self,text='Optimize Settings',
            command=lambda:self.OptimizeWindow()).grid(row=10,column=0)
        ttk.Button(self,text='View Calculations',
            command=lambda:self.OptimizeWindow()).grid(row=10,column=1)
        ttk.Button(self, text='Apply RF Parameters',
            command=lambda:self.ApplySettings()).grid(row=12, column=0)
        ttk.Button(self, text="Back to Home",
            command=lambda:controller.show_frame(HomePage)).grid(row=15,column=1,pady=20)
        ttk.Button(self, text="Save Settings",
            command=lambda:controller.OpenTopLevel(SavePage, options=[3])).grid(row=13,column=1)
        ttk.Button(self, text="Reset",
            command=lambda:self.ResetVals()).grid(row=12,column=1)
        ttk.Button(self, text="Confirm",
            command=lambda:self.ConfirmSettings()).grid(row=13,column=0)

        self.UpdateVars(self.controller.AppData["RF Settings"], confirm=True)

        InitSettings = [self.Q, self.A, self.TD, self.q_desired]
        self.fields = ('Ion Charge (e)','Ion Mass (AU)', 'Pseudopotential TD (V)', 'Desired Stability: q')
        self.RF_Ents = makeform(self,self.fields,InitSettings,rowstart=2)

        tk.Label(self,text="RF Settings", font=("verdana", 16)).grid(row=0, column=0, columnspan=8, pady=4)
        self.radio_button = tk.IntVar(self)
        tk.Radiobutton(self,text="Forward Power",variable=self.radio_button,
            command=lambda:self.RF_Power(self.radio_button.get()),
            value=0).grid(row=1,column=2)
        tk.Radiobutton(self,text="Reflected Power",variable=self.radio_button,
            command=lambda:self.RF_Power(self.radio_button.get()),
            value=1).grid(row=1,column=3)
        self.radio_button.set(0)

        self.RF_Power(0)
        self.RF_PhaseShift()

    def ResetVals(self):
        self.UpdateVars(self.OldVars)
        Settings = [self.Q, self.A, self.TD, self.q_desired]
        self.RF_Ents = makeform(self,self.fields,Settings,rowstart=2)

    def ConfirmSettings(self):
        variables = fetch(self.RF_Ents)
        variables = variables + [0.005]
        self.UpdateVars(variables, confirm=True)

    def ApplySettings(self):
        variables = fetch(self.RF_Ents)
        variables = variables + [0.005]
        self.UpdateVars(variables)

    def UpdateVars(self, variables, confirm=False):
        self.Q = variables[0]
        self.e = self.Q*1.602E-19
        self.A = variables[1]
        self.m = self.A*1.66E-27
        self.TD = variables[2]
        self.q_desired = variables[3]
        self.r0 = variables[4]

        self.Calc()

        if confirm:
            self.OldVars = [self.Q,self.A,self.TD,self.q_desired,self.r0]

    def Calc(self):
        Freq = 6
        V_rf = math.sqrt((self.m * self.r0**2 * (2*math.pi*Freq*1E6)**2 * self.TD)/self.e)
        q = 4*self.TD/V_rf
        self.Freq_H = {"Freq":Freq,"V_rf":V_rf,"q":q}

        Freq = 6
        V_rf = math.sqrt((self.m * self.r0**2 * (2*math.pi*Freq*1E6)**2 * self.TD)/self.e)
        q = 4*self.TD/V_rf
        self.Freq_L = {"Freq":Freq,"V_rf":V_rf,"q":q}

        if self.Freq_H["q"] < self.Freq_L["q"]:
            self.RF_vals = self.Freq_H
        else:self.RF_vals = self.Freq_L

        self.label3['text'] = str(self.RF_vals["Freq"])
        self.label5['text'] = str(self.RF_vals["V_rf"])[0:6]
        self.label7['text'] = str(self.RF_vals["q"])[0:6]

    def RF_Power(self, plot):
        self.ForwardPowerFile = 'C:/Users/njanzen/Documents/RFQ Application/Forward_Power.txt'
        self.ReflectedPowerFile = 'C:/Users/njanzen/Documents/RFQ Application/Reflected_Power.txt'
        PowerFiles = [self.ForwardPowerFile,self.ReflectedPowerFile]
        self.RFPower_plot = PlotFrame(self,self.controller,
            file_name=PowerFiles[plot], toolbar=False)
        self.RFPower_plot.grid(row=2,column=2,rowspan=6,columnspan=3,sticky='nsew')
        self.RFPower_plot.a.set_title("RF Power")
        self.RFPower_plot.a.set_xlim([0, 100])
        self.RFPower_plot.a.set_ylim([-3, 3])
        self.RFPower_plot.line.set_color('magenta')
        self.Power_press = self.RFPower_plot.canvas.mpl_connect('button_press_event',self.ViewPower)
        self.popup_Power = tk.Menu(self.controller, tearoff=0)
        self.popup_Power.add_command(label="View Graph",
            command=lambda:self.PowerOption(self.radio_button.get()))

    def ViewPower(self, event):
        frame_pos_x = self.RFPower_plot.winfo_rootx()
        frame_pos_y = self.RFPower_plot.winfo_rooty()
        frame_height = self.RFPower_plot.winfo_height()
        x_loc = int(frame_pos_x + event.x)
        y_loc = int(frame_pos_y + frame_height - event.y-35)
        if event.button == 3:
            self.popup_Power.post(x_loc, y_loc)

    def PowerOption(self, option):
        Options = [RF_Forward_Power_Plot,RF_Reflected_Power_Plot]
        self.controller.GraphWindow(Options[option])

    def RF_PhaseShift(self):
        self.RFPhaseFile = 'C:/Users/njanzen/Documents/RFQ Application/RF_PhaseShift.txt'
        self.RFPhase_plot = PlotFrame(self,self.controller,
            file_name=self.RFPhaseFile, toolbar=False)
        self.RFPhase_plot.grid(row=8,column=2,rowspan=6,columnspan=3,sticky='nsew')
        self.RFPhase_plot.a.set_title("RF Phase Shift")
        self.RFPhase_plot.a.set_xlim([0, 100])
        self.RFPhase_plot.a.set_ylim([-3, 3])
        self.RFPhase_plot.line.set_color('orange')
        self.Phase_press = self.RFPhase_plot.canvas.mpl_connect('button_press_event',self.ViewPhase)
        self.popup_Phase = tk.Menu(self.controller, tearoff=0)
        self.popup_Phase.add_command(label="View Graph",
        command=lambda:self.controller.GraphWindow(RF_Phase_Plot))

    def ViewPhase(self, event):
        frame_pos_x = self.RFPhase_plot.winfo_rootx()
        frame_pos_y = self.RFPhase_plot.winfo_rooty()
        frame_height = self.RFPhase_plot.winfo_height()
        x_loc = int(frame_pos_x + event.x)
        y_loc = int(frame_pos_y + frame_height - event.y-35)
        if event.button == 3:
            self.popup_Power.post(x_loc, y_loc)

    def OptimizeWindow(self):
        Window = tk.Toplevel(self)
        ttk.Button(Window,text='Close',command=lambda:Window.destroy()).pack()
        Window.grab_set()

class VacuumSystems(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        tk.Label(self,text="Vacuum Pumps").grid(row=0)
        var1 = tk.IntVar()
        tk.Checkbutton(self, text="Roughing Pump", variable=var1).grid(row=1, sticky=tk.W)
        var2 = tk.IntVar()
        tk.Checkbutton(self, text="Turbo Pump 1", variable=var2).grid(row=2, sticky=tk.W)
        var3 = tk.IntVar()
        tk.Checkbutton(self, text="Turbo Pump 2", variable=var3).grid(row=3, sticky=tk.W)
        var4 = tk.IntVar()
        tk.Checkbutton(self, text="Turbo Pump 3", variable=var4).grid(row=4, sticky=tk.W)
        var5 = tk.IntVar()
        tk.Checkbutton(self, text="Turbo Pump 4", variable=var5).grid(row=5, sticky=tk.W)
        var6 = tk.IntVar()
        tk.Checkbutton(self, text="Turbo Pump 5", variable=var6).grid(row=6, sticky=tk.W)

        tk.Frame(self,height=20).grid(row=7)

        tk.Label(self,text="Gas Inlets").grid(row=8)
        var10 = tk.IntVar()
        tk.Checkbutton(self, text="Inlet 1", variable=var10).grid(row=9, sticky=tk.W)
        var11 = tk.IntVar()
        tk.Checkbutton(self, text="Inlet 2", variable=var11).grid(row=10, sticky=tk.W)
        var12 = tk.IntVar()
        tk.Checkbutton(self, text="Inlet 3", variable=var12).grid(row=11, sticky=tk.W)
        var13 = tk.IntVar()
        tk.Checkbutton(self, text="Inlet 4", variable=var13).grid(row=12, sticky=tk.W)
        var14 = tk.IntVar()
        tk.Checkbutton(self, text="Inlet 5", variable=var14).grid(row=13, sticky=tk.W)

        ttk.Button(self,text="Apply",command=lambda:Empty()).grid(row=14)
        ttk.Button(self,text="Back to Home",
            command=lambda:controller.show_frame(HomePage)).grid(row=17,column=0)
        gif = "C:/Users/njanzen/Documents/RFQ Application/RFQ Crossection.gif"
        image = tk.PhotoImage(file=gif, master=controller)
        label = tk.Label(self,image=image)
        label.image = image
        label.grid(column=1,row=1, rowspan=20)

class PlotFrame(tk.Frame):
    def __init__(self, parent, controller, data=None, file_name=None, ani_func=True,
        toolbar=True, add_label=True, figsize=(7,2)):
        tk.Frame.__init__(self, parent)

        self.f = Figure(figsize=figsize)
        self.a = self.f.add_subplot(111)

        potentialcanvas = FigureCanvasTkAgg(self.f, self)
        potentialcanvas.show()
        potentialcanvas.get_tk_widget().pack()
        self.canvas = potentialcanvas
        if toolbar:
            plot_toolbar = NavigationToolbar2TkAgg(self.canvas,self)
            plot_toolbar.update()
            self.canvas._tkcanvas.pack()

        lin, = self.a.plot([], [], color="blue")
        self.line = lin

        if ani_func:
            try:
                self.animate(File=file_name)
                self.ani = animation.FuncAnimation(self.f, self.animate,
                fargs=(file_name,add_label), interval=1000)
            except: pass
        else:
            self.line.set_xdata(data[0])
            self.line.set_ydata(data[1])

    def animate(self, i=None, File='', add_label=True):
        Data = np.loadtxt(File, delimiter=',')
        self.line.set_xdata(Data[:,0])
        self.line.set_ydata(Data[:,1])
        Val = str(Data[-1,1])
        text=Val[0:6]
        if add_label:
            try:self.label.destroy()
            except:pass
            self.label = tk.Label(self,text=text,font=("verdana",18))
            self.label.pack()

class EditElectrode(tk.Toplevel):
    def __init__(self, controller, parent, *args):
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.parent = parent

        label = tk.Label(self, text="Adjusting Voltages", font=LARGE_FONT)
        label.grid(row=0, columnspan=5)
        self.ElectrodeTypes = ["Trapping Electrodes",
            "Transfer Electrodes","Extraction Electrodes"]
        self.fields = ('E1', 'E2A', 'E2B', 'E2C','E2D','E3', 'E4A', 'E4B', 'E4C', 'E4D',
            'E5', 'Hyperboloid', 'Cone', 'Immersion', 'Ground', 'DragField')
        self.numents = len(self.fields)

        self.AllElectrodeData = {}
        self.CreateElectrodeEntries()

        button1 = ttk.Button(self, text='Veiw Potential',
            command=lambda:self.UpdateGraph())
        button1.grid(row=self.numents+3,column=0)
        button2 = ttk.Button(self, text="Reset",
            command=lambda:self.ResetData())
        button2.grid(row=self.numents+3,column=1)
        button3 = ttk.Button(self, text='Confirm Electrode Config',
            command=lambda:self.ConfirmConfig())
        button3.grid(row=self.numents+4,column=0)
        button4 = ttk.Button(self, text="Save Electrode Config",
            command=lambda:controller.OpenTopLevel(SavePage, options=range(3)+[5]))
        button4.grid(row=self.numents+4,column=1)
        button5 = ttk.Button(self, text="Back to Home",
            command=lambda:controller.show_frame(HomePage))
        button5.grid(row=self.numents+5,column=1)

    def ConfirmConfig(self):
        self.Fetch_Data()
        for key in self.ElectrodeTypes:
            self.controller.AppData[key] = self.AllElectrodeData[key]
        self.controller.AppData["Electrode Voltages"] = self.AllElectrodeData["Electrode Voltages"]
        for key in self.AllElectrodeData:
            self.PrevElectrodeData[key] = self.AllElectrodeData[key]
        self.UpdateGraph()

    def UpdateGraph(self):
        self.Fetch_Data()
        self.parent.DrawPotential(self.parent.radio_button.get(),self.AllElectrodeData)
        self.parent.UpdateElectrodePage(self.parent.radio_button.get(),self.AllElectrodeData)

    def ResetData(self):
        self.CreateElectrodeEntries(init=False)
        self.UpdateGraph()

    def Fetch_Data(self):
        i = 0
        for TrapType in [self.trap_labels, self.trans_labels, self.extract_labels]:
            Data = np.zeros(self.numents)
            for Electrode in range(self.numents):
                label = TrapType[Electrode]
                if label.cget("text") == "ON":
                    Data[Electrode] = 1
                else:
                    Data[Electrode] = 0
            self.AllElectrodeData[self.ElectrodeTypes[i]] = Data
            i = i+1

        nums1 = []
        nums2 = []
        for entry in self.entries:
            field = entry[0]
            num1 = entry[1].get()
            num2 = entry[2].get()
            nums1.append(num1)
            nums2.append(num2)
        self.AllElectrodeData["Electrode Voltages"] = np.array([map(float,nums1), map(float,nums2)])

    def CreateElectrodeEntries(self, init=True):
        tk.Label(self,text="Electrode").grid(row=1,column=0)
        tk.Label(self,text="ON Voltage").grid(row=1,column=1)
        tk.Label(self,text="OFF Voltage").grid(row=1,column=2)
        tk.Label(self,text="Trap\nStates").grid(row=1,column=3)
        tk.Label(self,text="Transfer\nStates").grid(row=1,column=4)
        tk.Label(self,text="Extract\nStates").grid(row=1,column=5)

        if init:
            VoltageValues = self.controller.AppData["Electrode Voltages"]
            trap_state = self.controller.AppData["Trapping Electrodes"]
            trans_state = self.controller.AppData["Transfer Electrodes"]
            extract_state = self.controller.AppData["Extraction Electrodes"]
        else:
            VoltageValues = self.PrevElectrodeData["Electrode Voltages"]
            trap_state = self.PrevElectrodeData["Trapping Electrodes"]
            trans_state = self.PrevElectrodeData["Transfer Electrodes"]
            extract_state = self.PrevElectrodeData["Extraction Electrodes"]

        self.entries = []
        self.trap_labels = []
        self.trans_labels = []
        self.extract_labels = []
        for i in range(self.numents):
            label1 = tk.Label(self,text=self.fields[i])
            label1.grid(row=2+i)
            entryON = tk.Entry(self)
            entryON.insert(0,str(VoltageValues[0,i]))
            entryON.grid(row=2+i,column=1)
            entryOFF = tk.Entry(self)
            entryOFF.insert(0,str(VoltageValues[1,i]))
            entryOFF.grid(row=2+i,column=2)

            label2 = ON_OFF_Label(self)
            label2.grid(row=2+i,column=3,padx=2)
            self.trap_labels.append(label2)
            if trap_state[i]:
                label2.configure(text='ON',bg='lawn green')
            else:
                label2.configure(text='OFF',bg ='firebrick1')
            label3 = ON_OFF_Label(self)
            label3.grid(row=2+i,column=4,padx=2)
            self.trans_labels.append(label3)
            if trans_state[i]:
                label3.configure(text='ON',bg='lawn green')
            else:
                label3.configure(text='OFF',bg ='firebrick1')
            label4 = ON_OFF_Label(self)
            label4.grid(row=2+i,column=5,padx=2)
            self.extract_labels.append(label4)
            if extract_state[i]:
                label4.configure(text='ON',bg='lawn green')
            else:
                label4.configure(text='OFF',bg ='firebrick1')
            self.entries.append((self.fields[i], entryON, entryOFF))

        self.Fetch_Data()
        if init:
            self.PrevElectrodeData = {}
            for key in self.AllElectrodeData:
                self.PrevElectrodeData[key] = self.AllElectrodeData[key]

class PressurePlot(tk.Toplevel):
    def __init__(self, controller, *args):
        tk.Toplevel.__init__(self)
        self.PresFile = 'C:/Users/njanzen/Documents/RFQ Application/SampleData.txt'
        self.PressurePlot = PlotFrame(self,controller,file_name=self.PresFile,
                                figsize=(8,6),toolbar=True)
        self.PressurePlot.pack()
        self.PressurePlot.a.set_title("Pressure")
        self.PressurePlot.a.set_xlim([0, 100])
        self.PressurePlot.a.set_ylim([0, 1])
        self.PressurePlot.line.set_color('blue')

class TemperaturePlot(tk.Toplevel):
    def __init__(self, controller, *args):
        tk.Toplevel.__init__(self)
        self.TempFile = 'C:/Users/njanzen/Documents/RFQ Application/SampleData2.txt'
        self.TemperaturePlot = PlotFrame(self,controller,file_name=self.TempFile,
                                figsize=(8,6),toolbar=True)
        self.TemperaturePlot.pack()
        self.TemperaturePlot.a.set_title("Temperature")
        self.TemperaturePlot.a.set_xlim([0, 100])
        self.TemperaturePlot.a.set_ylim([-3, 3])
        self.TemperaturePlot.line.set_color('blue')

class ElectrodePlots(tk.Toplevel):
    def __init__(self, controller, *args):
        tk.Toplevel.__init__(self)
        self.TempFile = 'C:/Users/njanzen/Documents/RFQ Application/SampleData2.txt'
        self.TemperaturePlot = PlotFrame(self,controller,file_name=self.TempFile,
                                figsize=(8,6),toolbar=True)
        self.TemperaturePlot.pack()
        self.TemperaturePlot.a.set_title("Z Axis Potential")
        self.TemperaturePlot.a.set_xlim([0, 100])
        self.TemperaturePlot.a.set_ylim([-3, 3])
        self.TemperaturePlot.line.set_color('blue')

class RF_Forward_Power_Plot(tk.Toplevel):
    def __init__(self, controller, *args):
        tk.Toplevel.__init__(self)
        self.Forward_Power_File = 'C:/Users/njanzen/Documents/RFQ Application/Forward_Power.txt'
        self.ForwardPlot = PlotFrame(self,controller,file_name=self.Forward_Power_File,
                                figsize=(8,6),toolbar=True)
        self.ForwardPlot.pack()
        self.ForwardPlot.a.set_title("Forward Power")
        self.ForwardPlot.a.set_xlim([0, 100])
        self.ForwardPlot.a.set_ylim([-3, 3])
        self.ForwardPlot.line.set_color('blue')

class RF_Reflected_Power_Plot(tk.Toplevel):
    def __init__(self, controller, *args):
        tk.Toplevel.__init__(self)
        self.Reflected_Power_File = 'C:/Users/njanzen/Documents/RFQ Application/Reflected_Power.txt'
        self.Reflected = PlotFrame(self,controller,file_name=self.Reflected_Power_File,
                                figsize=(8,6),toolbar=True)
        self.Reflected.pack()
        self.Reflected.a.set_title("Reflected Power")
        self.Reflected.a.set_xlim([0, 100])
        self.Reflected.a.set_ylim([-3, 3])
        self.Reflected.line.set_color('blue')

class RF_Phase_Plot(tk.Toplevel):
    def __init__(self, controller, *args):
        tk.Toplevel.__init__(self)
        self.PhaseFile = 'C:/Users/njanzen/Documents/RFQ Application/RF_PhaseShift.txt'
        self.PhasePlot = PlotFrame(self,controller,file_name=self.PhaseFile,
                                figsize=(8,6),toolbar=True)
        self.PhasePlot.pack()
        self.PhasePlot.a.set_title("RF Phase Shift")
        self.PhasePlot.a.set_xlim([0, 100])
        self.PhasePlot.a.set_ylim([-3, 3])
        self.PhasePlot.line.set_color('blue')

class OverwritePage(tk.Toplevel):
    def __init__(self, controller, options=range(5), *args):
        tk.Toplevel.__init__(self)
        self.title = 'Overwrite Default Files'

        self.AppKeys = controller.AppData.keys()
        self.saveoptions = ['']*len(options)
        self.savedata = [None]*len(options)
        j = 0
        for i in options:
            self.saveoptions[j] = self.AppKeys[i]
            self.savedata[j] = controller.AppData[self.AppKeys[i]]
            j = j+1

        variable = tk.StringVar(self)
        variable.set(self.saveoptions[0])
        drop_down = apply(tk.OptionMenu, (self, variable) +
            tuple(self.saveoptions))
        drop_down.grid(row=0,column=0)
        drop_down.config(width=20)
        Label = tk.Label(self, text = "File Name").grid(row=1, column=0)
        var = tk.StringVar(self)
        var.set("")
        file_name = tk.Entry(self, textvariable=var).grid(row=1, column=1)

        file_button = ttk.Button(self, text='Browse',
            command = lambda: SetFile(var)).grid(row=1, column=3)

        apply_button = ttk.Button(self, text='Apply',
            command = lambda: self.OverwriteDefault(controller,
            var.get(),variable.get())).grid(row=2, column=3)
        self.grab_set()

    def OverwriteDefault(self, controller, source, savetype):
        # Maybe insert a password here for final application
        dest_dir = 'C:/Users/njanzen/Documents/RFQ Application/'
        # Should fix this to account for AppData changes
        default_names = ["Trap_Default.txt","Transfer_Default.txt",
            "Extraction_Default.txt","RFSettings_Default.txt","DeviceSettings_Default.txt"]

        i = 0
        for key in controller.AppData:
            if  savetype == key:
                default_file_name = default_names[i]
            i = i+1
        destination = dest_dir + 'Default Files/' + default_file_name
        NewData = np.loadtxt(source, delimiter=',')
        OldData = np.loadtxt(destination, delimiter=',')
        if len(NewData) == len(OldData):
            if source == destination:
                msg.showerror('Already Default',
                'This File is already the default.')
            else:
                if msg.askokcancel('Warning',"Are you sure you wish to update\nthe deafult files for this application?"):
                    copyfile(source, destination)
                    self.grab_release()
                    self.destroy()
        else: msg.showerror('Illegal File',
        'The save file does not meet the dimension\nrequirements for the default file.')

class SavePage(tk.Toplevel):
    def __init__(self, controller, options=range(5), *args):
        tk.Toplevel.__init__(self)
        self.title = 'Save'

        self.AppKeys = controller.AppData.keys()
        self.saveoptions = ['']*len(options)
        self.savedata = [None]*len(options)
        j = 0
        for option in options:
            self.saveoptions[j] = self.AppKeys[option]
            self.savedata[j] = controller.AppData[self.AppKeys[option]]
            j = j+1

        variable = tk.StringVar(self)
        variable.set(self.saveoptions[0])
        drop_down = apply(tk.OptionMenu, (self, variable) +
            tuple(self.saveoptions))
        drop_down.grid(row=0,column=0)
        drop_down.config(width=20)

        Label1 = tk.Label(self, text = "File Name").grid(row=1, column=0)
        self.var1 = tk.StringVar(self)
        self.var1.set("")
        file_name = tk.Entry(self, textvariable=self.var1).grid(row=1, column=1)

        Label2 = tk.Label(self, text = "Directory").grid(row=2, column=0)
        self.var2 = tk.StringVar(self)
        self.var2.set("")
        dir_name = tk.Entry(self, textvariable=self.var2).grid(row=2, column=1)

        file_button = ttk.Button(self, text='Browse',
            command = lambda: SetDir(self.var2)).grid(row=3, column=0)

        save_button = ttk.Button(self, text='Okay',
            command = lambda: self.ApplySave(controller, variable.get(),
            self.var2.get(),self.var1.get())).grid(row=3, column=1)

        self.grab_set()

    def ApplySave(self, controller, savetype, save_dir, save_name):

        if save_name[-4:] == ".txt":
            full_name = save_dir+'/'+save_name
        else:
            full_name = save_dir+'/'+save_name+".txt"
        np.savetxt(full_name, controller.AppData[savetype], delimiter=',', fmt='%1.4e')

        self.grab_release()
        self.destroy()

class LoadPage(tk.Toplevel):
    def __init__(self, controller, options=range(5), *args):
        tk.Toplevel.__init__(self)
        self.title = 'Load'

        self.AppKeys = controller.AppData.keys()
        self.saveoptions = ['']*len(options)
        self.savedata = [None]*len(options)
        j = 0
        for i in options:
            self.saveoptions[j] = self.AppKeys[i]
            self.savedata[j] = controller.AppData[self.AppKeys[i]]
            j = j+1

        variable = tk.StringVar(self)
        variable.set(self.saveoptions[0])
        drop_down = apply(tk.OptionMenu, (self, variable) +
            tuple(self.saveoptions))
        drop_down.grid(row=0,column=0)
        drop_down.config(width=20)

        Label = tk.Label(self, text = "File Name").grid(row=1, column=0)
        var = tk.StringVar(self)
        var.set("")
        file_name = tk.Entry(self, textvariable=var).grid(row=1, column=1)

        file_button = ttk.Button(self, text='Browse',
            command = lambda: SetFile(var)).grid(row=1, column=3)

        apply_button = ttk.Button(self, text='Load',
            command = lambda: self.Load(controller, var.get(),variable.get())).grid(row=2, column=3)
        self.grab_set()

    def Load(self, controller, source, loadtype):
        NewData = np.loadtxt(source, delimiter=',')
        if len(NewData) == len(controller.AppData[loadtype]):
            controller.AppData[loadtype] = NewData
            self.grab_release()
            self.destroy()
        else: msg.showerror("Illegal File",
            "The load file does not meet the dimension requirements")

class ON_OFF_Label(tk.Label):
    def __init__(self, controller, *args, **kwargs):
        tk.Label.__init__(self, controller, *args, **kwargs)
        self.bind("<Button-1>", lambda e:self.flip_ON_OFF())
        self.configure(width=8)
    def flip_ON_OFF(self):
        if self.cget("text") == "ON":
            self.configure(text='OFF',bg ='firebrick1')
        else:
            self.configure(text='ON',bg='lawn green')

def Empty():
    msg.showerror("No Function", "Sorry, button in developement.")

# A function to fetch the data related to any entries in an entry widget
def fetch(entries):
    # entries is an array of lists with length 2 which the entry text and a
    # cooresponding entry instance to get the entry value
    # printdata is a boolean that decides if each entry text and value will be
    # displayed in python
    nums = []
    for entry in entries:
        field = entry[0]
        num = entry[1].get()
        nums.append(num)
    # Assumes the entry value string is a number and converts it to a float
    return map(float,nums)

# A function to create the Tkinger entry forms
def makeform(root, fields, initData, rowstart=0, colstart=0):
    # fields is a list of strings for each entry field
    # initData is an array of the initial values for each entry
    entries = []
    i = 0
    for field in fields:
        lab = tk.Label(root, text=field, anchor='w')
        ent = tk.Entry(root)
        # Adds the initial value to each entr
        ent.insert(0, str(initData[i]))
        lab.grid(row=rowstart+i,column=colstart)
        ent.grid(row=rowstart+i,column=colstart+1)
        entries.append((field, ent))
        i += 1
    return entries

def SetDir(var):
    directory = dlg.askdirectory()
    if directory:
        var.set(directory)

def SetFile(var):
    filename = dlg.askopenfilename()
    if filename:
        var.set(filename)

if __name__ =='__main__':
    main()
