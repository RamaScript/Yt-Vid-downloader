import yt_dlp
from PIL import Image, ImageTk
import requests
from io import BytesIO
import customtkinter as ctk

def fetch_video_info(url):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get('title', 'Unknown Title')
        duration = format_duration(info.get('duration', 0))
        thumbnail_url = info.get('thumbnail', '')

        # Load thumbnail image
        response = requests.get(thumbnail_url)
        img_data = Image.open(BytesIO(response.content))
        img_data = img_data.resize((320, 180))
        thumbnail_ctk = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(320, 180))

        return {
            'title': title,
            'duration': duration,
            'thumbnail_ctk': thumbnail_ctk
        }

    except Exception as e:
        print("Failed to fetch info:", e)
        return None

def format_duration(seconds):
    minutes, sec = divmod(seconds, 60)
    hrs, mins = divmod(minutes, 60)
    if hrs:
        return f"{hrs}:{mins:02}:{sec:02}"
    else:
        return f"{mins}:{sec:02}"

