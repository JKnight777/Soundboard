import os
from multiprocessing import Process
import pyaudio
import numpy as np
import time

class Vc(Process):
    def __init__(self, conn, input_device: int, virtual_cable: int):
        # When this method is called by the main class starting a process, it is still the same process as the main. Only after Process.__init__() is called does it seperate.
        # Initialize as a seperate process, and will automatically look for and call a method called run.
        
        self.parentid = os.getppid()
        self.conn = conn
        self.input_device = input_device
        self.virtual_cable = virtual_cable
        self.run()
        #Process.__init__(self)

    # There needs to be a method called run. It is what the process will do after initializing.
    # out_index needs to be the index of the Virtual Cable Input
    def iostream(self):   
        # Open stream using callback to stream voice from input to output
        p = pyaudio.PyAudio()
        while(True):
            def callback(in_data, frame_count, time_info, status):
                input_data = np.frombuffer(in_data, dtype=np.int16)
                #input_data = (input_data * volume).astype(np.int16)
                return(input_data.tobytes(), pyaudio.paContinue)

            
            stream = p.open(format=p.get_format_from_width(4),
                            channels=2,
                            rate=48000,
                            output=True,
                            input=True,
                            output_device_index= self.virtual_cable,
                            input_device_index= self.input_device,
                            stream_callback=callback
                            )
            while not self.conn.poll():
                time.sleep(0.1)
            message = self.conn.recv()
            if message == "TERMINATE":
                break
            elif message != "MUTE":
                stream.close()
                self.input_device = message[0]
                self.virtual_cable = message[1]
                print("IOStream updated.")
                continue
            #print(f"Message {message} received! Muting.")
            stream.close()
            #p.terminate()
            
            while not self.conn.poll():
                time.sleep(0.1)

            message = self.conn.recv()
            if message == "TERMINATE":
                break
            elif message != "MUTE":
                stream.close()
                self.input_device = message[0]
                self.virtual_cable = message[1]
                print("IOStream updated.")
                continue
            #print(f"Message {message} received! Unmuting.")

        # Close the stream and release resources.
        stream.close()
        p.terminate()
        print("Succesfully Closed Voice channel.\n")

    def run(self):
        print(f"Hi, I'm the voice channel carrying your voice! My pid is {os.getpid()} and my parent is {os.getppid()}.\n")
        self.iostream()