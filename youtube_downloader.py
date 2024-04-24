import tkinter as tk
import customtkinter as ctk
import os
import pytube
import shutil
import subprocess
import time
from pytube import YouTube
from pytube import Playlist
from pytube.innertube import _default_clients
import threading


class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):

        super().__init__()

        # App frame
        self.title("YouTube Downloader")
        self.geometry("1000x900")
        self.resizable(False, False)

        # SySettings
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Start gui
        self.setup_ui()

    def setup_ui(self):

        # UI
        title = ctk.CTkLabel(master = self, text = "Download videos or audio from YouTube", font=("Helvetica", 16, "bold"))
        title.pack(padx = 10, pady = (5,80))

        # Input
        frame1 = ctk.CTkFrame(self)
        frame1.pack(pady=10,)

        self.link_entry = ctk.CTkEntry(master= frame1, width=300)
        self.link_entry.pack(padx = 5, side = tk.LEFT)

        format_values = ["Video", "Audio"]
        format_value = ctk.StringVar(value= format_values[0])
        self.format_combo_box = ctk.CTkComboBox(master=frame1, values=format_values, state="readonly", variable= format_value)
        self.format_combo_box.pack(padx= 5, side= tk.LEFT)

        add_button = ctk.CTkButton(master = frame1, text="Add", width= 28, command= self.add_item)      
        add_button.pack(padx = 5, side = tk.LEFT)

        # Frame with Listbox and buttons
        frame2 = ctk.CTkFrame(self)
        frame2.pack(pady=10)

        listbox_frame = ctk.CTkFrame(frame2)
        listbox_frame.pack(side=tk.LEFT)

        self.listb = tk.Listbox(master=listbox_frame, selectmode=tk.SINGLE, background="#1d1e1e", height=20, width=80, fg="white")
        self.listb.pack(pady=10)

        frame3 = ctk.CTkFrame(frame2)
        frame3.pack(pady=10, padx=10, side= tk.LEFT)

        # Buttons to edit items inside listbox
        delete_selected_button = ctk.CTkButton(frame3, text="Delete Selected", command=self.delete_selected)
        delete_selected_button.pack(side=tk.TOP, pady=5)

        delete_all_button = ctk.CTkButton(frame3, text="Delete All", command=self.delete_all)
        delete_all_button.pack(side=tk.TOP, pady=5)

        toggle_audio_video_button = ctk.CTkButton(frame3, text="Toggle Audio/Video", command=self.toggle_video_audio)
        toggle_audio_video_button.pack(side=tk.TOP, pady=5)

        # Toggle playlist mode
        self.playlist_mode = ctk.IntVar(value= 0)
        playlist_mode_swith = (ctk.CTkSwitch(master= frame3, text= "Playlist Mode", variable=self.playlist_mode, onvalue=1, offvalue=0))
        playlist_mode_swith.pack(side=tk.BOTTOM)

        # Download all button
        dl_button = ctk.CTkButton(master = self, text="Download all", command= lambda: threading.Thread(target= self.download_all).start())    # run download_all function in a different thread, 
        dl_button.pack(pady = 10)                                                                                                                   #so the gui doesnt freeze when we wait for the downloads to finish

        # Debug console
        self.dbg_console = ctk.CTkTextbox(master = self, width= 800, height=300, state=tk.NORMAL)
        self.dbg_console.pack(pady=10)
        self.dbg_console.tag_config("red_tag", foreground="red")
        self.dbg_console.tag_config("green_tag", foreground="green")

    # Functions
    
    def delete_selected(self):
        """
        deletes the selected element in the listbox
        """
        selected_index = self.listb.curselection()
        if selected_index:
            self.listb.delete(selected_index[0])
            del yt_videos[selected_index[0]]   

    def delete_all(self):
        """
        delets all elements in the listbox
        """
        global yt_videos
        self.listb.delete(0, tk.END)
        yt_videos = []  

    def toggle_video_audio(self):
        selected_index = self.listb.curselection()
        if not selected_index:
            return
        selected_index = selected_index[0]
        yt_tuple = yt_videos[selected_index]
        listb_text = self.listb.get(selected_index)
        if yt_tuple[1] == 0:  # Video mode detected
            yt_videos[selected_index] = (yt_tuple[0],1)
            listb_text = listb_text[:-6] + "Audio)"
            self.listb.delete(selected_index)
            self.listb.insert(selected_index, listb_text)
        else:                 #Audio mode detected
            yt_videos[selected_index] = (yt_tuple[0],0)
            listb_text = listb_text[:-6] + "Video)"
            self.listb.delete(selected_index)
            self.listb.insert(selected_index, listb_text)
            

    def add_item(self):
        """
        adds an the youtube video from the entry to the listbox,
        and the youtube object with the mode to the internal list
        """
        item = self.link_entry.get()
        mode = self.format_combo_box.get()
        if item.startswith(("http", "www", "youtube")):
            if self.playlist_mode.get() == 0:
                yt_obj = YouTube(item)
                yt_videos.append((yt_obj, 0 if mode == "Video" else 1))
                self.listb.insert('end', yt_obj.title + "  |  (" + mode +")")
                self.link_entry.delete(0, 'end')
            else:
                if not "&list=" in item:
                    self.dbg_console.insert(tk.END, "Video is not part of a playlist!", "red_tag")
                else:
                    playlist = Playlist(item)
                    for i in playlist.videos:
                        yt_videos.append((i, 0 if mode == "Video" else 1))
                        self.listb.insert('end', i.title + "  |  (" + mode +")")
                    self.link_entry.delete(0, 'end')



    def clean_filename(self, filename):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        if not filename.strip():
            filename = "unnamed_file"  
        return filename 
    
    def download(self, video_entry, output):

        """
        Downloads the video from the YouTube object in the video_entry tuple.
        If the highest resolution available is not above 720p, we can use a progressive
        stream, which conatins both audio and video, to download the video.
        If not, we first download the video and then call the function again to download the audio.
        We then merge the two together with ffmpeg.
        """

        yt_obj = video_entry[0]
        title = self.clean_filename(yt_obj.title) # eliminate invalid chars in filename
        mode = video_entry[1]
        mode_name = "video" if mode == 0 else "audio"
        need_to_merge_audio = False

        self.dbg_console.insert(tk.END, f"Downloading {mode_name} of: '{title}'...\n")

        try:
            streams = yt_obj.streams
            if mode == 0:               # if we want to download video
                if len(streams.filter(progressive= False, res= "1080p", file_extension= "mp4")) == 0: # if there is no better stream than 720p, use the progressive stream
                    stream = streams.get_highest_resolution()
                else:
                    stream = streams.filter(progressive= False, res="1080p", file_extension= "mp4").first() # if there is a full hd stream available, get the video only stream
                    need_to_merge_audio = True                                                              # and later get the audio
                ending = ".mp4"
            else:                       # if we want to download audio
                stream = streams.filter(only_audio=True).first()
                ending = ".mp3"

            stream.download(output_path= output, filename= (title+ending))
            video_location = output+"/"+title+ending    
            if need_to_merge_audio:     # Get audio if needed

                #print(f"Getting audio for {title}, to merge with high res video.")
                self.dbg_console.insert(tk.END, f"Getting audio for: '{title}', to merge with high res video.\n")

                tmp_folder = "temp_" + str(time.time()) 
                os.makedirs(tmp_folder)
                mp3_location = self.download((yt_obj, 1), "./" + tmp_folder)
                final_path = "./"+tmp_folder + "/" +title + ending
                self.merge_audio_video(video_location, mp3_location, final_path)   # old version of merging with moviepy    end_path = "./"+tmp_folder and use video_location returned by mergefunction
                os.remove(video_location)
                shutil.move(final_path, output)
                time.sleep(2)
                shutil.rmtree(tmp_folder)   

            self.dbg_console.insert(tk.END, f"Download of: '{title}' {mode_name} complete!\n", "green_tag")

            return video_location

        except pytube.exceptions.AgeRestrictedError:  # if video is age restricted, use oauth

            self.dbg_console.insert(tk.END, f"{title} age restricted! Trying again with OAuth! Check console, you might need to authenticate\n", "red_tag")

            new_yt_obj = YouTube(yt_obj.watch_url, use_oauth=True, allow_oauth_cache=True)
            return self.download((new_yt_obj, mode), output)

        except Exception as e:
            self.dbg_console.insert(tk.END, f"\nAn error occurred: {e}\n")

            return -1  
         
    def merge_audio_video(self, video_file, audio_file, output_file):
        """
        merge the audio and video and save it to the ouput_file location
        """
        command = ['ffmpeg', '-i', audio_file, '-i', video_file, '-c', 'copy', output_file]
        subprocess.run(command) 

    def download_all(self):
        """
        downloads all videos in the internal list. downloads three videos at the same time, if the
        multithreading code is not commented out
        """
        global folder_created
        global unique_folder
        if not folder_created:  # one folder per session; problem if folder is deleted while running
            unique_folder = str(time.time()) 
            os.makedirs(unique_folder)  
            folder_created = True
        """
        #####  without multithreading the debug console only prints after every download
        
        # No multithreading:
        for i in yt_videos:
            self.download(i, unique_folder) 
        
        #####
        """
        
        #######
        # Multithreading -> 3 downloads at a time:

        length = len(yt_videos)
        for i in range(0, len(yt_videos), 3): 
    
            if i + 2 < length:
                download_thread1 = threading.Thread(target=lambda video = yt_videos[i]: self.download(video, unique_folder))
                download_thread2 = threading.Thread(target=lambda video = yt_videos[i+1]: self.download(video, unique_folder))
                download_thread3 = threading.Thread(target=lambda video = yt_videos[i+2]: self.download(video, unique_folder))
                
                download_thread1.start()
                download_thread2.start()
                download_thread3.start()

                download_thread1.join()
                download_thread2.join()
                download_thread3.join()

            else:
                # Handle the case when there are fewer than three elements remaining
                remaining_elements = length - i
                if remaining_elements == 1:
                    download_thread1 = threading.Thread(target=lambda video = yt_videos[i]: self.download(video, unique_folder))
                    download_thread1.start()
                    download_thread1.join()
                elif remaining_elements == 2:
                    download_thread1 = threading.Thread(target=lambda video = yt_videos[i]: self.download(video, unique_folder))
                    download_thread2 = threading.Thread(target=lambda video = yt_videos[i+1]: self.download(video, unique_folder))
                    download_thread1.start()
                    download_thread2.start()
                    download_thread1.join()
                    download_thread2.join()
        ########
        



if __name__ == "__main__":
    
    # Configuration changes
    _default_clients["ANDROID_CREATOR"]["context"]["client"]["clientVersion"] = '23.30.100'     # choosing newer versions prevents a bug i think
    _default_clients["ANDROID_CREATOR"]["context"]["client"]["androidSdkVersion"] = 33
    _default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]  #  with android fix age restriction loop bug but then we have 403 error | with android creator we have less streams...
    # Backend variables
    yt_videos = []
    unique_folder = ""
    folder_created = False
    # Start app
    app = YouTubeDownloaderApp()
    app.mainloop()


"""
To do:
- get links from textfile
- download playlist all at once
- use multithreading (one thread for gui and one for each download)                             ✓
- show thumbnail when adding video
- show progressbar
- add other formats than mp4 and mp3
- allow user to choose resolution
- show debug messages to a textbox in the gui (also because multithreading spams the console)  ✓
- disable new input in some cases to prevent unwanted behavior
- add button to toggle audio/video mode
To fix:
- with the ANDROID_CREATOR client, in some cases, there is no 1080p stream, even though there should be one,
    using the ADROID client could fix this. it also fixes a loop bug with age restricted videos, but leads to 403 errors
    very often; how can I eliminate all these bugs?

"""
