import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from yt_dlp import YoutubeDL
import threading
import os

# Globals
download_path = os.getcwd()

# GUI setup first
root = tk.Tk()
root.title("YouTube to MP3 Downloader")
root.geometry("500x260")

# Then safe to declare tkinter variables
current_filename = tk.StringVar(value="")
progress_value = tk.DoubleVar(value=0)

# Folder picker
def choose_folder():
    global download_path
    folder = filedialog.askdirectory()
    if folder:
        download_path = folder
        folder_label.config(text=f"Download folder: {download_path}")

# Update from progress hook
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0.0%').strip()
        filename = d.get('filename', '')
        try:
            progress_value.set(float(percent.strip('%')))
        except:
            progress_value.set(0)
        current_filename.set(f"Downloading: {os.path.basename(filename)} - {percent}")
    elif d['status'] == 'finished':
        current_filename.set("Download complete. Converting to MP3...")
    elif d['status'] == 'error':
        current_filename.set("Error during download.")

# Download wrapper
def start_download():
    url = entry.get().strip()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL.")
        return
    download_button.config(state="disabled")
    progress_value.set(0)
    current_filename.set("Starting download...")
    threading.Thread(target=download_mp3, args=(url,), daemon=True).start()

# Download function using yt_dlp as module
def download_mp3(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        messagebox.showinfo("Success", "MP3 downloaded successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        download_button.config(state="normal")
        current_filename.set("")


tk.Label(root, text="Paste YouTube link:").pack(pady=10)
entry = tk.Entry(root, width=60)
entry.pack()

tk.Button(root, text="Choose Download Folder", command=choose_folder).pack(pady=5)
folder_label = tk.Label(root, text=f"Download folder: {download_path}", wraplength=480)
folder_label.pack()

download_button = tk.Button(root, text="Download MP3", command=start_download)
download_button.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_value)
progress_bar.pack(pady=5)

progress_label = tk.Label(root, textvariable=current_filename, wraplength=480)
progress_label.pack(pady=5)

root.mainloop()
