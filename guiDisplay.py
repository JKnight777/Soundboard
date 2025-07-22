import os
import sys
import pyaudio
import json
import tkinter as tk
from tkinter import ttk
from multiprocessing import Process

global volume
    
class MainGui(Process):

    def __init__(self, ioConn, spConn, devices):
        self.ioConn = ioConn
        self.spConn = spConn
        self.input_device = devices[0]
        self.output_device = devices[1]
        self.virtual_cable = devices[2]
        self.base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self.run()
        #Process.__init__(self)
    
    def setAndSave(self, i: int, o: int, v: int):
        pya = pyaudio.PyAudio()
        self.input_device = i
        self.output_device = o
        self.virtual_cable = v

        devices = {
            "input_device": pya.get_device_info_by_host_api_device_index(0, self.input_device).get('name'),
            "output_device": pya.get_device_info_by_host_api_device_index(0, self.output_device).get('name'),
            "virtual_cable": pya.get_device_info_by_host_api_device_index(0, self.virtual_cable).get('name')
        }

        # Save the updates
        data_path = os.path.join(self.base_path, "devices.json")

        with open(data_path, "w") as f:
            json.dump(devices, f)
            f.close()

        pya.terminate()

        # Reset the voice Channel
        self.ioConn.send([self.input_device, self.virtual_cable])

    def openFolder(self):
        folder_path = os.path.join(self.base_path, 'Sounds')
        print(folder_path)
        
        if os.name == 'nt':  # Check if the OS is Windows
            os.system(f"explorer.exe {folder_path}")
        elif os.uname().sysname == 'Darwin':  # Check if the OS is macOS
            os.system(f"open {folder_path}")
        else:  # Assume Linux-like system
            os.system(f"xdg-open {folder_path}")

    def settings(self):
        pa = pyaudio.PyAudio()

        modal = tk.Toplevel(root)
        modal.title("Settings")

        modal.geometry("300x400")

        icon = tk.PhotoImage(file=os.path.join(self.base_path, 'settingsIcon.png'))
        modal.iconphoto(False, icon)

        label = ttk.Label(modal, text="Please select your preferred audio devices.")

        # Used to update the json
        saveButton = ttk.Button(modal, text="Save", command=lambda: self.setAndSave(input_indexes[input_selection.current()], output_indexes[output_selection.current()], output_indexes[virtual_selection.current()]))
        
        #Used to access folder where Sounds is located.
        openButton = ttk.Button(modal, text="Open Sounds Folder", command=lambda: self.openFolder())

        li = ttk.Label(modal, text="Input Device:")
        
        lo = ttk.Label(modal, text="Output Device:")

        lv = ttk.Label(modal, text="Virtual Cable:")

        i = tk.StringVar()
        o = tk.StringVar()
        v = tk.StringVar()

        input_selection = ttk.Combobox(modal, width=35, state='readonly', textvariable= i)
        output_selection = ttk.Combobox(modal, width=35, state='readonly', textvariable= o)
        virtual_selection = ttk.Combobox(modal, width=35, state='readonly', textvariable= v)

        #Populate the comboboxes and find which values are currently in use
        num_devices = pa.get_default_host_api_info()["deviceCount"]

        inputs = []
        input_indexes = []
        outputs = []
        output_indexes = []

        curri = 0
        curro = 0
        currv = 0

        for i in range(num_devices):
            if (pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                inputs.append(pa.get_device_info_by_host_api_device_index(0, i).get('name'))
                input_indexes.append(i)

                if i == self.input_device:
                    curri = len(input_indexes) - 1

            elif (pa.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                outputs.append(pa.get_device_info_by_host_api_device_index(0, i).get('name'))
                output_indexes.append(i)

                if i == self.output_device:
                    curro = len(output_indexes) - 1
                
                if i == self.virtual_cable:
                    currv = len(output_indexes) - 1
        
        # Set and display
        input_selection['values'] = inputs
        input_selection.current(curri)

        output_selection['values'] = outputs
        output_selection.current(curro)

        virtual_selection['values'] = outputs
        virtual_selection.current(currv)

        openButton.pack(pady=10)

        label.pack(pady=10)

        li.pack(pady=10)
        input_selection.pack(pady=5)

        lo.pack(pady=10)
        output_selection.pack(pady=5)

        lv.pack(pady=10)
        virtual_selection.pack(pady=5)

        saveButton.pack(pady=10)
    
        pa.terminate()

        # Make it modal
        modal.transient(root)    # Keep it on top of the main window
        modal.grab_set()         # Make it grab all input
        root.wait_window(modal)  # Pause main window until this one is closed

    def change(self, right: bool):
        global currPage
        global thisFolder

        names = os.listdir(thisFolder + '/Sounds')
        maxPages = (len(names) // 9) + 1

        if right:
            currPage = currPage + 1 if currPage < maxPages else 1
        else:
            currPage = currPage - 1 if currPage > 1 else maxPages

        print(f"{currPage} out of {maxPages}")
        start = (currPage - 1) * 9
        for i in range(3):
            for j in range(3):
                buttons[i + (j * 3)].grid(column=i, row=j, sticky=tk.W+tk.E)
                try:
                    buttons[i + (j * 3)].configure(text=f"{names[start + i + j * 3][:-4]}", command= lambda this = buttons[i + (j * 3)]: self.spConn.send([this['text'], volume.get(), self.output_device, self.virtual_cable]))
                except:
                    buttons[i + (j * 3)].configure(text="", command=lambda: None)
    

    def run(self):
        global root
        root= tk.Tk()

        root.geometry("500x500")

        root.title("Soundboard")

        icon = tk.PhotoImage(file=os.path.join(self.base_path, 'mainIcon.png'))
        root.iconphoto(False, icon)

        titleLabel = tk.Label(root, text="Sounds", font=('Arial', 18))

        volumeLabel = tk.Label(root, text="Volume", font=('Arial', 12))
        
        global volume
        volume = tk.IntVar()
        volumeslider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, variable=volume)
        volumeslider.set(50)
        volume.set(50)

        #stopButton = tk.Button(text="☐", font=('Arial', 10), command=lambda: stopAll())

        muteButton = tk.Button(text="Mute", font=('Arial', 10), command=lambda: self.ioConn.send("MUTE"))
        settingsButton = tk.Button(text="Settings", font=('Arial', 10), command=lambda: self.settings())

        buttonframe = tk.Frame(root)
        buttonframe.columnconfigure(0, weight=1)
        buttonframe.columnconfigure(1, weight=1)
        buttonframe.columnconfigure(2, weight=1)

        global buttons
        global playQueue
        buttons = [tk.Button(buttonframe, text="Null", font=('Arial', 10)) for i in range(9)]
        playQueue = list()

        global thisFolder
        thisFolder = os.path.dirname(os.path.abspath(__file__))
        names = os.listdir(thisFolder + '/Sounds')
        global currPage
        currPage = 1
        rightButton = tk.Button(text="->", font=('Arial', 10), command=lambda: self.change(True))
        leftButton = tk.Button(text="<-", font=('Arial', 10), command=lambda: self.change(False))

        for i in range(3):
            for j in range(3):
                buttons[i + (j * 3)].grid(column=i, row=j, sticky=tk.W+tk.E)
                buttons[i + (j * 3)].configure(text=f"{names[i + (j * 3)][:-4]}", command= lambda this = buttons[i + (j * 3)]: self.spConn.send([this['text'], volume.get(), self.output_device, self.virtual_cable]))
                
        titleLabel.pack()
        buttonframe.pack(fill=tk.BOTH, padx=20, pady=20,side=tk.TOP)
        rightButton.pack(padx=30, side=tk.RIGHT)
        #stopButton.pack(side=tk.TOP)
        leftButton.pack(padx=30, side=tk.LEFT)
        volumeslider.pack(side=tk.BOTTOM)
        volumeLabel.pack(side=tk.BOTTOM)
        muteButton.pack()
        settingsButton.pack()

        root.columnconfigure(1, weight = 1)
        root.rowconfigure(1, weight = 1)

        root.mainloop()
        self.spConn.send("TERMINATE")
        self.ioConn.send("TERMINATE")
        print(f"Gui closed. My pid is {os.getpid()}")