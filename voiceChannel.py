import os
from multiprocessing import Process
import pyaudio
import numpy as np
import time

class vc(Process):
    def __init__(self, conn):
        # When this method is called by the main class starting a process, it is still the same process as the main. Only after Process.__init__() is called does it seperate.
        # Initialize as a seperate process, and will automatically look for and call a method called run.
        self.parentid = os.getppid()
        self.conn = conn
        self.run()
        #Process.__init__(self)

    # There needs to be a method called run. It is what the process will do after initializing.

    def iostream(self, p: pyaudio = pyaudio.PyAudio(), out_index: int = 5, in_index: int = 1):   
        # Open stream using callback to stream voice from input to output
        while(True):
            def callback(in_data, frame_count, time_info, status):
                input_data = np.frombuffer(in_data, dtype=np.int16)
                #input_data = (input_data * 1.0).astype(np.int16)
                return(input_data.tobytes(), pyaudio.paContinue)
            
            stream = p.open(format=p.get_format_from_width(4),
                            channels=2,
                            rate=48000,
                            output=True,
                            input=True,
                            output_device_index= out_index,
                            input_device_index= in_index,
                            stream_callback=callback
                            )
            while not self.conn.poll():
                time.sleep(0.1)
            message = self.conn.recv()
            if message == "TERMINATE":
                break
            #print(f"Message {message} received! Muting.")
            stream.close()
            #p.terminate()
            
            while not self.conn.poll():
                time.sleep(0.1)

            message = self.conn.recv()
            if message == "TERMINATE":
                break
            #print(f"Message {message} received! Unmuting.")

        # Wait for user to finish using the stream.
        # while stream.is_active():
        #     time.sleep(0.1)
        #time.sleep(5) # For testing until a way to stop and start the stream is made.


        # Close the stream and release resources.
        stream.close()
        p.terminate()
        print("Succesfully Closed Voice channel.\n")

    def run(self):
        print(f"Hi, I'm the voice channel carrying your beautiful voice! My pid is {os.getpid()} and my parent is {os.getppid()}.\n")
        self.iostream()