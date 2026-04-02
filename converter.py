import customtkinter as ctk
import yt_dlp
import os
import subprocess
import threading
import re

# --- CONFIG ---
# Dein GitHub-Pfad (achte darauf, dass am Ende ein / steht)
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class BacofyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BACOFY Desktop Control Center v3.1")
        self.geometry("550x600")

        # Header
        self.label = ctk.CTkLabel(self, text="BACOFY MUSIC CONVERTER", font=("Roboto", 24, "bold"))
        self.label.pack(pady=20)

        # Eingabefelder
        self.url_entry = ctk.CTkEntry(self, placeholder_text="YouTube URL hier einfügen...", width=450)
        self.url_entry.pack(pady=10)

        self.genre_entry = ctk.CTkEntry(self, placeholder_text="Genre / Ordner (z.B. Jpop)", width=450)
        self.genre_entry.pack(pady=10)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Song Name für Minecraft (Anzeige)", width=450)
        self.name_entry.pack(pady=10)

        # Button
        self.convert_button = ctk.CTkButton(self, text="SONG KONVERTIEREN & PUSH", 
                                          command=self.start_process, 
                                          fg_color="#1f538d", hover_color="#14375e")
        self.convert_button.pack(pady=20)

        # Log Box
        self.status_box = ctk.CTkTextbox(self, width=450, height=200, font=("Consolas", 12))
        self.status_box.pack(pady=10)
        self.log("System bereit. Warte auf Eingabe... 🥓")

    def log(self, text):
        self.status_box.insert("end", f"> {text}\n")
        self.status_box.see("end")

    def start_process(self):
        # Threading damit das Fenster nicht einfriert
        self.convert_button.configure(state="disabled")
        thread = threading.Thread(target=self.process)
        thread.start()

    def process(self):
        url = self.url_entry.get().strip()
        genre = self.genre_entry.get().strip()
        display_name = self.name_entry.get().strip()

        if not url or not genre or not display_name:
            self.log("FEHLER: Bitte alle Felder ausfüllen!")
            self.convert_button.configure(state="normal")
            return

        try:
            # 1. GIT PULL (Daten abgleichen)
            self.log("Synchronisiere mit GitHub (Pull)...")
            subprocess.run(["git", "pull", "origin", "main"], check=True)

            # 2. DATEINAME REINIGEN (Wichtig für Minecraft!)
            # Entfernt alles außer Buchstaben und Zahlen
            clean_filename = re.sub(r'[^a-zA-Z0-9]', '', display_name) + ".dfpwm"
            self.log(f"Dateiname: {clean_filename}")

            if not os.path.exists(genre):
                os.makedirs(genre)
                self.log(f"Ordner {genre} wurde erstellt.")

            # 3. YOUTUBE DOWNLOAD
            self.log("Lade Video/Audio von YouTube...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp_audio.%(ext)s',
                'noplaylist': True, 
                'ffmpeg_location': FFMPEG_DIR,
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # 4. FFMPEG KONVERTIERUNG
            self.log("Konvertiere zu DFPWM (Minecraft)...")
            output_file = os.path.join(genre, clean_filename)
            subprocess.run([
                FFMPEG_PATH, '-y', '-i', 'temp_audio.wav',
                '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm',
                output_file
            ], check=True)

            # 5. PLAYLIST AKTUALISIEREN
            self.log("Trage Song in playlist.txt ein...")
            playlist_path = os.path.join(genre, "playlist.txt")
            # Der Link muss URL-konform sein (BASE_URL + Ordner + clean_filename)
            final_url = f"{BASE_URL}{genre}/{clean_filename}"
            entry = f"{final_url}, {display_name}\n"
            
            with open(playlist_path, "a") as f:
                f.write(entry)

            # 6. GIT PUSH (Upload)
            self.log("Sende Daten zu GitHub (Push)...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Bacofy Auto-Add: {display_name}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)

            # Cleanup
            if os.path.exists('temp_audio.wav'):
                os.remove('temp_audio.wav')
            
            self.log("================================")
            self.log("ERFOLG! Song ist online.")
            self.log("Klicke REFRESH in Minecraft.")
            self.log("================================")
            
        except Exception as e:
            self.log(f"!!! FEHLER: {str(e)}")
        
        finally:
            self.convert_button.configure(state="normal")

if __name__ == "__main__":
    app = BacofyApp()
    app.mainloop()