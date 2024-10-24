import os
from multiprocessing import Process
import threading
import pyaudio
import wave
import time
import numpy as np

class sp(Process):
    def __init__(self, conn):
        self.conn = conn
        print("hi")
        #Process.__init__(self)
        self.run()
    
    def playback(self, filename: str, sbStream: pyaudio, out_index: int, volume = 0.15):
        try:
            with wave.open(f'Sounds/{filename}.wav', 'rb') as wf:
                        print(f"Playing {filename}...")
                        # Define callback for playback (1)
                        def callback(in_data, frame_count, time_info, status):
                            data = wf.readframes(frame_count)

                            volume_factor = volume
                            audio_data = np.frombuffer(data, dtype=np.int16)
                            # Reduce the volume
                            audio_data = (audio_data * volume_factor).astype(np.int16)
                            # Convert numpy array back to byte data
                            data = audio_data.tobytes()

                            # If len(data) is less than requested frame_count, PyAudio automatically
                            # assumes the stream is finished, and the stream stops.
                            return (data, pyaudio.paContinue)

                        # Open stream using callback (3)
                        stream = sbStream.open(format=sbStream.get_format_from_width(wf.getsampwidth()),
                                        channels=wf.getnchannels(),
                                        rate=wf.getframerate(),
                                        output=True,
                                        stream_callback=callback,
                                        output_device_index=out_index
                                        )

                        # Wait for stream to finish (4)
                        while stream.is_active():
                            time.sleep(0.1)
                            #await asyncio.sleep(0.1)

                        stream.close()
        except:
            print("Uh-oh")

    def run(self):
        print("hi again")
        sounds = pyaudio.PyAudio()
        print(f"Hi, I'm the sound player delivering your sick sounds! My pid is {os.getpid()} and my parent is {os.getppid()}.\n")

        message = ""
        while not self.conn.poll() or message != "TERMINATE":
            message = self.conn.recv()
            if message == "TERMINATE":
                break
            
            else:
                name = message[:message.rfind("/")]
                volume = message[message.rfind("/") + 1:-1]
                print(name + "|" + volume)
                toMe = threading.Thread(target=self.playback, args=(name, sounds, 4, (float(volume) / 100)), daemon=True)
                toThem = threading.Thread(target=self.playback, args=(name, sounds, 5, (float(volume) / 100)), daemon= True)
                toMe.start()
                toThem.start()