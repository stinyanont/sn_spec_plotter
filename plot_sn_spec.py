# import all classes/methods
# from the tkinter module
import tkinter as tk
# from turtle import window_width
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)


import numpy as np
import astropy.io.ascii as asci

import astropy.constants as const
import astropy.units as u
import copy, os, sys
# print(sys.argv)
#some default parameters
if len(sys.argv) == 2: #Can take filename as an argument from command line
    filename = sys.argv[1]
else:
    filename = None #Start with this before browsed
print(filename)
z = 0 #redshift
v = 0 #line velocity
c = const.c.to(u.km/u.s).value #speed of light from astropy constants

# default_path = "/Users/kaew/work/optical_spectra/20210611_Kast" #########For testing
# default_path = '.'
default_path = os.getcwd() #current path where the code is called. 

# Set up the main tkinter window
window = tk.Tk()
  
# setting the title and 
window.title('Supernova Spectrum Plotter')

# setting the dimensions of 
# the main window
window.geometry("1000x600")

#####This window is divided into two frames
#Left frame for plotting
plotting_frame = tk.Frame(window, width=800, height = 600)
plotting_frame.pack(side = tk.LEFT)
#Right frame for plot controls (redshift, line velocity, etc)
button_frame = tk.Frame(window, width=200, height = 600)
button_frame.pack(side = tk.RIGHT)

########Set up the matplotlib fig and axis for the plot
# the figure that will contain the plot
fig = Figure(figsize = (8, 5),
                dpi = 100)
# adding the subplot
plot1 = fig.add_subplot(111)
plot1.set_ylabel("Flux", fontsize = 12)
plot1.tick_params(labelsize = 12)
spectrum_plot = plot1.step([],[])
spectrum_plot[0].set_visible(False)

#This axis is for plotting the line markers
spec_lines = plot1.twinx()

# creating the Tkinter canvas
# containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig,
                            master = plotting_frame)  



#Define a function to plot the spectrum from 
#a specified file and redshift
def plot_spec(filename, z):
    if filename is not None:
        try:
            sn_spec = asci.read(filename, names = ('wavelength', 'flux', 'fluxerr'))
            title = filename.split('/')[-1]
        except:
            try:
                sn_spec = asci.read(filename, names = ('wavelength', 'flux'))
                title = filename.split('/')[-1]
            except:
                title = 'Make sure the spectrum file is an ascii file with wavelenght and flux.'
        x = sn_spec['wavelength']
        y = sn_spec['flux']
    else:
        title = 'No File Selected'
        # Just blank x and y
        x = np.array([])
        y = np.array([])

    # plotting the graph
    # plot1.cla()
    # plot1.grid()
    # spectrum_plot = plot1.step(x/(1+z),y, lw = 2)
    #Use new data to update the data used for the spectrum plot. 
    spectrum_plot[0].set_data(x/(1+z),y) 
    spectrum_plot[0].set_visible(True) #make it visible
    # plot1.set_xlim([np.min(x/(1+z)), np.max(x/(1+z))]) #Set x,y lims
    # plot1.set_ylim([np.min(y), np.max(y)])
    # recompute the ax.dataLim
    plot1.relim()
    # update ax.viewLim using the new dataLim
    plot1.autoscale_view()

    plot1.set_xlabel(r"Wavelength $\rm \AA$ (z = %.4f)"%z, fontsize = 12)
    plot1.set_title(title, fontsize = 12)
    fig.tight_layout()
    canvas.draw()
    # plot1.clear()

def update_plot(z, old_z):
    """
    This function updates the plot by resetting data in the Line2D object.
    Doing it this way rather than redrawing the line preserves zoom/pan settings. 
    """
    x, y = spectrum_plot[0].get_data()
    spectrum_plot[0].set_data(x*(1+old_z)/(1+z),y)
    # spectrum_plot[0].set_visible(True)
    # # recompute the ax.dataLim
    # plot1.relim()
    # # update ax.viewLim using the new dataLim
    # plot1.autoscale_view()

    plot1.set_xlabel(r"Wavelength $\rm \AA$ (z = %.4f)"%z, fontsize = 12)
    # plot1.set_title(title, fontsize = 12)
    # fig.tight_layout()
    canvas.draw()
    # plot1.clear()
  
#Define a function that deals with file browsing.
def browseFiles():
    #Get file name form the file dialog
    global filename
    global z
    filename = tk.filedialog.askopenfilename(initialdir = default_path,
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt *.flm *.dat"),
                                                       ("all files",
                                                        "*.*")))
    #plot the spectrum
    plot_spec(filename, z)
    # Change label contents to display the file name.
    # We define this label later in the code
    # label_file_explorer.configure(text="File Opened: "+filename)

############If filename is given from the command line
if filename is not None:
    plot_spec(filename, z)


#Add a button to bring up file dialog
button_explore = tk.Button(button_frame,
                        text = "Browse Files",
                        command = browseFiles)
button_explore.grid(row = 1, column = 2)


############Set redshift 
def callback_z(sv):
    """
    callback function to set z when a new number is entered
    """
    global z
    old_z = copy.deepcopy(z)
    # print(sv.get())
    try:
        z = float(sv.get())
    except:
        z = 0
    # plot_spec(filename, z)
    # print(z, old_z)
    update_plot(z, old_z)

#Set up a text box to get redshift
sv_z = tk.StringVar()
sv_z.trace("w", lambda name, index, mode, sv=sv_z: callback_z(sv_z))

ztext = tk.Label(button_frame, text = 'z = ')
ztext.grid(row = 2, column = 1)

zbox = tk.Entry(master = button_frame, width=10, textvariable=sv_z)
zbox.insert(0, '%f'%z)
# zbox.pack(side = LEFT)
zbox.grid(row = 2, column = 2)
    
####Define a helper function for spectral line plotting
###############PLOTTING LINES
lines_to_plot = []
#dictionary for the color of the line for each element
element_color_dict = {'H':'r', 'He':'y', 'Si':'c', 'O':'b', 'C':'m', 'Mg':'C0', '[CaII]':'C1', 'Na':'C2'} #TO DO add more
#dictionary for line style: solid for permitted, dashed for forbidden, and dotted for semi-forbidden
ls_dict = {'p':'-', 'f':'--', 's':':'} 

all_elements = ['H', 'He', 'Si', 'O', 'C', '[CaII]', 'Mg', 'Na']
toPlots = [tk.BooleanVar(False)]*len(all_elements) #whether or not to plot this element
element_box = [0]*len(all_elements)
wl_plot = [ [4102, 4341,4861,6563, 10940, 12820, 18750, 21660], 
[20581,10830,7065,6678,5876,4472,3886], 
[4128,4131,5958,5979,6347,6371], 
[6158,7772,7774,7775,8446,9263], 
[], 
[7292,7324],
[],
[ 5890,5896]]

def updateLines():
    """
    a function to update line plotting
    """
    #clear all lines
    spec_lines.cla()
    # print('v=',v)
    #plot the ones requested.
    for ind, element in enumerate(all_elements):
        if toPlots[ind].get() == True:
            for wl in wl_plot[ind]:
                z_vel = np.sqrt((c+v)/(c-v)) - 1
                spec_lines.axvline(wl*(1+z_vel), color = element_color_dict[element], lw = 1)
    canvas.draw()

def callback_v(sv):
    #This is the function called when v is updated. Update v parameter and redraw spectral lines. 
    global v
    # print(sv.get())
    try:
        v = float(sv.get())
    except:
        v = 0
    updateLines()


#Input text box to take velocity
sv_v = tk.StringVar()
sv_v.trace("w", lambda name, index, mode, sv=sv_v: callback_v(sv_v))

vtext = tk.Label(button_frame, text = 'v = ')
vtext.grid(row = 3, column = 1)

vbox = tk.Entry(master = button_frame, width=10, textvariable=sv_v)
vbox.insert(0, '%d'%v)
vbox.grid(row = 3, column = 2)

# button that would displays the plot
# plot_button = tk.Button(master = button_frame,
#                     command = lambda: plot_spec(filename, z),
#                     text = "Plot")
# place the button
# into the window
# plot_button.grid(column = 2, row = 2)
# plot_button.grid(row = 4, column = 2)

#add the check boxes to plot lines from different species
for i, specie in enumerate(all_elements):
    toPlots[i] = tk.BooleanVar(False)
    # check_box = tk.Checkbutton(button_frame, text=specie,variable=toPlot, onvalue=1, offvalue=0,
    #             command = lambda: modify_line_to_plot(toPlot, specie))
    element_box[i] = tk.Checkbutton(button_frame, text=specie,variable=toPlots[i], onvalue=1, offvalue=0,
                #   command = lambda: modify_line_to_plot(toPlots[i], specie))
                command = updateLines)
    element_box[i].grid(row = 5+i, column = 1)

# print(element_box)
# print([x.get() for x in toPlots])
# run the gui

##################Final element: 
# ################packing the plot and the matplotlib toolbar into the Tk canvas
# # creating the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas,
                                plotting_frame)
#, pack_toolbar=False)
toolbar.update()
# # placing the toolbar on the Tkinter window
# canvas._tkcanvas.pack()
# placing the canvas on the Tkinter window
toolbar.pack(side=tk.BOTTOM, fill=tk.X)
# canvas.get_tk_widget().pack()

canvas._tkcanvas.pack()

#Run the Tk mainloop
window.mainloop()
