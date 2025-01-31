#!/usr/bin/env python3
import feedparser
from datetime import datetime
import humanize
import webbrowser
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
from urllib.request import urlopen
import threading
import os

CHANNEL_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id=UCJdmdUp5BrsWsYVQUylCMLg"
MAX_ITEMS = 15
THUMBNAIL_SIZE = (200, 112)
GITHUB_URL = "https://github.com/elevation75/chvilist"
COLORS = {
    'background': '#2D2D2D',
    'primary': '#383838',
    'secondary': '#404040',
    'accent': '#FF4D4D',
    'text': '#FFFFFF',
    'highlight': '#6D6D6D'
}

class AboutWindow(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")
        self.geometry("400x250")
        self.configure(background=COLORS['background'])
        self.resizable(False, False)
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self, style='VideoFrame.TFrame')
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="YouTube RSS Viewer", 
                font=('Roboto', 14, 'bold'), style='Custom.TLabel').pack(pady=10)
        
        info_text = (
            "Version: 0.1\n"
            "Author: elevation75\n"
            "Description: A smart method to have latest videos posted\n"
            "for Erik Dubois' channel"
        )
        ttk.Label(main_frame, text=info_text, style='Custom.TLabel').pack(pady=5)
        
        github_frame = ttk.Frame(main_frame, style='VideoFrame.TFrame')
        github_frame.pack(pady=15)
        ttk.Label(github_frame, text="More on GitHub Repository:", style='Custom.TLabel').pack(side=LEFT)
        ttk.Button(github_frame, text="Open", command=lambda: webbrowser.open(GITHUB_URL),
                 style='Accent.TButton').pack(side=LEFT, padx=10)
        
        ttk.Button(main_frame, text="Close", command=self.destroy,
                 style='Nav.TButton').pack(pady=10)

class StyledVideoFrame(ttk.Frame):
    def __init__(self, parent, video, thumbnail_url):
        super().__init__(parent, style='VideoFrame.TFrame')
        self.video = video
        self.thumbnail_url = thumbnail_url
        self.create_widgets()
        self.load_thumbnail()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        thumbnail_container = ttk.Frame(self, style='Thumbnail.TFrame')
        thumbnail_container.grid(row=0, column=0, rowspan=2, padx=(10, 15), pady=10)
        self.thumbnail_label = ttk.Label(thumbnail_container, background=COLORS['primary'])
        self.thumbnail_label.pack(padx=3, pady=3)

        title_label = ttk.Label(self, text=self.video['title'], wraplength=450, 
                              font=('Roboto', 11, 'bold'), foreground=COLORS['text'],
                              style='Custom.TLabel')
        title_label.grid(row=0, column=1, sticky="nw", padx=(0, 10), pady=(10, 0))

        bottom_frame = ttk.Frame(self, style='VideoFrame.TFrame')
        bottom_frame.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
        
        ttk.Label(bottom_frame, text=self.video['date'], 
                font=('Roboto', 9), foreground='#CCCCCC').pack(side="left", padx=5)
        
        self.watch_btn = ttk.Button(bottom_frame, text="▶ Watch Now", 
                                  command=self.open_video, style='Accent.TButton')
        self.watch_btn.pack(side="right", ipadx=10, ipady=3)

    def load_thumbnail(self):
        def fetch_image():
            try:
                with urlopen(self.thumbnail_url) as response:
                    image_data = response.read()
                image = Image.open(BytesIO(image_data))
                image.thumbnail(THUMBNAIL_SIZE)
                photo = ImageTk.PhotoImage(image)
                self.thumbnail_label.config(image=photo)
                self.thumbnail_label.image = photo
            except Exception as e:
                print(f"Error loading thumbnail: {e}")

        threading.Thread(target=fetch_image, daemon=True).start()

    def open_video(self):
        self.watch_btn.config(text="Opening...")
        webbrowser.open(self.video['link'])
        self.after(2000, lambda: self.watch_btn.config(text="▶ Watch Now"))

class ModernYTViewer(Tk):
    def __init__(self):
        super().__init__()
        self.title("Erik Dubois YouTube Viewer")
        self.geometry("900x700+100+100")
        self.configure(background=COLORS['background'])
        self.setup_styles()
        self.create_widgets()
        self.load_videos()

    def setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        self.style.configure('.', background=COLORS['background'], foreground=COLORS['text'])
        self.style.configure('VideoFrame.TFrame', background=COLORS['primary'])
        self.style.configure('Thumbnail.TFrame', background=COLORS['secondary'])
        self.style.configure('Custom.TLabel', background=COLORS['primary'])
        
        self.style.configure('Vertical.TScrollbar', background=COLORS['secondary'], 
                           troughcolor=COLORS['background'], bordercolor=COLORS['background'])
        
        self.style.configure('Accent.TButton', foreground=COLORS['text'], background=COLORS['accent'],
                           font=('Roboto', 10, 'bold'), borderwidth=0)
        self.style.map('Accent.TButton',
                      background=[('active', '#FF6666'), ('pressed', '#CC3D3D')])
        
        self.style.configure('Nav.TButton', foreground=COLORS['text'], 
                           background=COLORS['highlight'], font=('Roboto', 10))
        self.style.map('Nav.TButton',
                      background=[('active', '#5D5D5D'), ('pressed', '#4D4D4D')])

    def create_widgets(self):
        header_frame = ttk.Frame(self, style='VideoFrame.TFrame')
        header_frame.pack(fill=X, padx=10, pady=10)
        
        title_frame = ttk.Frame(header_frame, style='VideoFrame.TFrame')
        title_frame.pack(side=LEFT, padx=20)
        ttk.Label(title_frame, text="Erik Dubois' Latest Videos", 
                font=('Roboto', 16, 'bold'), style='Custom.TLabel').pack()
        
        btn_container = ttk.Frame(header_frame, style='VideoFrame.TFrame')
        btn_container.pack(side=RIGHT, padx=20)
        
        ttk.Button(btn_container, text="  About", command=self.show_about,
                 style='Nav.TButton').pack(side=RIGHT, padx=5, ipadx=8, ipady=3)
        ttk.Button(btn_container, text="⟳ Refresh", command=self.refresh_videos,
                 style='Nav.TButton').pack(side=RIGHT, padx=5, ipadx=8, ipady=3)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvas = Canvas(main_frame, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, style='Vertical.TScrollbar', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='VideoFrame.TFrame')

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def show_about(self):
        AboutWindow(self)

    def refresh_videos(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.load_videos()

    def load_videos(self):
        videos = get_videos()
        if not videos:
            error_frame = ttk.Frame(self.scrollable_frame, style='VideoFrame.TFrame')
            error_frame.pack(pady=50)
            ttk.Label(error_frame, text="⛔ No Videos Found ⛔", 
                    font=('Roboto', 14), foreground=COLORS['accent']).pack()
            return

        for idx, video in enumerate(videos):
            frame = StyledVideoFrame(self.scrollable_frame, video, video['thumbnail'])
            frame.pack(fill=X, padx=10, pady=8, ipady=5)
            if idx < len(videos)-1:
                ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).pack(fill=X, padx=20)

def get_videos():
    feed = feedparser.parse(CHANNEL_RSS)
    videos = []
    
    for entry in feed.entries[:MAX_ITEMS]:
        published = datetime(*entry.published_parsed[:6])
        videos.append({
            'date': humanize.naturaltime(published),
            'title': entry.title,
            'id': entry.yt_videoid,
            'link': entry.link,
            'thumbnail': entry.media_thumbnail[0]['url'].replace('hqdefault', 'mqdefault')
        })
    
    return videos

if __name__ == "__main__":
    app = ModernYTViewer()
    app.mainloop()