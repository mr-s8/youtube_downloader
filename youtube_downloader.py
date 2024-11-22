import tkinter as tk
import customtkinter as ctk
import os
import time
from yt_dlp import YoutubeDL
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

        """
        # Toggle playlist mode
        self.playlist_mode = ctk.IntVar(value= 0)
        playlist_mode_swith = (ctk.CTkSwitch(master= frame3, text= "Playlist Mode", variable=self.playlist_mode, onvalue=1, offvalue=0))
        playlist_mode_swith.pack(side=tk.BOTTOM)
        """
        
        
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
        yt_video = yt_videos[selected_index]
        listb_text = self.listb.get(selected_index)
        if "video" in yt_video["options"]["format"]:  # Video mode detected
            yt_video["options"] = {
                    'quiet': False,  # Fortschrittsinformationen anzeigen
                    'format': 'bestaudio/best',  # Nur die beste Audioqualität auswählen
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',  # Extrahiert das Audio
                        'preferredcodec': 'mp3',  # Ziel-Audioformat, z. B. mp3, m4a
                        'preferredquality': '192',  # Audioqualität (192 kbps für MP3)
                    }],
                }
            listb_text = listb_text[:-6] + "Audio)"
            self.listb.delete(selected_index)
            self.listb.insert(selected_index, listb_text)
        else:                 #Audio mode detected
            yt_video["options"] = {
                        'quiet': False,  # Fortschrittsinformationen anzeigen
                        'format': 'bestvideo+bestaudio/best',  # Beste Video- und Audioqualität
                    }
            listb_text = listb_text[:-6] + "Video)"
            self.listb.delete(selected_index)
            self.listb.insert(selected_index, listb_text)
            

    def add_item(self):         ## aktuell hier am arbeiten
        """
        adds the youtube video from the entry to the listbox,
        and the youtube object with the mode to the internal list
        """
        item = self.link_entry.get()
        mode = self.format_combo_box.get()
        print("mode")
        print(mode)
        
        if item.startswith(("http", "www", "youtube")):
            title = self.get_video_title(item)
            if mode == "Video":
                options = {
                        'quiet': False,  # Fortschrittsinformationen anzeigen
                        'format': 'bestvideo+bestaudio/best',  # Beste Video- und Audioqualität
                    }
            else:
                options = {
                    'quiet': False,  # Fortschrittsinformationen anzeigen
                    'format': 'bestaudio/best',  # Nur die beste Audioqualität auswählen
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',  # Extrahiert das Audio
                        'preferredcodec': 'mp3',  # Ziel-Audioformat, z. B. mp3, m4a
                        'preferredquality': '192',  # Audioqualität (192 kbps für MP3)
                    }],
                }

            
            
            # if video is part of a playlist (list parameter in url),
            # the whole playlist is going to get downloaded
            playlist = False
            prefix = ""
            if "list" in item:
                prefix = "Playlist containing: "
                playlist = True
            
            yt_videos.append({"link": item, "options": options, "title": title, "playlist": playlist})
            
            self.listb.insert('end', prefix + title + "  |  (" + mode +")")  
            self.link_entry.delete(0, 'end')

    def get_video_title(self, video_url):
        ydl_opts = {
            'quiet': True,  # Keine Ausgaben im Terminal
            'simulate': True,  # Kein Download, nur Metadaten abrufen
            'noplaylist': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)  # Metadaten extrahieren
            return info_dict.get('title', 'Unbekannter Titel')  # Titel abrufen

            

    def clean_filename(self, filename):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        if not filename.strip():
            filename = "unnamed_file"  
        return filename 
    
    def download(self, video_entry, output):
        
        yt_link = video_entry["link"]
        yt_options = video_entry["options"]
        yt_title = video_entry["title"]
        yt_playlist = video_entry["playlist"]
        
        if yt_playlist:
            outtmpl = f'{output}/%(playlist)s/%(title)s.%(ext)s'  # Ordner für Playlist
        else:
            outtmpl = f'{output}/%(title)s.%(ext)s'  # Nur Hauptordner
            
        yt_options["outtmpl"] = outtmpl

        mode_name = "video" if "video" in yt_options["format"] else "audio"
        
    
        self.dbg_console.insert(tk.END, f"Downloading {mode_name} of: '{yt_title}' {" as part of a Playlist" if yt_playlist else ""}...\n")

        try:
            
            with YoutubeDL(yt_options) as ydl:
                ydl.download([yt_link])
            

            self.dbg_console.insert(tk.END, f"Download of: '{yt_title}' {mode_name} {"Playlist" if yt_playlist else ""} complete!\n", "green_tag")

            return 1

        except Exception as e:
            self.dbg_console.insert(tk.END, f"\nAn error occurred: {e}\n")

            return -1  
         

    def download_all(self):
        print("download all called")
        
        """
        downloads all videos in the internal list. downloads three videos at the same time, if the
        multithreading code is not commented out
        """
        global yt_videos
        global folder_created
        global unique_folder
        
        print(yt_videos)

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
        
        self.listb.delete(0, tk.END)
        yt_videos = []




if __name__ == "__main__":
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

----


-delete video from list after download  # sollte passen
-dont allow deleting from list while downloading
-toggle audio video # sollte passen
-fix freeze when add to list, use requests;
- limit length of list text and show progress instead
- show playlist name instead of video name
- zwei toggle buttons für playlist optionen
"""
