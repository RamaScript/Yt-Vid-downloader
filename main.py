import customtkinter as ctk
from tkinter import filedialog, messagebox
from video_info import fetch_video_info
import threading
import os
import yt_dlp

# Globals
download_path = os.path.expanduser("~/Downloads")

def choose_folder(entry):
    global download_path
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_path = folder_selected
        entry.delete(0, ctk.END)
        entry.insert(0, folder_selected)

def show_video_info(url, info_label, thumb_label):
    def fetch():
        data = fetch_video_info(url)
        if data:
            info_label.configure(text=f"🎮 {data['title']} | ⏱ {data['duration']}")
            thumb_label.configure(image=data['thumbnail_ctk'])
            thumb_label.image = data['thumbnail_ctk']

    threading.Thread(target=fetch, daemon=True).start()

def on_url_change(entry, info_label, thumb_label):
    url = entry.get()
    if url.strip():
        show_video_info(url, info_label, thumb_label)

def start_download(url, quality, path, is_playlist, progress_label, numbered_playlist):
    def download():
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                eta = d.get('_eta_str', '').strip()
                progress_label.configure(
                    text=f"Downloading... {percent} | Speed: {speed} | ETA: {eta}"
                )
            elif d['status'] == 'finished':
                progress_label.configure(text="Download complete!")

        try:
            outtmpl = os.path.join(path, '%(title)s.%(ext)s')
            if is_playlist == "playlist" and numbered_playlist:
                outtmpl = os.path.join(path, '%(playlist_index)s. %(title)s.%(ext)s')

            ydl_opts = {
                'progress_hooks': [progress_hook],
                'outtmpl': outtmpl,
                'quiet': True,
                'format': quality if quality not in ['best', 'worst'] else quality,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("Error", str(e))
            progress_label.configure(text="Download failed.")

    threading.Thread(target=download, daemon=True).start()

# App Init
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("YouTube Downloader - Smart GUI")
app.geometry("700x650")

# Radio buttons (Video / Playlist)
download_type = ctk.StringVar(value="video")
radio_frame = ctk.CTkFrame(app)
ctk.CTkRadioButton(radio_frame, text="Video", variable=download_type, value="video").pack(side="left", padx=10)
ctk.CTkRadioButton(radio_frame, text="Playlist", variable=download_type, value="playlist").pack(side="left", padx=10)
radio_frame.pack(pady=10)

# URL Entry
url_entry = ctk.CTkEntry(app, placeholder_text="Enter YouTube URL", width=500)
url_entry.pack(pady=10)
preview_btn = ctk.CTkButton(
    app,
    text="Preview",
    command=lambda: on_url_change(url_entry, video_info_label, thumbnail_label)
)
preview_btn.pack(pady=5)
preview_card = ctk.CTkFrame(app)
thumbnail_label = ctk.CTkLabel(preview_card, text="")
thumbnail_label.pack(pady=5)
video_info_label = ctk.CTkLabel(preview_card, text="", font=("Arial", 14))
video_info_label.pack()
preview_card.pack(pady=10)

# Video Quality Option
quality_var = ctk.StringVar(value="best")
quality_menu = ctk.CTkOptionMenu(app, values=["best", "worst", "1080p", "720p", "480p", "audio"], variable=quality_var)
quality_menu.pack(pady=10)

# Folder Picker
folder_frame = ctk.CTkFrame(app)
folder_entry = ctk.CTkEntry(folder_frame, width=440)
folder_entry.insert(0, download_path)
folder_entry.pack(side="left", padx=5)
folder_btn = ctk.CTkButton(folder_frame, text="📁", width=40, command=lambda: choose_folder(folder_entry))
folder_btn.pack(side="left")
folder_frame.pack(pady=10)

# Numbered Playlist Checkbox
numbered_playlist_var = ctk.BooleanVar(value=True)
numbered_checkbox = ctk.CTkCheckBox(app, text="Number playlist items (e.g., 1. video_title.ext)", variable=numbered_playlist_var)
numbered_checkbox.pack(pady=5)

# Thumbnail & Info
thumbnail_label = ctk.CTkLabel(app, text="")
thumbnail_label.pack(pady=10)
video_info_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
video_info_label.pack()

# Progress Label
progress_label = ctk.CTkLabel(app, text="", font=("Arial", 13))
progress_label.pack(pady=10)

# Download Button
download_btn = ctk.CTkButton(
    app,
    text="Download",
    command=lambda: start_download(
        url_entry.get(),
        quality_var.get(),
        folder_entry.get(),
        download_type.get(),
        progress_label,
        numbered_playlist_var.get()
    )
)
download_btn.pack(pady=20)

app.mainloop()
