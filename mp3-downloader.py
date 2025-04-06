import tkinter as tk
from tkinter import messagebox
import subprocess

def download_mp3():
    url = entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL.")
        return
    try:
        subprocess.run([
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            url
        ], check=True)
        messagebox.showinfo("Success", "MP3 downloaded successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Download failed:\n{e}")

# GUI setup
root = tk.Tk()
root.title("YouTube to MP3 Downloader")
root.geometry("400x150")

label = tk.Label(root, text="Paste YouTube link:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

download_button = tk.Button(root, text="Download MP3", command=download_mp3)
download_button.pack(pady=10)

root.mainloop()
