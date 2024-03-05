<div align="center">
  <p>
    <a href="https://github.com/mr-s8/youtube_downloader/blob/main/images/download_logo.png"><img src="https://github.com/mr-s8/youtube_downloader/blob/main/images/download_logo.png" width="200" alt="pytube logo" /></a>
  </p>
</div>



# youtube_downloader
A GUI made with Tkinter, that allows the user to download YouTube videos, even age restricted ones.

# To Do
Features to add:
- get links from textfile
- download playlist all at once
- use multithreading (one thread for gui and one for each download)                             ✓
- show thumbnail when adding video
- show progressbar
- add other formats than mp4 and mp3
- allow user to choose resolution
- show debug messages to a textbox in the gui (also because multithreading spams the console)  ✓

To fix:
- with the ANDROID_CREATOR client, in some cases, there is no 1080p stream, even though there should be one,
    using the ADROID client could fix this, it fixes a loop bug with age restricted videos, but leads to 403 errors
    very often; how can I eliminate all these bugs?

## GUI
<div align="center">
  <p>
    <a href="https://github.com/mr-s8/youtube_downloader/blob/main/images/youtube_downloader_gui_tested.png"><img src="https://github.com/mr-s8/youtube_downloader/blob/main/images/youtube_downloader_gui_tested.png"       
    width="800" alt="pytube logo" /></a>
    <a href="https://github.com/mr-s8/youtube_downloader/blob/main/images/youtube_downloader_gui.png"><img src="https://github.com/mr-s8/youtube_downloader/blob/main/images/youtube_downloader_gui.png" width="800" alt="pytube 
    logo" /></a>
  </p>
</div>
