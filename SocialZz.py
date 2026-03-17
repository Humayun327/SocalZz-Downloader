import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import re

class UniversalDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("SocialZz Downloader")
        self.root.geometry("500x480")

        # --- UI Elements ---
        tk.Label(root, text="Video URL:", font=("Arial", 10, "bold")).pack(pady=10)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        tk.Label(root, text="Select Quality:", font=("Arial", 10, "bold")).pack(pady=5)
        self.quality_var = tk.StringVar(value="Best Available")
        self.quality_menu = ttk.Combobox(root, textvariable=self.quality_var, state="readonly")
        self.quality_menu['values'] = ("Best Available", "720p", "520p", "480p", "380p", "360p")
        self.quality_menu.pack(pady=5)

        tk.Button(root, text="Browse Save Folder", command=self.browse_folder).pack(pady=10)
        self.path_label = tk.Label(root, text="No folder selected", fg="grey", font=("Arial", 8))
        self.path_label.pack()

        # --- Progress Section ---
        self.progress_label = tk.Label(root, text="Ready", font=("Arial", 9))
        self.progress_label.pack(pady=(20, 5))
        
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5)

        # UI Color change to reflect speed
        self.download_btn = tk.Button(root, text="Start Turbo Download", bg="#e67e22", fg="white", 
                                      command=self.start_download_thread, height=2, width=25, font=("Arial", 10, "bold"))
        self.download_btn.pack(pady=20)

        self.save_path = ""

    def browse_folder(self):
        self.save_path = filedialog.askdirectory()
        if self.save_path:
            self.path_label.config(text=f"Saving to: {self.save_path}", fg="blue")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            clean_p = re.sub(r'\x1b\[[0-9;]*m', '', p).replace('%', '')
            try:
                self.progress_bar['value'] = float(clean_p)
                # Added speed and ETA to the label
                self.progress_label.config(text=f"Speed: {d.get('_speed_str', 'N/A')} | ETA: {d.get('_eta_str', 'N/A')} | {p}")
                self.root.update_idletasks() 
            except ValueError:
                pass
        elif d['status'] == 'finished':
            self.progress_label.config(text="Download Complete! Finalizing file...")

    def get_format_string(self):
        choice = self.quality_var.get()
        if choice == "Best Available":
            return "best"
        height = choice.replace("p", "")
        # Optimized format string for faster selection
        return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

    def download_video(self):
        url = self.url_entry.get()
        if not url or not self.save_path:
            messagebox.showerror("Error", "Please provide a URL and select a folder!")
            return

        self.download_btn.config(state="disabled")
        self.progress_bar['value'] = 0
        
        # --- HIGH SPEED CONFIGURATION ---
        ydl_opts = {
            'format': self.get_format_string(),
            'outtmpl': f'{self.save_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'no_warnings': True,
            
            # 1. Multi-threaded fragmentation (The most important for speed)
            'concurrent_fragment_downloads': 10, 
            
            # 2. Network Optimizations
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'retries': 10,
            
            # 3. Buffer and Cache tuning
            'buffersize': 1024 * 1024, # 1MB buffer
            'http_chunk_size': 10485760, # 10MB chunks
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "Turbo Download finished!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress_label.config(text="Ready")
            self.download_btn.config(state="normal")

    def start_download_thread(self):
        thread = threading.Thread(target=self.download_video, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalDownloader(root)
    root.mainloop()