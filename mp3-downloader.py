import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from yt_dlp import YoutubeDL
import threading
import os
import time
import random
import colorsys

# Globals
download_path = os.getcwd()

# GUI setup first
root = tk.Tk()
root.title("YouTube to MP3 Downloader")
root.geometry("550x360")
root.configure(bg="#f0f0f0")

# Style configuration
style = ttk.Style()
style.theme_use('default')
style.configure("TButton",
                padding=6,
                relief="flat",
                background="#4287f5",
                foreground="#ffffff",
                font=('Arial', 10, 'bold'))

style.configure("Horizontal.TProgressbar",
                thickness=25,
                borderwidth=0,
                troughcolor="#e0e0e0",
                background="#4287f5")

# Then safe to declare tkinter variables
current_filename = tk.StringVar(value="")
progress_value = tk.DoubleVar(value=0)
download_speed = tk.StringVar(value="")
estimated_time = tk.StringVar(value="")
download_in_progress = False

# Create a global reference to the download and cancel buttons
# We'll define these properly later
download_btn = None
cancel_btn = None


# Color transition effect for progress bar
def update_progress_color():
    # Generate a pulsing color effect
    hue = (time.time() / 10) % 1.0  # Cycle through hues
    r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.95)

    # Convert to hex format
    color = f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

    style.configure("Horizontal.TProgressbar", background=color)

    # Update progress text with bounce effect
    if progress_value.get() > 0 and progress_value.get() < 100:
        progress_text = "▮" * int(progress_value.get() / 5)
        progress_detail.config(text=progress_text)

    # Continue animation if download in progress
    if download_in_progress:
        root.after(100, update_progress_color)


# Progress indicator animation
def start_progress_animation():
    update_progress_color()

    # Add pulsing effect to labels
    def pulse_effect():
        if download_in_progress:
            # Make labels pulse slightly
            current_size = random.uniform(9.8, 10.2)
            progress_label.config(font=('Arial', int(current_size)))
            root.after(200, pulse_effect)

    pulse_effect()


# Folder picker
def choose_folder():
    global download_path
    folder = filedialog.askdirectory()
    if folder:
        download_path = folder
        folder_label.config(text=f"Download folder: {download_path}")


# Update from progress hook
def progress_hook(d):
    def update_ui():
        if d['status'] == 'downloading':
            # Parse percentage more reliably
            if '_percent_str' in d:
                percent_str = d['_percent_str'].strip()
                try:
                    # Handle both "45.5%" and "45.5" formats
                    percent_value = float(percent_str.rstrip('%'))
                    progress_value.set(percent_value)
                except ValueError:
                    # Fall back to downloaded bytes if percentage parsing fails
                    if 'downloaded_bytes' in d and 'total_bytes' in d:
                        if d['total_bytes'] > 0:
                            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                            progress_value.set(percent)

            # Update speed and ETA info
            if 'speed' in d and d['speed'] is not None:
                speed_mbps = d['speed'] / 1024 / 1024  # Convert to MB/s
                download_speed.set(f"Speed: {speed_mbps:.2f} MB/s")

            if 'eta' in d and d['eta'] is not None:
                eta_mins = d['eta'] // 60
                eta_secs = d['eta'] % 60
                estimated_time.set(f"ETA: {eta_mins}m {eta_secs}s")

            filename = d.get('filename', '')
            current_filename.set(f"Downloading: {os.path.basename(filename)}")

        elif d['status'] == 'finished':
            progress_value.set(100)  # Set to 100% when download is finished
            current_filename.set("Download complete. Converting to MP3...")
            download_speed.set("")
            estimated_time.set("")
            # Change progress bar color for completion
            style.configure("Horizontal.TProgressbar", background="#2ecc71")  # Green

        elif d['status'] == 'error':
            current_filename.set("Error during download.")
            style.configure("Horizontal.TProgressbar", background="#e74c3c")  # Red

    # Schedule the UI update on the main thread
    root.after(10, update_ui)


# Standard button (simpler implementation)
def create_button(parent, text, command, bg_color="#4287f5"):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_color,
        fg="white",
        font=("Arial", 11, "bold"),
        relief="flat",
        padx=20,
        pady=8,
        activebackground="#2a6dd7",
        activeforeground="white",
        bd=0
    )
    return button


# Download wrapper
def start_download():
    global download_in_progress
    url = entry.get().strip()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL.")
        return

    download_in_progress = True
    download_btn.pack_forget()  # Hide download button
    cancel_btn.pack(pady=10)  # Show cancel button

    progress_value.set(0)
    current_filename.set("Starting download...")
    download_speed.set("Connecting...")
    estimated_time.set("Calculating...")

    # Start progress animation
    start_progress_animation()

    threading.Thread(target=download_mp3, args=(url,), daemon=True).start()


# Cancel download functionality
def cancel_download():
    global download_in_progress
    download_in_progress = False
    current_filename.set("Download cancelled.")
    progress_value.set(0)
    download_speed.set("")
    estimated_time.set("")

    # Reset UI
    cancel_btn.pack_forget()
    download_btn.pack(pady=10)


# Download function using yt_dlp as module
def download_mp3(url):
    global download_in_progress
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'EmbedThumbnail',
                },
                {
                    'key': 'FFmpegMetadata',
                },
            ],
            'writethumbnail': True,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
            'prefer_ffmpeg': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Define completion function
        def complete_download():
            global download_in_progress
            download_in_progress = False
            current_filename.set("Download completed! Ready for next download.")

            # Force the cancel button to hide and download button to show
            if cancel_btn.winfo_ismapped():
                cancel_btn.pack_forget()

            if not download_btn.winfo_ismapped():
                download_btn.pack(pady=10)

            # Clear download stats
            download_speed.set("")
            estimated_time.set("")

            # Debug message to console (won't be visible to users)
            print("Download complete, button should be visible now")

        # Schedule UI updates on the main thread
        root.after(0, complete_download)

    except Exception as e:
        # Error handling function
        def handle_error():
            global download_in_progress
            download_in_progress = False
            messagebox.showerror("Error", str(e))
            current_filename.set("Download error")

            # Force the cancel button to hide and download button to show
            if cancel_btn.winfo_ismapped():
                cancel_btn.pack_forget()

            if not download_btn.winfo_ismapped():
                download_btn.pack(pady=10)

            # Clear download stats
            download_speed.set("")
            estimated_time.set("")

        root.after(0, handle_error)


# Create gradient title
title_frame = tk.Frame(root, bg="#f0f0f0")
title_frame.pack(pady=10, fill="x")

title_label = tk.Label(title_frame, text="YouTube to MP3 Downloader",
                       font=("Arial", 16, "bold"),
                       fg="#4287f5", bg="#f0f0f0")
title_label.pack()

# URL entry section
entry_frame = tk.Frame(root, bg="#f0f0f0")
entry_frame.pack(pady=5)

entry_label = tk.Label(entry_frame, text="Paste YouTube link:",
                       font=("Arial", 10),
                       fg="#555", bg="#f0f0f0")
entry_label.pack(anchor="w")

entry = tk.Entry(entry_frame, width=60, font=("Arial", 10),
                 bd=0, highlightthickness=1, highlightbackground="#ccc",
                 bg="white", fg="black")
entry.pack(pady=5, ipady=8)

# Download folder section
folder_frame = tk.Frame(root, bg="#f0f0f0")
folder_frame.pack(pady=5)

folder_button = tk.Button(folder_frame, text="Choose Download Folder",
                          command=choose_folder,
                          bg="#e0e0e0", fg="#333",
                          relief="flat", padx=10, pady=5,
                          font=("Arial", 9))
folder_button.pack(pady=5)

folder_label = tk.Label(folder_frame, text=f"Download folder: {download_path}",
                        wraplength=500, font=("Arial", 9),
                        fg="#555", bg="#f0f0f0")
folder_label.pack(pady=3)

# Create buttons container frame (helps with button management)
buttons_frame = tk.Frame(root, bg="#f0f0f0")
buttons_frame.pack(pady=10)

# Create the buttons with simpler implementation
download_btn = create_button(buttons_frame, "Download MP3", start_download, "#4287f5")
download_btn.pack(pady=10)

cancel_btn = create_button(buttons_frame, "Cancel Download", cancel_download, "#e74c3c")
cancel_btn.pack_forget()  # Initially hidden

# Progress section
progress_frame = tk.Frame(root, bg="#f0f0f0")
progress_frame.pack(pady=5, fill="x", padx=20)

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal",
                               length=500, mode="determinate",
                               variable=progress_value,
                               style="Horizontal.TProgressbar")
progress_bar.pack(fill="x", pady=5)

# Progress details
progress_detail = tk.Label(progress_frame, text="", bg="#f0f0f0", fg="#4287f5",
                           font=("Courier New", 12))
progress_detail.pack(pady=2)

# Status information
info_frame = tk.Frame(root, bg="#f0f0f0")
info_frame.pack(pady=5, fill="x")

progress_label = tk.Label(info_frame, textvariable=current_filename,
                          wraplength=500, font=("Arial", 10),
                          fg="#333", bg="#f0f0f0")
progress_label.pack(pady=2)

# Download stats (speed and ETA)
stats_frame = tk.Frame(root, bg="#f0f0f0")
stats_frame.pack(pady=0, fill="x")

speed_label = tk.Label(stats_frame, textvariable=download_speed,
                       font=("Arial", 9), fg="#555", bg="#f0f0f0")
speed_label.pack(side="left", padx=25)

eta_label = tk.Label(stats_frame, textvariable=estimated_time,
                     font=("Arial", 9), fg="#555", bg="#f0f0f0")
eta_label.pack(side="right", padx=25)

# Add a footer
footer = tk.Label(root, text="Made with ❤️ using Python",
                  font=("Arial", 8), fg="#888", bg="#f0f0f0")
footer.pack(side="bottom", pady=5)

root.mainloop()