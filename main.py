import os
import sys
import voiceChannel
import soundPlayer
import guiDisplay
import multiprocessing
import pyaudio
import json

# This line is needed to make sure this program works on Windows devices.
if __name__ == "__main__":

    setup = pyaudio.PyAudio()

    guiIOConn, child_conn = multiprocessing.Pipe()
    guiSpConn, stop_conn = multiprocessing.Pipe()

    input_device: int = None
    output_device: int = None
    virtual_cable: int = None

    data_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)), "devices.json")

    try:
        # Try to use saved values
        with open(data_path, "r") as f:
            devices = json.load(f)
            f.close()

        num_devices = setup.get_default_host_api_info()["deviceCount"]

        for index in range(num_devices):

            if setup.get_device_info_by_host_api_device_index(0, index).get('name') == devices.get("input_device"):
                input_device = index

            else:
                if setup.get_device_info_by_host_api_device_index(0, index).get('name') == devices.get("output_device"):
                    output_device = index

                if setup.get_device_info_by_host_api_device_index(0, index).get('name') == devices.get("virtual_cable"):
                    virtual_cable = index

        if (input_device == None or output_device == None or virtual_cable == None):
            # Device wasn't found on computer, set defaults
            raise(FileNotFoundError)

        print("Read the saved data successfully.")

    except(FileNotFoundError):
        # No file exists, or error loading. Set defaults and virtual cable to speakers
        print("One or more saved devices missing. Automatically replacing missing with system defaults.")

        input_device = setup.get_default_input_device_info()["index"] if not input_device else input_device
        output_device = setup.get_default_output_device_info()["index"] if not output_device else output_device
        virtual_cable = setup.get_default_output_device_info()["index"] if not virtual_cable else virtual_cable

        devices = {
            "input_device": setup.get_device_info_by_host_api_device_index(0, input_device).get('name'),
            "output_device": setup.get_device_info_by_host_api_device_index(0, output_device).get('name'),
            "virtual_cable": setup.get_device_info_by_host_api_device_index(0, virtual_cable).get('name')
        }

        # Save the defaults
        with open(data_path, "w") as f:
            json.dump(devices, f)
            f.close()
    

    
    p = multiprocessing.Process(target=voiceChannel.Vc, args=(child_conn, input_device, virtual_cable))
    p2 = multiprocessing.Process(target=soundPlayer.Sp, args=(stop_conn,))
    p3 = multiprocessing.Process(target=guiDisplay.MainGui, args=(guiIOConn, guiSpConn, [input_device, output_device, virtual_cable]))
    
    setup.terminate()

    p.start()
    p2.start()
    p3.start()

    p2.join()
    print("Looks like the sound player is done! Now to wait for the vc...")
    p.join()
    print("Looks like the voice channel is done! Now to wait for the gui...")
    p3.join()
    print(f"Everyone's all done! I'm the main and my pid is {os.getpid()}.")