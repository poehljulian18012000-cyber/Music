import yt_dlp
import os
import subprocess

# --- CONFIGURATION ---
# Achte darauf, dass die Datei auf GitHub auch 'Bacofy.lua' heißt!
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

def update_playlist_file(category, filename, song_display_name):
    """Schreibt den Link direkt in die playlist.txt des Genres."""
    playlist_path = os.path.join(category, "playlist.txt")
    file_url = f"{BASE_URL}{category}/{filename}"
    entry = f"{file_url}, {song_display_name}"
    
    # Verhindert doppelte Einträge
    if os.path.exists(playlist_path):
        with open(playlist_path, "r") as f:
            if entry in f.read():
                print(f"--- Info: Song bereits in {category}/playlist.txt vorhanden ---")
                return

    with open(playlist_path, "a") as f:
        f.write(entry + "\n")
    print(f"--- Success: Link zu {category}/playlist.txt hinzugefügt ---")

def run_bacofy_encoder():
    print("====================================")
    print("   BACOFY ENCODER - VERSION 2.0    ")
    print("====================================")
    
    raw_url = input("YouTube URL: ")
    category = input("Genre/Ordner (z.B. Jpop, Tekk): ")
    song_name = input("Song Name für Minecraft: ")
    
    # Dateiname ohne Leerzeichen für saubere URLs
    safe_filename = song_name.replace(" ", "_") + ".dfpwm"
    
    if not os.path.exists(category):
        os.makedirs(category)

    # noplaylist=True verhindert das Laden von 100+ Songs
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'noplaylist': True, 
        'ffmpeg_location': FFMPEG_DIR,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]
    }

    try:
        print(f"\n[1/3] Downloade Audio...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([raw_url])

        print(f"[2/3] Konvertiere zu DFPWM...")
        output_file = os.path.join(category, safe_filename)
        
        subprocess.run([
            FFMPEG_PATH, '-y', '-i', 'temp_audio.wav',
            '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm',
            output_file
        ], check=True)

        print(f"[3/3] Aktualisiere Playlisten...")
        update_playlist_file(category, safe_filename, song_name)

        if os.path.exists('temp_audio.wav'):
            os.remove('temp_audio.wav')
            
        print("\n=== FERTIG! ===")
        print(f"Song: {song_name}")
        print(f"Pfad: {output_file}")
        print("\nNächster Schritt: git add . && git commit -m 'New Song' && git push")

    except Exception as e:
        print(f"\n!!! FEHLER: {e} !!!")

if __name__ == "__main__":
    run_bacofy_encoder()