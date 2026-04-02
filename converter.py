import customtkinter as ctk
import yt_dlp
import os
import subprocess
import threading
import re

# --- CONFIG ---
# Dein GitHub-Pfad (Raw-Link-Basis)
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BacofyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BACOFY HQ CONTROL v3.4")
        self.geometry("550x650")

        # UI Elemente
        ctk.CTkLabel(self, text="BACOFY HQ CONVERTER", font=("Roboto", 24, "bold")).pack(pady=20)
        
        self.url_entry = ctk.CTkEntry(self, placeholder_text="YouTube URL...", width=450)
        self.url_entry.pack(pady=10)
        
        self.genre_entry = ctk.CTkEntry(self, placeholder_text="Genre / Ordner (z.B. Jpop)", width=450)
        self.genre_entry.pack(pady=10)
        
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Song Name für Minecraft (Anzeige)", width=450)
        self.name_entry.pack(pady=10)

        self.btn = ctk.CTkButton(self, text="HQ KONVERTIEREN & PUSH", command=self.start_process, 
                                 fg_color="#1f538d", hover_color="#14375e")
        self.btn.pack(pady=20)

        self.status_box = ctk.CTkTextbox(self, width=450, height=250, font=("Consolas", 12))
        self.status_box.pack(pady=10)
        self.log("HQ-Modus aktiv: Nutzt SOXR Resampler & Loudnorm. 🥓")

    def log(self, text):
        self.status_box.insert("end", f"> {text}\n")
        self.status_box.see("end")

    def start_process(self):
        self.btn.configure(state="disabled")
        threading.Thread(target=self.process).start()

    def process(self):
        url = self.url_entry.get().strip()
        genre = self.genre_entry.get().strip()
        d_name = self.name_entry.get().strip()

        if not url or not genre or not d_name:
            self.log("FEHLER: Bitte alle Felder ausfüllen!")
            self.btn.configure(state="normal")
            return

        try:
            # 1. GIT PULL
            self.log("Synchronisiere mit GitHub (Pull)...")
            subprocess.run(["git", "pull", "origin", "main"], check=True)

            # 2. DATEINAME REINIGEN
            clean_filename = re.sub(r'[^a-zA-Z0-9]', '', d_name) + ".dfpwm"
            if not os.path.exists(genre):
                os.makedirs(genre)

            # 3. YOUTUBE DOWNLOAD
            self.log("Lade Video von YouTube...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp.%(ext)s',
                'noplaylist': True, 
                'ffmpeg_location': FFMPEG_DIR,
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # 4. HQ FFMPEG KONVERTIERUNG
            self.log("HQ-Konvertierung (Normalisierung & Filter)...")
            output_file = os.path.join(genre, clean_filename)
            subprocess.run([
                FFMPEG_PATH, '-y', '-i', 'temp.wav',
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', 
                '-ac', '1', '-ar', '48000', '-resampler', 'soxr', 
                '-acodec', 'dfpwm', output_file
            ], check=True)

            # 5. PLAYLIST AKTUALISIEREN
            self.log("Aktualisiere playlist.txt...")
            playlist_path = os.path.join(genre, "playlist.txt")
            final_url = f"{BASE_URL}{genre}/{clean_filename}"
            
            lines = []
            if os.path.exists(playlist_path):
                with open(playlist_path, "r") as f:
                    for line in f:
                        if line.strip(): lines.append(line.strip())
            
            lines.append(f"{final_url}, {d_name}")
            
            with open(playlist_path, "w") as f:
                f.write("\n".join(lines) + "\n")

            # 6. GIT PUSH (Songs + Code)
            self.log("Sende ALLES zu GitHub (Push)...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"HQ Add: {d_name}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)

            if os.path.exists('temp.wav'):
                os.remove('temp.wav')
            
            self.log("================================")
            self.log(f"ERFOLG! '{d_name}' ist online.")
            self.log("================================")
            
        except Exception as e:
            self.log(f"!!! KRITISCHER FEHLER: {str(e)}")
        
        finally:
            self.btn.configure(state="normal")

if __name__ == "__main__":
    app = BacofyApp()
    app.mainloop()