'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''


'''~~~~~~~~~~~~~~~~~~~~~~~~~   RFQ Application   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

'''
by Noah Janzen
Fall 2017
V 1.0

This application is meant for use with the CANREB RFQ cooler and buncher. It uses
tkinter to create several pages and live updating graphs to help adjust settings
and view outputs of the RFQ device. The main idea is that there should be a couple
of defualt files that load basic settings into the application that can be adjusted
within the app windows. These settings are all located in the app directory >>
Default Files. They are required for the app to initialize. There are also several
'Sample Files' that are loaded which have random data in order to test the graphical
displays.The end goal is to connect the data and settings of this app directly with
the RFQ to read and writesettings directly to the device. This application will
need some extra work once the RFQ is online in order to connect it to the app.
The settings should automatically update the RFQ and the 'Sample Files' should
instead be real output files that live update as the data is produced on the RFQ.
'''

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

# Imports all relevant modules
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
    '''A class using the tkinter main framework. This class houses all of the
    different windows used by the aplliction. It also initializes the main app
    variables and functions.'''
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "RFQ Application") #App Title
        ico_file = "C:/Users/njanzen/Documents/RFQ Application/triumf_logo.ico" #Adds Triumf icon
        tk.Tk.iconbitmap(self, default=ico_file)

        container = tk.Frame(self) #Creates a continer to help house all of the pages
        container.pack(side="top", fill="both", expand = True) #Configures container
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        self.LoadDeafaultFiles() #Loads in files
        self.AddMenu(container) #Loads in menus
        self.frames = {} #Sets up a dictionary for frames
        for page in (HomePage, Electrodes, RF_Settings, VacuumSystems): #Loops through all the frames and adds them to the dic
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage) #Initially shows the Home Page

        self.SetWindowSize(590,1080) #Sets size and centers window

    def show_frame(self, page_name):
        '''Function to show the frame page_name in the app.'''
        frame = self.frames[page_name]
        frame.tkraise()

    def GraphWindow(self, Page):
        '''Function to open a toplevel window of the chosen graph'''
        plot = Page(self)

    def OpenTopLevel(self, Page, options=range(6)):
        '''Function to open toplevel window for saving or loading files'''
        Popup = Page(self, options)

    def SetWindowSize(self, h, w):
        '''Sets window size and also centers the window of the monitor'''
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def AddMenu(self, container):
        '''Initializes all the dropdown menus for the application.'''
        menubar = tk.Menu(container) #Adds a menu instance

        # Adds a file menu with save, load, reset, and exit options
        filemenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save",
            command=lambda:self.OpenTopLevel(SavePage)) #Opens an instance of SavePage
        filemenu.add_command(label="Load Setting",
            command=lambda:self.OpenTopLevel(LoadPage)) #Opens an instance of LoadPage
        filemenu.add_command(label="Reset Settings to Default",
            command=lambda:self.ResetVals()) #Resets all values to default settings
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit) #Quits the app

        # Adds an edit menu for opening different
        editmenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="Edit", menu=editmenu)
        editmenu.add_command(label="Electrode Settings",
            command=lambda:self.show_frame(Electrodes)) #Shows the electrode frame
        editmenu.add_command(label="RF Settings",
            command=lambda:self.show_frame(RF_Settings)) #Shows the RF settings frame
        editmenu.add_command(label="Vacuum Controls",
            command=lambda:self.show_frame(VacuumSystems)) #Shows the vacuum system frame
        # This option can be added if there is a way to adjust data collection of buncher while in operation
        # editmenu.add_command(label="Buncher Options", command=Empty)
        editmenu.add_command(label="Change Default Files",
            command=lambda:self.OverWrite()) #Opens an instance of OverwritePage

        # Adds a menu that allows one to open a variety of different graph windows
        # to observe data collections. These windows open in a Toplevel window
        graphmenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="Graphs", menu=graphmenu)
        graphmenu.add_command(label="Pressure Readouts",
            command=lambda:self.GraphWindow(PressurePlot)) #Opens an instance of PressurePlot
        graphmenu.add_command(label="Temperature Readouts",
            command=lambda:self.GraphWindow(TemperaturePlot)) #Opens an instance of TemperaturePlot
        graphmenu.add_command(label="Potential Readouts",
            command=lambda:self.GraphWindow(ElectrodePlots)) #Opens an instance of ElectrodePlots
        graphmenu.add_command(label="RF Forward Power Readouts",
            command=lambda:self.GraphWindow(RF_Forward_Power_Plot)) #Opens an instance of RF_Forward_Power_Plot
        graphmenu.add_command(label="RF Reflected Power Readouts",
            command=lambda:self.GraphWindow(RF_Reflected_Power_Plot)) #Opens an instance of RF_Reflected_Power_Plot
        graphmenu.add_command(label="RF Phase Readouts",
            command=lambda:self.GraphWindow(RF_Phase_Plot)) #Opens an instance of RF_Phase_Plot

        tk.Tk.config(self, menu=menubar) #Configures this class to use the created menus

    def OverWrite(self):
        '''Creates an instance of OverwritePage where one can permanently change the
        default files for this application. Then reloads all files with the new changes'''
        self.OpenTopLevel(OverwritePage)
        self.LoadDeafaultFiles(False)

    def LoadDeafaultFiles(self, UpdateCurrent=True):
        '''Load all deafault data files to the application. Creates golbal data
        arrays for both the default and the current settings.'''
        loc = "C:/Users/njanzen/Documents/RFQ Application/Default Files/" #Loaction of files
        files = ("Trap", "Transfer", "Extraction", "RFSettings",
            "DeviceSettings","ElectrodeVoltages") #Lists all different files types to loop through
        de = "_Default.txt"

        # Creates an ordered dictionary that contains the default files for the app.
        # Concatenates the previous strings to make each file location for loading
        self.DefaultAppData = OrderedDict()
        self.DefaultAppData["Trapping Electrodes"] = np.loadtxt(loc+files[0]+de, delimiter=',')
        self.DefaultAppData["Transfer Electrodes"] = np.loadtxt(loc+files[1]+de, delimiter=',')
        self.DefaultAppData["Extraction Electrodes"] = np.loadtxt(loc+files[2]+de, delimiter=',')
        self.DefaultAppData["RF Settings"] = np.loadtxt(loc+files[3]+de, delimiter=',')
        self.DefaultAppData["Device Settings"] = np.loadtxt(loc+files[4]+de, delimiter=',')
        self.DefaultAppData["Electrode Voltages"] = np.loadtxt(loc+files[5]+de, delimiter=',')

        # Creates an ordered dictionary that contains all the current application
        # data. This dic gets called and updated many times in the applictation.
        # Starts off by setting all of the AppData to defualt values.
        if UpdateCurrent:
            self.AppData = OrderedDict()
            for key in self.DefaultAppData:
                self.AppData[key] = self.DefaultAppData[key]

    def ResetVals(self):
        '''Function resests all of the data to defualt values'''
        if msg.askokcancel('',"Reset all values to default?"):
            self.AppData = OrderedDict()
            for key in self.DefaultAppData:
                self.AppData[key] = self.DefaultAppData[key]

        # Recreates all frames to return settings to default.
        self.frames = {}
        for page in (HomePage, Electrodes, RF_Settings, VacuumSystems):
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(HomePage)

class HomePage(tk.Frame):
    '''A class using the tk.Frame framework. HomePage is the main page initialized
    application. It contains some of the basic RFQ settings as well as readouts like
    temp and pressure.'''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent) #Initializes as a tk Frame

        self.controller = controller
        self.get_settings(controller) #Loads in settings
        self.AddLabels() #Adds page labels
        self.AddPressure() #Adds the pressure graph
        self.AddTemperature() #Adds the temp graph

    def AddLabels(self):
        '''Adds several buttons that should interact with the actual device'''
        ttk.Button(self, text='Apply', command=lambda:
            Empty).grid(row=7, column=0, pady=4)
        ttk.Button(self, text='Reset', command=lambda:
            Empty).grid(row=7, column=1, pady=4)
        ttk.Button(self, text='Browse', command=lambda:
            Empty).grid(row=8, column=1, pady=4)
        tk.Label(self,text="RFQ Outputs",font =("Verdana",16),
        padx = 40).grid(row=1, column=3, pady=4, columnspan=10)

    def AddPressure(self):
        '''Adds the live pressure graph to the home page. It uses an intance of
        PlotFrame to create the live graph. It then adjusts come of the graph
        settings like title/limits. Binds a right click event that allows one to
        open the graph in a seperate window.
        Potential to add a radio button that can choose different pressure guages
        to read. The file used must be updated to contain real output data when
        device is live.'''
        self.PresFile = 'C:/Users/njanzen/Documents/RFQ Application/SampleData.txt'
        self.PressurePlot = PlotFrame(self,self.controller,
                                file_name=self.PresFile, toolbar=False)
        self.PressurePlot.grid(row=2,column=3,rowspan=3,columnspan=3,sticky='nsew')
        self.PressurePlot.a.set_title("Pressure")
        self.PressurePlot.a.set_xlim([0, 100])
        self.PressurePlot.a.set_ylim([0, 1])
        self.PressurePlot.line.set_color('blue')
        self.Pres_press = self.PressurePlot.canvas.mpl_connect('button_press_event',self.ViewPres)
        self.popup_Pres = tk.Menu(self.controller, tearoff=0) #Creates popup tab to open graph window
        self.popup_Pres.add_command(label="View Graph",
            command=lambda:self.controller.GraphWindow(PressurePlot))

    def ViewPres(self, event):
        '''The event that opens the graph in a seperate window. Creates a dropdown
        tab at the click location to open the window.'''
        frame_pos_x = self.PressurePlot.winfo_rootx() #Gets positions and height of the plot area
        frame_pos_y = self.PressurePlot.winfo_rooty()
        frame_height = self.PressurePlot.winfo_height()

        x_loc = int(frame_pos_x + event.x) #Uses a little math to ensure the event window appears right at the mouse
        y_loc = int(frame_pos_y + frame_height - event.y-35)
        if event.button == 3:
            self.popup_Pres.post(x_loc, y_loc)

    def AddTemperature(self):
        '''Adds the live temperature graph to the home page. It uses an intance of
        PlotFrame to create the live graph. It then adjusts come of the graph
        settings like title/limits. Binds a right click event that allows one to
        open the graph in a seperate window.'''
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
        '''The event that opens the graph in a seperate window. Creates a dropdown
        tab at the click location to open the window.'''
        frame_pos_x = self.TemperaturePlot.winfo_rootx()
        frame_pos_y = self.TemperaturePlot.winfo_rooty()
        frame_height = self.TemperaturePlot.winfo_height()

        x_loc = int(frame_pos_x + event.x)
        y_loc = int(frame_pos_y + frame_height - event.y-35)
        if event.button == 3:
            self.popup_Temp.post(x_loc, y_loc)

    def get_settings(self, controller):
        '''Function that loads in the main device settings. This function needs
        adjustments for real values and changes to which values are shown here.'''
        DeviceFields = ("Pressure (Bar)","Temperature (K)","Bunch Time (ms)",
            "RF Frequency (MHz)","RF Amplitude")
        InitSettings = np.array([1,1,1,1,1])
        self.ents = makeform(self,DeviceFields,InitSettings,2)

class Electrodes(tk.Frame):
    '''A class using the tk.Frame framework. Electrodes is a page where one can
    see the on axis potentials created by the different electrode settings. Helps
    visualize how the ions are trapped and extracted.'''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Electrode Settings", font=LARGE_FONT) #A title
        label.grid(row=0, columnspan=5)
        self.controller = controller
        self.ElectrodeTypes = ["Trapping Electrodes",
            "Transfer Electrodes","Extraction Electrodes"] #The three electrode configurations
        self.fields = ('E1', 'E2A', 'E2B', 'E2C','E2D','E3', 'E4A', 'E4B', 'E4C', 'E4D',
            'E5', 'Hyperboloid', 'Cone', 'Immersion', 'Ground', 'DragField') #The different electrodes
        self.numents = len(self.fields)
        self.DrawPotential("Trapping Electrodes", controller.AppData) #Draws the potentials
        # Highlights the selected configuration in graph area and creates labels for the electrodes and their potentials
        self.UpdateElectrodePage("Trapping Electrodes",controller.AppData)

        #Creates a radio button to select the different configs
        self.radio_button = tk.StringVar(self) #Sets up variable
        DisplayLabel = tk.Label(self,text="Electrode Configuration",
                    padx = 40).grid(row=1, column=3, pady=4) #Radio button label
        i = 0
        for key in self.ElectrodeTypes: #Loops through the configs assigning each a command to highlight thmselves on the graph when pressed
            tk.Radiobutton(self,text=key,padx=5,
                command=lambda: self.UpdateElectrodePage(self.radio_button.get(), controller.AppData),
                variable=self.radio_button,
                value=key).grid(row=2, column=i+3, pady=4)
            i = i+1

        self.radio_button.set("Trapping Electrodes") #Sets button to first config

        button1 = ttk.Button(self, text='Edit Potentials',
            command=lambda:EditElectrode(controller, self)) #Creates button that opens an electrode editor window
        button1.grid(row=self.numents+1,column=0, pady=15)
        button4 = ttk.Button(self, text="Back to Home",
            command=lambda:controller.show_frame(HomePage)) #Button that returns to home page
        button4.grid(row=self.numents+1,column=1, columnspan=2)

        #Adds in an image of the physical electrode setup
        gif = "C:/Users/njanzen/Documents/RFQ Application/Electrodes.gif"
        image = tk.PhotoImage(file=gif, master=controller)
        label = tk.Label(self,image=image)
        label.image = image
        label.grid(column=3,columnspan=3,row=self.numents-2, rowspan=4)

    def DrawLabels(self, config, DataSource):
        '''Draws all of the electrode labels and the associated values. Highlights
        the values when the electrode is on for a particular congiuration.'''
        is_on = DataSource[config] #Creates a list indicating which electrodes are on
        for i in range(self.numents): #Loops through all of the electrodes
            label1 = tk.Label(self,text=self.fields[i]) #Labels each electrode
            label1.grid(row=1+i)
            label2 = tk.Label(self,text=DataSource["Electrode Voltages"][0,i],width=9) #The ON electrode value
            label2.grid(row=1+i,column=1)
            label3 = tk.Label(self,text=DataSource["Electrode Voltages"][1,i],width=9) #The OFF value
            label3.grid(row=1+i,column=2)
            if is_on[i]: #Highlights the selected electrode voltage for the config
                label2.config(bg='pale violet red')
            else: label3.config(bg='pale violet red')

    def UpdateElectrodePage(self, config, DataSource):
        '''Function that redraws labels and highlights particular config on electrode graph.'''
        self.DrawLabels(config, DataSource)
        for i in range(3):
            if config == self.ElectrodeTypes[i]:
                confignum = i
        self.HighlightLine(confignum)

    def DrawPotential(self, config, DataSource):
        '''Creates a plot and then draws three lines--one for each config--on it.
        For each config it acquires the ON/OFF data for each electrode and then
        saves the associated voltage. Then runs each voltage list through a function
        that produced the on axis potential.'''
        ElectrodeData = np.zeros([3,self.numents]) #Sets up an array for electrode voltages
        for i in range(3): #Loops through each config and saves the voltage value based on the ON/OFF data
            data = DataSource[self.ElectrodeTypes[i]]
            for j in range(self.numents):
                if data[j]: #If ON saves the On voltage
                    ElectrodeData[i,j] = DataSource["Electrode Voltages"][0,j]
                else: ElectrodeData[i,j] = DataSource["Electrode Voltages"][1,j]
        # Creates a plot for the first config
        # Runs the electrode voltages through a function that scales the voltages and outputs the resulting potential
        TotPotential1 = self.ScalePotential(ElectrodeData[0,:])
        plot_data = [self.Location,TotPotential1[0:750]]
        self.plot_frame = PlotFrame(self,self.controller,data=plot_data,
            figsize=(8,3), add_label=False, ani_func=False) #Creates the graph using a PlotFrame instance
        self.plot_frame.grid(row=3,column=3,rowspan=self.numents-5,columnspan=3)
        self.plot_frame.a.set_xlim([0,75]) #Adjusts graphs settings
        self.plot_frame.a.set_ylim([-25,30])
        self.plot_frame.line.set_alpha(0.25)

        # Creates lines on plot_frame for the other configs
        TotPotential2 = self.ScalePotential(ElectrodeData[1,:]) #Scales potential
        self.plot_frame.a2 = self.plot_frame.f.add_subplot(111) #Adds new subplot
        lin2, = self.plot_frame.a2.plot([], [], color="blue", alpha=0.25) #Adds new line
        self.plot_frame.line2 = lin2
        self.plot_frame.line2.set_xdata(self.Location) #Adds data to the new line
        self.plot_frame.line2.set_ydata(TotPotential2[0:750])

        # Same as second config
        TotPotential3 = self.ScalePotential(ElectrodeData[2,:])
        self.plot_frame.a3 = self.plot_frame.f.add_subplot(111)
        lin3, = self.plot_frame.a3.plot([], [], color="blue", alpha=0.25)
        self.plot_frame.line3 = lin3
        self.plot_frame.line3.set_xdata(self.Location)
        self.plot_frame.line3.set_ydata(TotPotential3[0:750])

    def HighlightLine(self,confignum):
        '''Highlights the line in the potential graph based on the chosen config.'''
        self.plot_frame.line.set_alpha(0.25)
        self.plot_frame.line2.set_alpha(0.25)
        self.plot_frame.line3.set_alpha(0.25)
        if confignum == 0:
            self.plot_frame.line.set_alpha(1) #Increases alpha (opacity) of selected config
        elif confignum == 1:
            self.plot_frame.line2.set_alpha(1)
        else:
            self.plot_frame.line3.set_alpha(1)
        self.plot_frame.f.canvas.draw()

    def ScalePotential(self,ElectrodeData):
        '''Opens a text file containing the default scaling parameters then
        runs a function to scale each electrode voltage.'''
        DataFile = "C:/Users/njanzen/Documents/RFQ Application/VoltageScaling.txt"
        Data = np.loadtxt(DataFile, delimiter=',')
        Location = Data[:,0] #Extracts the location info from the data
        self.Location = Location[0:750]
        VoltageScaling = Data[:,1::] #Extracts the scaling info from the data

        # Based on the set electrode voltages, calculates the total potential on the Z
        # axis by scaling the VoltageScaling array
        PotentialArray = np.zeros(VoltageScaling.shape, dtype = float)
        for i in range(11): #The first 11 electrodes are saved twice in the data file (for the different phases)
            scaled = VoltageScaling[:,i*2:i*2+2] * ElectrodeData[i]
            PotentialArray[:,i*2:i*2+2] = scaled
        for i in range(5):
            scaled = VoltageScaling[:,i+22] * ElectrodeData[i+11]
            PotentialArray[:,i+22] = scaled

        TotPotential = map(sum, PotentialArray) #Sums the potential over all the electrode contributors
        return TotPotential

class RF_Settings(tk.Frame):
    '''A class using the tk.Frame framework. RF_settings is a page that uses some
    calculations in order to determine optimized RF amplitudes and freqencies
    based on the input parameters like ion mass. In addition, the page displays
    RFQ data outputs of the RF phase difference and power.'''
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller #To be used in class functions

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
            command=lambda:self.OptimizeWindow()).grid(row=10,column=0) #Intended to have a window used to optimize directly with RFQ
        ttk.Button(self,text='View Calculations',
            command=lambda:Empty).grid(row=10,column=1) #Button intended to have a popup that simply displays calculation used
        ttk.Button(self, text='Apply RF Parameters',
            command=lambda:self.ApplySettings()).grid(row=12, column=0) #Appies changes and displays new RF params
        ttk.Button(self, text="Back to Home",
            command=lambda:controller.show_frame(HomePage)).grid(row=15,column=1,pady=20) #Returns to home page
        ttk.Button(self, text="Save Settings",
            command=lambda:controller.OpenTopLevel(SavePage, options=[3])).grid(row=13,column=1) #Opens a save page for RF settings
        ttk.Button(self, text="Reset",
            command=lambda:self.ResetVals()).grid(row=12,column=1) #Resets values to last confirmed settings
        ttk.Button(self, text="Confirm",
            command=lambda:self.ConfirmSettings()).grid(row=13,column=0) #Confirms settings, reset now returns to these settings

        self.UpdateVars(self.controller.AppData["RF Settings"], confirm=True) #Loads initial variables and performs calculations

        InitSettings = [self.Q, self.A, self.TD, self.q_desired]
        self.fields = ('Ion Charge (e)','Ion Mass (AU)', 'Pseudopotential TD (V)', 'Desired Stability: q')
        self.RF_Ents = makeform(self,self.fields,InitSettings,rowstart=2) #Loads the fields and settings into an entry list

        tk.Label(self,text="RF Settings", font=("verdana", 16)).grid(row=0, column=0, columnspan=8, pady=4) #Title
        self.radio_button = tk.IntVar(self) #Initialize radio button vaiable, selects between forward and revers outout power
        tk.Radiobutton(self,text="Forward Power",variable=self.radio_button,
            command=lambda:self.RF_Power(self.radio_button.get()),
            value=0).grid(row=1,column=2)
        tk.Radiobutton(self,text="Reflected Power",variable=self.radio_button,
            command=lambda:self.RF_Power(self.radio_button.get()),
            value=1).grid(row=1,column=3)
        self.radio_button.set(0) #Sets button initially to forward power

        self.RF_Power(0) #Creates RF Power graph, defaults to forward
        self.RF_PhaseShift() #Creates RF Phase graph

    def ResetVals(self):
        '''Resets values to last confirmed configuration (or default).'''
        self.UpdateVars(self.OldVars) #Performs calculations with original variables
        Settings = [self.Q, self.A, self.TD, self.q_desired] #Remakes variables
        self.RF_Ents = makeform(self,self.fields,Settings,rowstart=2) #Remakes entries

    def ConfirmSettings(self):
        '''Confirms the current settings and then performs calculations'''
        variables = fetch(self.RF_Ents) #Retrieves current vars
        variables = variables + [0.005]
        self.UpdateVars(variables, confirm=True) #Performs calculation and sets vars

    def ApplySettings(self):
        '''Updates the variables while alowing to a reset to last settings'''
        variables = fetch(self.RF_Ents) #Retrieves current vars
        variables = variables + [0.005]
        self.UpdateVars(variables)  #Performs calculation and sets vars

    def UpdateVars(self, variables, confirm=False):
        '''Extracts values from variables and uses them to calculate all parameters'''
        self.Q = variables[0] #Ion Charge (e)
        self.e = self.Q*1.602E-19 #Ion Charge (C)
        self.A = variables[1] #Ion Mass (AU)
        self.m = self.A*1.66E-27 #Ion Mass (kg)
        self.TD = variables[2] #Pseudopotential (Trap Depth)
        self.q_desired = variables[3] #Maximum q value (not currently used in app)
        self.r0 = variables[4] #The hyperbolic radius of the electrodes

        self.Calc() #Performs calculation to find optimal frequency and other params

        if confirm: #Sets saves variables if confirmed
            self.OldVars = [self.Q,self.A,self.TD,self.q_desired,self.r0]

    def Calc(self):
        '''Function that calculates the RF amplitude required to achieve the
        desired psuedopotential for each of the two frequencies based on all of
        the input parameters. Also produces the stability parameter q. Then the
        function selects the frequency with the lower q value and saves the outputs
        from that frequency.'''
        Freq = 6 #High freq
        V_rf = math.sqrt((self.m * self.r0**2 * (2*math.pi*Freq*1E6)**2 * self.TD)/self.e) #Amp calc
        q = 4*self.TD/V_rf #q calc
        self.Freq_H = {"Freq":Freq,"V_rf":V_rf,"q":q} #Saves high freq data

        Freq = 3 #Low Freq
        V_rf = math.sqrt((self.m * self.r0**2 * (2*math.pi*Freq*1E6)**2 * self.TD)/self.e) #Amp calc
        q = 4*self.TD/V_rf #q calc
        self.Freq_L = {"Freq":Freq,"V_rf":V_rf,"q":q} #Saves low freq data

        if self.Freq_H["q"] < self.Freq_L["q"]: #Saves the data from the freq with the lower q value
            self.RF_vals = self.Freq_H
        else:self.RF_vals = self.Freq_L

        self.label3['text'] = str(self.RF_vals["Freq"]) #Updates window text with data from selected frequency
        self.label5['text'] = str(self.RF_vals["V_rf"])[0:6]
        self.label7['text'] = str(self.RF_vals["q"])[0:6]

    def RF_Power(self, plot):
        '''Function that creates live plot for RF power. Variable 'plot' is either
        0 for forward power or 1 for reflected.'''
        self.ForwardPowerFile = 'C:/Users/njanzen/Documents/RFQ Application/Forward_Power.txt' #File for forward power
        self.ReflectedPowerFile = 'C:/Users/njanzen/Documents/RFQ Application/Reflected_Power.txt' #File for reflected power
        PowerFiles = [self.ForwardPowerFile,self.ReflectedPowerFile] #Lists files
        self.RFPower_plot = PlotFrame(self,self.controller,
            file_name=PowerFiles[plot], toolbar=False) #Instance of PlotFrame using data from one of the two data files
        self.RFPower_plot.grid(row=2,column=2,rowspan=6,columnspan=3,sticky='nsew') #Formatting plot
        self.RFPower_plot.a.set_title("RF Power")
        self.RFPower_plot.a.set_xlim([0, 100])
        self.RFPower_plot.a.set_ylim([-3, 3])
        self.RFPower_plot.line.set_color('magenta')
        self.Power_press = self.RFPower_plot.canvas.mpl_connect('button_press_event',self.ViewPower) #Creates event to open seperate graph window
        self.popup_Power = tk.Menu(self.controller, tearoff=0) #Creates dropdown when main plot is right clicked
        self.popup_Power.add_command(label="View Graph",
            command=lambda:self.PowerOption(self.radio_button.get()))

    def ViewPower(self, event):
        '''Event that opens a dropdown at the mouse when the graph is right clicked.'''
        frame_pos_x = self.RFPower_plot.winfo_rootx()
        frame_pos_y = self.RFPower_plot.winfo_rooty()
        frame_height = self.RFPower_plot.winfo_height()
        x_loc = int(frame_pos_x + event.x)
        y_loc = int(frame_pos_y + frame_height - event.y-35)
        if event.button == 3:
            self.popup_Power.post(x_loc, y_loc)

    def PowerOption(self, option):
        '''Selects which graph window to open up based on which graph was currently
        on display on the RF_settings page.'''
        Options = [RF_Forward_Power_Plot,RF_Reflected_Power_Plot]
        self.controller.GraphWindow(Options[option])

    def RF_PhaseShift(self):
        '''Function that creates live plot for the RF phase shift.'''
        self.RFPhaseFile = 'C:/Users/njanzen/Documents/RFQ Application/RF_PhaseShift.txt' #File for phase data
        self.RFPhase_plot = PlotFrame(self,self.controller,
            file_name=self.RFPhaseFile, toolbar=False) #Instance of PlotFrame using phase data
        self.RFPhase_plot.grid(row=8,column=2,rowspan=6,columnspan=3,sticky='nsew') #Formatting plot
        self.RFPhase_plot.a.set_title("RF Phase Shift")
        self.RFPhase_plot.a.set_xlim([0, 100])
        self.RFPhase_plot.a.set_ylim([-3, 3])
        self.RFPhase_plot.line.set_color('orange')
        self.Phase_press = self.RFPhase_plot.canvas.mpl_connect('button_press_event',self.ViewPhase) #Creates event to open seperate graph window
        self.popup_Phase = tk.Menu(self.controller, tearoff=0) #Creates dropdown when plot is right clicked
        self.popup_Phase.add_command(label="View Graph",
        command=lambda:self.controller.GraphWindow(RF_Phase_Plot))

    def ViewPhase(self, event):
        '''Event that opens a dropdown at the mouse when the graph is right clicked.'''
        frame_pos_x = self.RFPhase_plot.winfo_rootx()
        frame_pos_y = self.RFPhase_plot.winfo_rooty()
        frame_height = self.RFPhase_plot.winfo_height()
        x_loc = int(frame_pos_x + event.x)
        y_loc = int(frame_pos_y + frame_height - event.y-35)
        if event.button == 3:
            self.popup_Power.post(x_loc, y_loc)

    def OptimizeWindow(self):
        '''This window has not been developed yet, intended to include some
        interaction with the RFQ device to optimize settings.'''
        Window = tk.Toplevel(self)
        ttk.Button(Window,text='Close',command=lambda:Window.destroy()).pack()
        Window.grab_set()

class VacuumSystems(tk.Frame):
    '''A window for activating any of the systems pumps and inlets. Page is
    currently underdeveloped and will need some attention once online testing
    begins. Ideally should be able to monitor and control flow here as well.'''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        # Creates check boxes for turning turbopumps on and off
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
        # Creates check boxes for turning gas inlets on and off
        tk.Label(self,text="Gas Inlets").grid(row=8)
        var10 = tk.IntVar()
        tk.Checkbutton(self, text="Inlet 1", variable=var10).grid(row=9, sticky=tk.W)
        var11 = tk.IntVar()
        tk.Checkbutton(self, text="Inlet 2", variable=var11).grid(row=10, sticky=tk.W)

        ttk.Button(self,text="Apply",command=lambda:Empty()).grid(row=14) #Button that can be updated to officially activate pumps
        ttk.Button(self,text="Back to Home",
            command=lambda:controller.show_frame(HomePage)).grid(row=17,column=0) #Opens home frame
        # Adds a piture with the locations of pumps and gas inlets
        gif = "C:/Users/njanzen/Documents/RFQ Application/RFQ Crossection.gif"
        image = tk.PhotoImage(file=gif, master=controller)
        label = tk.Label(self,image=image)
        label.image = image
        label.grid(column=1,row=1, rowspan=20)

class PlotFrame(tk.Frame):
    '''IMPORTANT class for this application. Used by most frames of the app to help
    create and run any live updating plots for RFQ output data. It is also used for
    any popup windows that contain graphs. Its key features are attaching the
    matplotlib plot to a tkinter canvas to display it in the frames and animate
    function which takes a file location and constantly updates the date on the graph
    as the file data changes. The RFQ is to output data into these files so that
    it can be read into the app and constantly update the plots.'''
    def __init__(self, parent, controller, data=None, file_name=None, ani_func=True,
        toolbar=True, add_label=True, figsize=(7,2), ):
        ''''Data' variable is an array that can be used to simply plot a specific
        set of data already contained in the app. 'file_name' is a string that holds
        the file location for importing data. 'ani_func' is a BOOL that desides
        whether to constantly update the plot with file data. 'toolbar' is a BOOL
        that decides whether to adda toolbar to the plot. 'add_label' is a BOOL
        that decides whether to print the most recent (last) data value from the
        imported data set in the app window.'''
        tk.Frame.__init__(self, parent)

        self.f = Figure(figsize=figsize) #Creates matplotlib figure
        self.a = self.f.add_subplot(111) #Adds plot to figure

        potentialcanvas = FigureCanvasTkAgg(self.f, self) #Attaches figure f to the current tkinter window
        potentialcanvas.show() #Shows the canvas
        potentialcanvas.get_tk_widget().pack() #Places canvas on current window
        self.canvas = potentialcanvas
        if toolbar: #Adds toolbar to plot
            plot_toolbar = NavigationToolbar2TkAgg(self.canvas,self)
            plot_toolbar.update()
            self.canvas._tkcanvas.pack()

        lin, = self.a.plot([], [], color="blue") #Creates the data line on the graph
        self.line = lin

        if ani_func: #Sets up the plot to automatically update the plot with data from the file
            try:
                self.animate(File=file_name) #Performs a single initial animate to immediately update plot
                # Runs a matplotlib animation function that runs animate every 1000ms to continually update figure f
                # fargs adds other function arguments that animate needs to run
                self.ani = animation.FuncAnimation(self.f, self.animate,
                fargs=(file_name,add_label), interval=1000)
            except: pass
        else: #Sets line points to the data input data array
            self.line.set_xdata(data[0])
            self.line.set_ydata(data[1])

    def animate(self, i=None, File='', add_label=True):
        '''Function that updates self.line with new data from the imported file.'''
        Data = np.loadtxt(File, delimiter=',') #Loads in data
        self.line.set_xdata(Data[:,0]) #Updates x vals
        self.line.set_ydata(Data[:,1]) #Updates y vals
        Val = str(Data[-1,1])
        text=Val[0:6]
        if add_label: #Adds a label with the most recent value
            try:self.label.destroy()
            except:pass
            self.label = tk.Label(self,text=text,font=("verdana",18))
            self.label.pack()

class EditElectrode(tk.Toplevel):
    '''Class that creates a Toplevel window for editing electrode settings.'''
    def __init__(self, controller, parent, *args):
        tk.Toplevel.__init__(self)
        self.controller = controller #Turns inputs into self attributes so they can be called in later functions
        self.parent = parent

        label = tk.Label(self, text="Adjusting Voltages", font=LARGE_FONT) #Title
        label.grid(row=0, columnspan=5)
        self.ElectrodeTypes = ["Trapping Electrodes",
            "Transfer Electrodes","Extraction Electrodes"] #Initializes the config types
        self.fields = ('E1', 'E2A', 'E2B', 'E2C','E2D','E3', 'E4A', 'E4B', 'E4C', 'E4D',
            'E5', 'Hyperboloid', 'Cone', 'Immersion', 'Ground', 'DragField') #List of all electrodes
        self.numents = len(self.fields) #Number of electrodes

        self.AllElectrodeData = {} #Creates a dictionary for the data
        self.CreateElectrodeEntries() #Creates the entries in the windows

        button1 = ttk.Button(self, text='Veiw Potential',
            command=lambda:self.UpdateGraph()) #Button to update the graph on Electrodes page
        button1.grid(row=self.numents+3,column=0)
        button2 = ttk.Button(self, text="Reset",
            command=lambda:self.ResetData()) #Returns the entries to the last confirmed settings
        button2.grid(row=self.numents+3,column=1)
        button3 = ttk.Button(self, text='Confirm Electrode Config',
            command=lambda:self.ConfirmConfig()) #Confirms the electrode settings, reset now returns to these settings
        button3.grid(row=self.numents+4,column=0)
        button4 = ttk.Button(self, text="Save Electrode Config",
            command=lambda:controller.OpenTopLevel(SavePage, options=range(3)+[5])) #Opens a Save window
        button4.grid(row=self.numents+4,column=1)
        button5 = ttk.Button(self, text="Back to Home",
            command=lambda:controller.show_frame(HomePage)) #Returns the home window
        button5.grid(row=self.numents+5,column=1)

    def ConfirmConfig(self):
        '''Updates the application's AppData and becomes the new settings to which
        reset returns to.'''
        self.Fetch_Data() #Calls the current settings based on the entry fields
        for key in self.ElectrodeTypes: #Updates AppData
            self.controller.AppData[key] = self.AllElectrodeData[key]
        self.controller.AppData["Electrode Voltages"] = self.AllElectrodeData["Electrode Voltages"]
        for key in self.AllElectrodeData: #Confirms current settings
            self.PrevElectrodeData[key] = self.AllElectrodeData[key]
        self.UpdateGraph()

    def UpdateGraph(self):
        '''Runs functions in the parent window 'Electrodes' in order to update the
        plots located there. See class for function details.'''
        self.Fetch_Data()
        self.parent.DrawPotential(self.parent.radio_button.get(),self.AllElectrodeData)
        self.parent.UpdateElectrodePage(self.parent.radio_button.get(),self.AllElectrodeData)

    def ResetData(self):
        '''Returns the window to the lsat confirmed settings.'''
        self.CreateElectrodeEntries(init=False)
        self.UpdateGraph()

    def Fetch_Data(self):
        '''Fetches all of the current setting on the editor page.'''
        i = 0
        # Loops through each type and identifies the state of each voltage switch
        for TrapType in [self.trap_labels, self.trans_labels, self.extract_labels]:
            Data = np.zeros(self.numents)
            for Electrode in range(self.numents):
                label = TrapType[Electrode]
                if label.cget("text") == "ON":
                    Data[Electrode] = 1
                else:
                    Data[Electrode] = 0
            self.AllElectrodeData[self.ElectrodeTypes[i]] = Data #Saves the state data
            i = i+1

        nums1 = []
        nums2 = []
        for entry in self.entries: #Loops through each entry and returns both the ON and OFF voltage setting
            field = entry[0]
            num1 = entry[1].get()
            num2 = entry[2].get()
            nums1.append(num1)
            nums2.append(num2)
        self.AllElectrodeData["Electrode Voltages"] = np.array([map(float,nums1), map(float,nums2)])

    def CreateElectrodeEntries(self, init=True):
        '''Function that creates all of the labels and the entries for the editor page.'''
        tk.Label(self,text="Electrode").grid(row=1,column=0) #Creates headers
        tk.Label(self,text="ON Voltage").grid(row=1,column=1)
        tk.Label(self,text="OFF Voltage").grid(row=1,column=2)
        tk.Label(self,text="Trap\nStates").grid(row=1,column=3)
        tk.Label(self,text="Transfer\nStates").grid(row=1,column=4)
        tk.Label(self,text="Extract\nStates").grid(row=1,column=5)

        if init: #If this is the first time the function is run, it uses AppData
            VoltageValues = self.controller.AppData["Electrode Voltages"]
            trap_state = self.controller.AppData["Trapping Electrodes"]
            trans_state = self.controller.AppData["Transfer Electrodes"]
            extract_state = self.controller.AppData["Extraction Electrodes"]
        else: #If this is not the first time, it resets to previous data
            VoltageValues = self.PrevElectrodeData["Electrode Voltages"]
            trap_state = self.PrevElectrodeData["Trapping Electrodes"]
            trans_state = self.PrevElectrodeData["Transfer Electrodes"]
            extract_state = self.PrevElectrodeData["Extraction Electrodes"]

        # Initializes a number of empty lists for later use
        self.entries = []
        self.trap_labels = []
        self.trans_labels = []
        self.extract_labels = []
        for i in range(self.numents): #Loops through all the electrodes
            label1 = tk.Label(self,text=self.fields[i]) #Creates a label for the electrode name
            label1.grid(row=2+i)
            entryON = tk.Entry(self) #Creates an entry for the ON voltage
            entryON.insert(0,str(VoltageValues[0,i]))
            entryON.grid(row=2+i,column=1)
            entryOFF = tk.Entry(self) #Creates an entry for the OFF voltage
            entryOFF.insert(0,str(VoltageValues[1,i]))
            entryOFF.grid(row=2+i,column=2)

            label2 = ON_OFF_Label(self) #Creates an ON/OFF state label for the first electrode config
            label2.grid(row=2+i,column=3,padx=2)
            self.trap_labels.append(label2) #Adds label to list of first config labels
            if trap_state[i]: #Adds colour based on state
                label2.configure(text='ON',bg='lawn green')
            else:
                label2.configure(text='OFF',bg ='firebrick1')
            label3 = ON_OFF_Label(self) #Creates a state label for second config
            label3.grid(row=2+i,column=4,padx=2)
            self.trans_labels.append(label3) #Adds label to list of second config labels
            if trans_state[i]: #Adds colour based on state
                label3.configure(text='ON',bg='lawn green')
            else:
                label3.configure(text='OFF',bg ='firebrick1')
            label4 = ON_OFF_Label(self) #Creates a state label for third config
            label4.grid(row=2+i,column=5,padx=2)
            self.extract_labels.append(label4) #Adds label to list of third config labels
            if extract_state[i]: #Adds colour based on state
                label4.configure(text='ON',bg='lawn green')
            else:
                label4.configure(text='OFF',bg ='firebrick1')
            self.entries.append((self.fields[i], entryON, entryOFF)) #Creates a list of the voltage entries

        self.Fetch_Data() #Returns all current data settings
        if init: #If this is the first run of the function, creates a dictionary to house most recent confirmed data
            self.PrevElectrodeData = {}
            for key in self.AllElectrodeData:
                self.PrevElectrodeData[key] = self.AllElectrodeData[key]

'''Next several classes are all just a variation of PlotFrame using a tkinter
Toplevel window to display a live graph for different RFQ data outputs. They each
have a file location and then build the PlotFrame with that file. Then they do
some small configurations to the plot.'''

class PressurePlot(tk.Toplevel):
    '''Class to create the live Pressure readout window.'''
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
    '''Class to create the live Temperature readout window.'''
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
    '''Class to create show the electrode potential switches over time. Needs
    further developement. Probably wont show live updates (since the switching
    will be on the order of 10-100ms) but can illustrate the switches over time
    1/10 or 1/100 speed for instance.'''
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
    '''Class to create the live RF Forward Power readout window.'''
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
    '''Class to create the live RF reflected power readout window.'''
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
    '''Class to create the live phase difference readout window.'''
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
    '''A Toplevel window used to overwrite the default files of this application.
    Should be used generally after some optimal settings are found for the RFQ.
    One selects a saved file to upload as the new default file.'''
    def __init__(self, controller, options=range(6), *args):
        '''Options is a list of all the AppData files that are included in the
        window's dropdown. Each number on the list corresponds to the location of
        the variable in the AppData ordered dictionary created at the start of the app.'''
        tk.Toplevel.__init__(self)
        self.title = 'Overwrite Default Files' #Title

        self.AppKeys = controller.AppData.keys() #List of all possible keys
        self.saveoptions = ['']*len(options) #Initialize list for dropdown options
        self.savedata = [None]*len(options) #Initializes list for data
        j = 0
        for i in options: #If the index of the AppData key is in options, adds that key to saveoptions
            self.saveoptions[j] = self.AppKeys[i]
            self.savedata[j] = controller.AppData[self.AppKeys[i]]
            j = j+1

        variable = tk.StringVar(self) #Creates StringVar for all the options
        variable.set(self.saveoptions[0]) #Sets to first option
        drop_down = apply(tk.OptionMenu, (self, variable) +
            tuple(self.saveoptions)) #Creates drop down with all saveoptions
        drop_down.grid(row=0,column=0) #Configures dropdown
        drop_down.config(width=20)

        Label = tk.Label(self, text = "File Name").grid(row=1, column=0) #Label to show where to input
        var = tk.StringVar(self) #Variable for the file name
        var.set("")
        file_name = tk.Entry(self, textvariable=var).grid(row=1, column=1) #Entry for the file name
        file_button = ttk.Button(self, text='Browse',
            command = lambda: SetFile(var)).grid(row=1, column=3) #Button to browse for a file
        apply_button = ttk.Button(self, text='Apply',
            command = lambda: self.OverwriteDefault(controller,
            var.get(),variable.get())).grid(row=2, column=3) #Confirms the save

        self.grab_set() #Locks window so save must occur before main app can be accesed

    def OverwriteDefault(self, controller, source, savetype):
        '''Function that uses the inputs in the OverwriteWindow to save the file
        as the default.'''
        # Maybe insert a password here for final application
        dest_dir = 'C:/Users/njanzen/Documents/RFQ Application/'
        # Should fix this to account for AppData changes
        default_names = ["Trap_Default.txt","Transfer_Default.txt",
            "Extraction_Default.txt","RFSettings_Default.txt",
            "DeviceSettings_Default.txt","ElectrodeVoltages_Default.txt"] #List of possible save file names

        i = 0
        for key in controller.AppData: #Chooses a save file name based on the selected dropdown option
            if  savetype == key:
                default_file_name = default_names[i]
            i = i+1

        destination = dest_dir + 'Default Files/' + default_file_name #Creates desination file name
        NewData = np.loadtxt(source, delimiter=',') #Imports the new data
        OldData = np.loadtxt(destination, delimiter=',') #Imports the opld data
        if len(NewData) == len(OldData): #Ensures they are the same length to not cause future error
            if source == destination: #Makes sure the new data is actually new
                msg.showerror('Already Default',
                'This File is already the default.')
            else: #Double checks to make sure overwriting defaults is okay
                if msg.askokcancel('Warning',"Are you sure you wish to update\nthe deafult files for this application?"):
                    copyfile(source, destination) #Replaces the old with the new
                    self.grab_release() #Lets one access the main app again
                    self.destroy() #Destroys overwrite window
        else: msg.showerror('Illegal File',
        'The save file does not meet the dimension\nrequirements for the default file.') #Creates error cause files are not compatable

class SavePage(tk.Toplevel):
    '''A Toplevel window used to save the current settings of the application.
    Should be used whenever an optimized setting setting has been found for the
    RFQ so that the setting can be reloaded at a different time.'''
    def __init__(self, controller, options=range(5), *args):
        tk.Toplevel.__init__(self)
        self.title = 'Save' #Title

        self.AppKeys = controller.AppData.keys() #List of all possible keys
        self.saveoptions = ['']*len(options) #Initialize list for dropdown options
        self.savedata = [None]*len(options) #Initializes list for data

        j = 0
        for option in options: #If the index of the AppData key is in options, adds that key to saveoptions
            self.saveoptions[j] = self.AppKeys[option]
            self.savedata[j] = controller.AppData[self.AppKeys[option]]
            j = j+1

        variable = tk.StringVar(self) #Creates StringVar for all the options
        variable.set(self.saveoptions[0]) #Sets to first option
        drop_down = apply(tk.OptionMenu, (self, variable) +
            tuple(self.saveoptions)) #Creates drop down with all saveoptions
        drop_down.grid(row=0,column=0) #Configures dropdown
        drop_down.config(width=20)

        #Lets one input a name to save the data as
        Label1 = tk.Label(self, text = "File Name").grid(row=1, column=0)
        self.var1 = tk.StringVar(self) #Sets up variable to retrieve text
        self.var1.set("")
        file_name = tk.Entry(self, textvariable=self.var1).grid(row=1, column=1)

        #Lets one input or browse for a directory to save the file in
        Label2 = tk.Label(self, text = "Directory").grid(row=2, column=0)
        self.var2 = tk.StringVar(self) #Sets up variable to retrieve text
        self.var2.set("")
        dir_name = tk.Entry(self, textvariable=self.var2).grid(row=2, column=1)
        file_button = ttk.Button(self, text='Browse',
            command=lambda: SetDir(self.var2)).grid(row=3, column=0) #Browse button

        save_button = ttk.Button(self, text='Okay',
            command=lambda: self.ApplySave(controller, variable.get(),
            self.var2.get(),self.var1.get())).grid(row=3, column=1) #Applies the save

        self.grab_set() #Locks window so save must occur before main app can be accesed

    def ApplySave(self, controller, savetype, save_dir, save_name):
        '''Function thta uses the save window inputs to save the data as the given
        file name in the given directory'''
        if save_name[-4:] == ".txt": #Ensures the file name has the proper file format
            full_name = save_dir+'/'+save_name
        else:
            full_name = save_dir+'/'+save_name+".txt"
        np.savetxt(full_name, controller.AppData[savetype], delimiter=',', fmt='%1.4e') #Saves the file

        self.grab_release() #Lets one access the main app again
        self.destroy() #Destroys overwrite window

class LoadPage(tk.Toplevel):
    '''A Toplevel window used to load in saved settings to the app.'''
    def __init__(self, controller, options=range(5), *args):
        tk.Toplevel.__init__(self)
        self.title = 'Load'

        self.AppKeys = controller.AppData.keys() #List of all possible keys
        self.saveoptions = ['']*len(options) #Initialize list for dropdown options
        self.savedata = [None]*len(options) #Initializes list for data

        j = 0
        for option in options: #If the index of the AppData key is in options, adds that key to saveoptions
            self.saveoptions[j] = self.AppKeys[option]
            self.savedata[j] = controller.AppData[self.AppKeys[option]]
            j = j+1

        variable = tk.StringVar(self) #Creates StringVar for all the options
        variable.set(self.saveoptions[0]) #Sets to first option
        drop_down = apply(tk.OptionMenu, (self, variable) +
            tuple(self.saveoptions)) #Creates drop down with all saveoptions
        drop_down.grid(row=0,column=0) #Configures dropdown
        drop_down.config(width=20)

        Label = tk.Label(self, text = "File Name").grid(row=1, column=0) #Label for input
        var = tk.StringVar(self) #Variable to for calling input
        var.set("")
        file_name = tk.Entry(self, textvariable=var).grid(row=1, column=1)n #Entry to input file name
        file_button = ttk.Button(self, text='Browse',
            command = lambda: SetFile(var)).grid(row=1, column=3) #Browse for file name

        apply_button = ttk.Button(self, text='Load',
            command = lambda: self.Load(controller, var.get(),variable.get())).grid(row=2, column=3) #Button to load settings
        self.grab_set() #Locks window so save must occur before main app can be accesed

    def Load(self, controller, source, loadtype):
        '''Function that loads the data into the app.'''
        NewData = np.loadtxt(source, delimiter=',') #Imports the load file
        if len(NewData) == len(controller.AppData[loadtype]): #Makes sure the load file is compatable
            controller.AppData[loadtype] = NewData #Sets the app's settings with the new data
            self.grab_release() #Lets one access the main app again
            self.destroy() #Destroys overwrite window
        else: msg.showerror("Illegal File",
            "The load file does not meet the dimension requirements") #Error if not compatable

class ON_OFF_Label(tk.Label):
    '''A tkinter Label class. It is used for the electrode editor page to make a
    bunch of coloured labels that switch colours and text when clicked.'''
    def __init__(self, controller, *args, **kwargs):
        tk.Label.__init__(self, controller, *args, **kwargs)
        self.bind("<Button-1>", lambda e:self.flip_ON_OFF()) #Event that flips the switch when the label is left clicked
        self.configure(width=8) #Makes sure label has constant size
    def flip_ON_OFF(self):
        '''Function to change the label colour and text when clicked.'''
        if self.cget("text") == "ON": #If on, turn off
            self.configure(text='OFF',bg ='firebrick1')
        else: #If off, turn on
            self.configure(text='ON',bg='lawn green')

def Empty():
    '''Simple function to put as a button command when there is no command created
    yet for the button.'''
    msg.showerror("No Function", "Sorry, button in developement.")


def fetch(entries):
    '''A function to fetch the data related to any entries in an entry widget.
    'entries' is an array of lists with length 2 which the entry instance and a
    cooresponding entry text to get the entry value.'''
    nums = [] #List for final values
    for entry in entries: #Loop through all entries
        field = entry[0] #Return entry name
        num = entry[1].get() #Return entry value
        nums.append(num) #Add to list
    # Assumes the entry value string is a number and converts it to a float
    return map(float,nums)


def makeform(root, fields, initData, rowstart=0, colstart=0):
    '''A function to create the Tkinger entry forms.
    'fields' is a list of strings for each entry field.
    'initData' is an array of the initial values for each entry.'''
    entries = [] #List of tuples that contains the entry instance and its value
    i = 0
    for field in fields: #Loops through all entry fields
        lab = tk.Label(root, text=field, anchor='w') #Creates the field label
        lab.grid(row=rowstart+i,column=colstart)
        ent = tk.Entry(root) #Creates the entry sidget
        ent.insert(0, str(initData[i]))# Adds the initial value to each entry
        ent.grid(row=rowstart+i,column=colstart+1)
        entries.append((field, ent)) #Adds variables to tuple list
        i += 1
    return entries

def SetDir(var):
    '''Function that opens a browse window and then sets the input 'var' to the
    selected directory name.'''
    directory = dlg.askdirectory()
    if directory:
        var.set(directory)

def SetFile(var):
    '''Function that opens a browse window and then sets the input 'var' to the
    selected file name.'''
    filename = dlg.askopenfilename()
    if filename:
        var.set(filename)

if __name__ =='__main__':
    main()
