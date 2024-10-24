import os
import voiceChannel
import soundPlayer
import guiDisplay
import multiprocessing

# This line is needed to make sure this program works on Windows devices.
if __name__ == "__main__":
    guiIOConn, child_conn = multiprocessing.Pipe()
    guiSpConn, stop_conn = multiprocessing.Pipe()
    
    p = multiprocessing.Process(target=voiceChannel.vc, args=(child_conn,))
    p2 = multiprocessing.Process(target=soundPlayer.sp, args=(stop_conn,))
    p3 = multiprocessing.Process(target=guiDisplay.gui, args=(guiIOConn, guiSpConn))
    

    p.start()
    p2.start()
    p3.start()
    p2.join()
    print("Looks like the sound player is done! Now to wait for the vc...")
    p.join()
    print("Looks like the voice channel is done! Now to wait for the gui...")
    p3.join()
    print(f"All done! I'm the main and my pid is {os.getpid()}.")