import customtkinter as ctk
import yt_dlp
import os
import subprocess
import threading
import re

# --- CONFIG ---
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BacofyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BACOFY RAW HQ v3.9")
        self.geometry("550x600")

        ctk.CTkLabel(self, text="BACOFY RAW CONVERTER", font=("Roboto", 24, "bold")).pack(pady=20)
        self.url_entry = ctk.CTkEntry(self, placeholder_text="YouTube URL...", width=450)
        self.url_entry.pack(pady=10)
        self.genre_entry = ctk.CTkEntry(self, placeholder_text="Genre...", width=450)
        self.genre_entry.pack(pady=10)
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Song Name...", width=450)
        self.name_entry.pack(pady=10)

        self.btn = ctk.CTkButton(self, text="RAW KONVERTIEREN & PUSH", command=self.start_process)
        self.btn.pack(pady=20)

        self.status_box = ctk.CTkTextbox(self, width=450, height=200, font=("Consolas", 12))
        self.status_box.pack(pady=10)

    def log(self, text):
        self.status_box.insert("end", f"> {text}\n"); self.status_box.see("end")

    def start_process(self):
        self.btn.configure(state="disabled")
        threading.Thread(target=self.process).start()

    def process(self):
        url, genre, d_name = self.url_entry.get().strip(), self.genre_entry.get().strip(), self.name_entry.get().strip()
        if not url or not genre or not d_name:
            self.log("FEHLER: Felder ausfüllen!"); self.btn.configure(state="normal"); return

        try:
            self.log("Synchronisiere GitHub...")
            subprocess.run(["git", "pull", "origin", "main"], check=True)

            safe_name = re.sub(r'[^a-zA-Z0-9]', '', d_name)
            output_file = os.path.join(genre, f"{safe_name}.raw")
            if not os.path.exists(genre): os.makedirs(genre)

            self.log("Lade von YouTube...")
            ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'temp.%(ext)s', 'ffmpeg_location': FFMPEG_DIR, 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
            
            self.log("Konvertiere zu RAW (HQ-Resample)...")
            subprocess.run([
                FFMPEG_PATH, '-y', '-i', 'temp.wav',
                '-af', 'aresample=48000:resample_cutoff=0.99:dither_method=triangular,volume=-1dB',
                '-ac', '1', '-ar', '48000', '-f', 's8', '-acodec', 'pcm_s8',
                output_file
            ], check=True)

            self.log("Update Playlist...")
            playlist_path = os.path.join(genre, "playlist.txt")
            with open(playlist_path, "a") as f: 
                f.write(f"{BASE_URL}{genre}/{safe_name}.raw, {d_name}\n")

            self.log("Pushe zu GitHub...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"RAW Add: {d_name}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)

            if os.path.exists('temp.wav'): os.remove('temp.wav')
            self.log("ERFOLGREICH! „" + d_name + "“ ist jetzt online.")
        except Exception as e: self.log(f"FEHLER: {str(e)}")
        finally: self.btn.configure(state="normal")

if __name__ == "__main__":
    BacofyApp().mainloop()