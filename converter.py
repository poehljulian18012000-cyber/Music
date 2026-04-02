import yt_dlp
import os
import subprocess

# --- CONFIGURATION ---
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

def update_playlist_file(category, filename, song_display_name):
    """Adds the direct raw link to the playlist.txt inside the genre folder."""
    # Wir nutzen jetzt playlist.txt, damit Bacofy es sofort findet
    playlist_path = os.path.join(category, "playlist.txt")
    file_url = f"{BASE_URL}{category}/{filename}"
    entry = f"{file_url}, {song_display_name}"
    
    # Check if file exists to avoid duplicates
    if os.path.exists(playlist_path):
        with open(playlist_path, "r") as f:
            if entry in f.read():
                print(f"--- Info: {song_display_name} ist bereits in der {category}/playlist.txt ---")
                return

    # Append entry
    with open(playlist_path, "a") as f:
        f.write(entry + "\n")
    print(f"--- Success: Link in {category}/playlist.txt gespeichert ---")

def run_bacofy_encoder():
    print("====================================")
    print("   BACOFY ENCODER - PLAYLIST MODE   ")
    print("====================================")
    
    raw_url = input("YouTube URL: ")
    category = input("Genre/Ordner (z.B. Jpop, Tekk): ")
    song_name = input("Song Name für Minecraft: ")
    
    # Bereinige Dateiname (keine Leerzeichen für GitHub Links)
    safe_filename = song_name.replace(" ", "_") + ".dfpwm"
    
    if not os.path.exists(category):
        os.makedirs(category)

    # yt-dlp Optionen: 'noplaylist' sorgt dafür, dass nur 1 Song geladen wird!
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'noplaylist': True, 
        'ffmpeg_location': FFMPEG_DIR,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]
    }

    try:
        print(f"\n--- Lade Song herunter... ---")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([raw_url])

        print(f"--- Konvertiere zu DFPWM... ---")
        output_file = os.path.join(category, safe_filename)
        
        # FFmpeg Prozess
        subprocess.run([
            FFMPEG_PATH, '-y', '-i', 'temp_audio.wav',
            '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm',
            output_file
        ], check=True)

        # Playlist-Datei im Unterordner aktualisieren
        update_playlist_file(category, safe_filename, song_name)

        # Temporäre WAV löschen
        if os.path.exists('temp_audio.wav'):
            os.remove('temp_audio.wav')
            
        print("\n=== FERTIG! ===")
        print(f"Datei erstellt: {output_file}")
        print("Jetzt: git add . && git commit -m 'Add Song' && git push")

    except Exception as e:
        print(f"\n!!! FEHLER: {e} !!!")

if __name__ == "__main__":
    run_bacofy_encoder()