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
root.configure(bg="#f5f5f7")  # Light Apple-style background

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


# Modern button with rounded corners
def create_modern_button(parent, text, command, primary=True):
    if primary:
        bg_color = "#1a73e8"  # Google blue
        hover_color = "#0d62cb"
    else:
        bg_color = "#f44336"  # Material red
        hover_color = "#d32f2f"

    # Create a canvas-based button with rounded corners
    button_frame = tk.Frame(parent, bg="#f5f5f7")

    # Canvas for rounded button
    canvas = tk.Canvas(button_frame, width=150, height=40,
                       bg="#f5f5f7", highlightthickness=0)
    canvas.pack()

    # Create rounded rectangle
    radius = 10
    button = canvas.create_rounded_rect(0, 0, 150, 40, radius, fill=bg_color)
    button_text = canvas.create_text(75, 20, text=text, fill="white",
                                     font=("Segoe UI", 11, "bold"))

    # Bind events
    def on_enter(e):
        canvas.itemconfig(button, fill=hover_color)

    def on_leave(e):
        canvas.itemconfig(button, fill=bg_color)

    def on_click(e):
        canvas.itemconfig(button, fill=hover_color)
        command()

    canvas.tag_bind(button, "<Enter>", on_enter)
    canvas.tag_bind(button, "<Leave>", on_leave)
    canvas.tag_bind(button, "<Button-1>", on_click)
    canvas.tag_bind(button_text, "<Enter>", on_enter)
    canvas.tag_bind(button_text, "<Leave>", on_leave)
    canvas.tag_bind(button_text, "<Button-1>", on_click)

    return button_frame


# Add the rounded rectangle method to the Canvas class
tk.Canvas.create_rounded_rect = lambda self, x1, y1, x2, y2, radius, **kwargs: self.create_polygon(
    x1 + radius, y1,
    x2 - radius, y1,
    x2, y1,
    x2, y1 + radius,
    x2, y2 - radius,
    x2, y2,
    x2 - radius, y2,
    x1 + radius, y2,
    x1, y2,
    x1, y2 - radius,
    x1, y1 + radius,
    x1, y1,
    smooth=True, **kwargs)


# Standard button (fallback if the rounded corners don't work)
def create_button(parent, text, command, primary=True):
    if primary:
        bg_color = "#1a73e8"  # Google blue
        hover_color = "#0d62cb"
    else:
        bg_color = "#f44336"  # Material red
        hover_color = "#d32f2f"

    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_color,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padx=20,
        pady=8,
        activebackground=hover_color,
        activeforeground="white",
        bd=0,
        cursor="hand2"  # Hand cursor on hover
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

    # Clear entry field for next use
    entry.delete(0, tk.END)

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
title_frame = tk.Frame(root, bg="#f5f5f7")
title_frame.pack(pady=10, fill="x")

# Add a subtle gradient effect to the title
title_canvas = tk.Canvas(title_frame, width=500, height=40,
                         bg="#f5f5f7", highlightthickness=0)
title_canvas.pack()

# Create gradient for title
title_canvas.create_text(250, 20, text="YouTube to MP3 Downloader",
                         font=("Segoe UI", 16, "bold"),
                         fill="#1a73e8")  # Google blue

# URL entry section with modern design
entry_frame = tk.Frame(root, bg="#f5f5f7")
entry_frame.pack(pady=5)

entry_label = tk.Label(entry_frame, text="Paste YouTube link:",
                       font=("Segoe UI", 10),
                       fg="#555", bg="#f5f5f7")
entry_label.pack(anchor="w")

# Create a frame for the entry to add a subtle shadow effect
entry_container = tk.Frame(entry_frame, bg="#ddd", padx=1, pady=1)
entry_container.pack(pady=5)

entry = tk.Entry(entry_container, width=60, font=("Segoe UI", 10),
                 bd=0, highlightthickness=0,
                 bg="white", fg="#202124")  # Google text color
entry.pack(ipady=8, padx=1, pady=1)

# Download folder section with modern style
folder_frame = tk.Frame(root, bg="#f5f5f7")
folder_frame.pack(pady=5)

folder_button = tk.Button(folder_frame, text="Choose Download Folder",
                          command=choose_folder,
                          bg="#e8eaed", fg="#202124",  # Google gray
                          relief="flat", padx=10, pady=5,
                          font=("Segoe UI", 9),
                          cursor="hand2")
folder_button.pack(pady=5)

folder_label = tk.Label(folder_frame, text=f"Download folder: {download_path}",
                        wraplength=500, font=("Segoe UI", 9),
                        fg="#5f6368", bg="#f5f5f7")  # Google secondary text
folder_label.pack(pady=3)

# Create buttons container frame
buttons_frame = tk.Frame(root, bg="#f5f5f7")
buttons_frame.pack(pady=10)

# Try to use modern rounded buttons, fallback to standard if error
try:
    download_btn = create_modern_button(buttons_frame, "Download MP3", start_download, True)
    download_btn.pack(pady=10)

    cancel_btn = create_modern_button(buttons_frame, "Cancel Download", cancel_download, False)
    cancel_btn.pack_forget()  # Initially hidden
except Exception:
    # Fallback to standard buttons
    download_btn = create_button(buttons_frame, "Download MP3", start_download, True)
    download_btn.pack(pady=10)

    cancel_btn = create_button(buttons_frame, "Cancel Download", cancel_download, False)
    cancel_btn.pack_forget()  # Initially hidden

# Progress section with modern design
progress_frame = tk.Frame(root, bg="#f5f5f7")
progress_frame.pack(pady=5, fill="x", padx=20)

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal",
                               length=500, mode="determinate",
                               variable=progress_value,
                               style="Horizontal.TProgressbar")
progress_bar.pack(fill="x", pady=5)

# Progress details
progress_detail = tk.Label(progress_frame, text="", bg="#f5f5f7", fg="#1a73e8",
                           font=("Consolas", 12))
progress_detail.pack(pady=2)

# Status information with modern font
info_frame = tk.Frame(root, bg="#f5f5f7")
info_frame.pack(pady=5, fill="x")

progress_label = tk.Label(info_frame, textvariable=current_filename,
                          wraplength=500, font=("Segoe UI", 10),
                          fg="#202124", bg="#f5f5f7")
progress_label.pack(pady=2)

# Download stats with modern look
stats_frame = tk.Frame(root, bg="#f5f5f7")
stats_frame.pack(pady=0, fill="x")

speed_label = tk.Label(stats_frame, textvariable=download_speed,
                       font=("Segoe UI", 9), fg="#5f6368", bg="#f5f5f7")
speed_label.pack(side="left", padx=25)

eta_label = tk.Label(stats_frame, textvariable=estimated_time,
                     font=("Segoe UI", 9), fg="#5f6368", bg="#f5f5f7")
eta_label.pack(side="right", padx=25)

# Add a footer with subtle styling
footer = tk.Label(root, text="Made with ❤️ using Python",
                  font=("Segoe UI", 8), fg="#5f6368", bg="#f5f5f7")
footer.pack(side="bottom", pady=5)

root.mainloop()