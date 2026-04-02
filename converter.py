import customtkinter as ctk
import yt_dlp
import os
import subprocess
import threading

# --- CONFIG ---
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class BacofyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BACOFY Desktop Control Center v3.0")
        self.geometry("500x550")

        # UI Elemente
        self.label = ctk.CTkLabel(self, text="BACOFY MUSIC CONVERTER", font=("Roboto", 24, "bold"))
        self.label.pack(pady=20)

        self.url_entry = ctk.CTkEntry(self, placeholder_text="YouTube URL hier einfügen...", width=400)
        self.url_entry.pack(pady=10)

        self.genre_entry = ctk.CTkEntry(self, placeholder_text="Genre / Ordner (z.B. Jpop)", width=400)
        self.genre_entry.pack(pady=10)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Song Name für Minecraft", width=400)
        self.name_entry.pack(pady=10)

        self.convert_button = ctk.CTkButton(self, text="SONG KONVERTIEREN & PUSH", command=self.start_process)
        self.convert_button.pack(pady=20)

        self.status_box = ctk.CTkTextbox(self, width=400, height=150)
        self.status_box.pack(pady=10)
        self.log("Bereit für neue Banger! 🥓")

    def log(self, text):
        self.status_box.insert("end", text + "\n")
        self.status_box.see("end")

    def start_process(self):
        # Threading nutzen, damit das Fenster nicht einfriert
        thread = threading.Thread(target=self.process)
        thread.start()

    def process(self):
        url = self.url_entry.get()
        genre = self.genre_entry.get()
        name = self.name_entry.get()

        if not url or not genre or not name:
            self.log("FEHLER: Alle Felder ausfüllen!")
            return

        try:
            self.log(f"--- Starte Prozess für: {name} ---")
            
            # 1. GIT PULL
            self.log("Synchronisiere mit GitHub (Pull)...")
            subprocess.run(["git", "pull", "origin", "main"], check=True)

            # 2. DOWNLOAD
            self.log("Downloade von YouTube...")
            safe_filename = name.replace(" ", "_") + ".dfpwm"
            if not os.path.exists(genre): os.makedirs(genre)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp_audio.%(ext)s',
                'noplaylist': True, 
                'ffmpeg_location': FFMPEG_DIR,
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # 3. CONVERT
            self.log("Konvertiere zu DFPWM...")
            output_file = os.path.join(genre, safe_filename)
            subprocess.run([FFMPEG_PATH, '-y', '-i', 'temp_audio.wav', '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm', output_file], check=True)

            # 4. PLAYLIST UPDATE
            self.log("Aktualisiere Playlist...")
            playlist_path = os.path.join(genre, "playlist.txt")
            entry = f"{BASE_URL}{genre}/{safe_filename}, {name}\n"
            with open(playlist_path, "a") as f:
                f.write(entry)

            # 5. PUSH
            self.log("Upload zu GitHub (Push)...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Auto-Add: {name}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)

            if os.path.exists('temp_audio.wav'): os.remove('temp_audio.wav')
            self.log("=== ERFOLG! Song ist online! ===")
            
        except Exception as e:
            self.log(f"FEHLER: {str(e)}")

if __name__ == "__main__":
    app = BacofyApp()
    app.mainloop()