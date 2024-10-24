import os
import tkinter as tk
from multiprocessing import Process

class gui(Process):
    def __init__(self, ioConn, spConn):
        self.ioConn = ioConn
        self.spConn = spConn
        self.run()
        #Process.__init__(self)

    def change(self, right: bool):
        global currPage
        global volume

        names = os.listdir('./Sounds')
        maxPages = (len(names) // 9) + 1 # if len(names) // 9 > 0 else 1

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
                    buttons[i + (j * 3)].configure(text=f"{names[start + i + j * 3][:-4]}", command= lambda this = buttons[i + (j * 3)]: self.spConn.send(this['text'] + "/" + str(volume)))
                except:
                    buttons[i + (j * 3)].configure(text="", command=lambda: None)
    
    def volumeset(self, v):
        global volume
        volume = v

    def run(self):
        global root
        root= tk.Tk()

        root.geometry("500x500")

        root.title("Soundboard")

        titleLabel = tk.Label(root, text="Sounds", font=('Arial', 18))

        volumeLabel = tk.Label(root, text="Volume", font=('Arial', 12))
        
        global volume
        volumeslider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=lambda: self.volumeset(v=volumeslider.get()))
        volumeslider.set(50)
        volume = 50

        #stopButton = tk.Button(text="☐", font=('Arial', 10), command=lambda: stopAll())

        muteButton = tk.Button(text="Mute", font=('Arial', 10), command=lambda: self.ioConn.send("MUTE"))

        buttonframe = tk.Frame(root)
        buttonframe.columnconfigure(0, weight=1)
        buttonframe.columnconfigure(1, weight=1)
        buttonframe.columnconfigure(2, weight=1)

        global buttons
        global playQueue
        buttons = [tk.Button(buttonframe, text="Null", font=('Arial', 10)) for i in range(9)]
        playQueue = list()

        names = os.listdir('./Sounds')
        global currPage
        currPage = 1
        rightButton = tk.Button(text="->", font=('Arial', 10), command=lambda: self.change(True))
        leftButton = tk.Button(text="<-", font=('Arial', 10), command=lambda: self.change(False))

        for i in range(3):
            for j in range(3):
                buttons[i + (j * 3)].grid(column=i, row=j, sticky=tk.W+tk.E)
                buttons[i + (j * 3)].configure(text=f"{names[i + (j * 3)][:-4]}", command= lambda this = buttons[i + (j * 3)]: self.spConn.send(this['text'] + "/" + str(volume)))
                
        titleLabel.pack()
        buttonframe.pack(fill=tk.BOTH, padx=20, pady=20,side=tk.TOP)
        rightButton.pack(padx=30, side=tk.RIGHT)
        #stopButton.pack(side=tk.TOP)
        leftButton.pack(padx=30, side=tk.LEFT)
        volumeslider.pack(side=tk.BOTTOM)
        volumeLabel.pack(side=tk.BOTTOM)
        muteButton.pack()

        root.columnconfigure(1, weight = 1)
        root.rowconfigure(1, weight = 1)

        root.mainloop()
        self.spConn.send("TERMINATE")
        self.ioConn.send("TERMINATE")
        print(f"Gui closed. My pid is {os.getpid()}")