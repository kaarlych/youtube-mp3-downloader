import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import subprocess
import threading
import os

# Globals
download_path = os.getcwd()

# Choose folder callback
def choose_folder():
    global download_path
    folder = filedialog.askdirectory()
    if folder:
        download_path = folder
        folder_label.config(text=f"Download folder: {download_path}")

# Download thread wrapper
def start_download():
    url = entry.get().strip()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL.")
        return
    progress_bar.start()
    download_button.config(state="disabled")
    threading.Thread(target=download_mp3, args=(url,), daemon=True).start()

# Actual download function
def download_mp3(url):
    try:
        result = subprocess.run([
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "-o", os.path.join(download_path, "%(title)s.%(ext)s"),
            url
        ], capture_output=True, text=True)

        progress_bar.stop()
        download_button.config(state="normal")

        if result.returncode == 0:
            messagebox.showinfo("Success", "MP3 downloaded successfully!")
        else:
            messagebox.showerror("Download Failed", result.stderr)

    except Exception as e:
        progress_bar.stop()
        download_button.config(state="normal")
        messagebox.showerror("Error", str(e))

# GUI setup
root = tk.Tk()
root.title("YouTube to MP3 Downloader")
root.geometry("500x220")

tk.Label(root, text="Paste YouTube link:").pack(pady=10)
entry = tk.Entry(root, width=60)
entry.pack()

folder_btn = tk.Button(root, text="Choose Download Folder", command=choose_folder)
folder_btn.pack(pady=5)

folder_label = tk.Label(root, text=f"Download folder: {download_path}", wraplength=480)
folder_label.pack(pady=2)

download_button = tk.Button(root, text="Download MP3", command=start_download)
download_button.pack(pady=10)

progress_bar = ttk.Progressbar(root, mode='indeterminate', length=300)
progress_bar.pack(pady=5)

root.mainloop()
