import yt_dlp
import os
import subprocess

# --- CONFIGURATION ---
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

def run_git_commands(song_name):
    """Führt git add, commit und push automatisch aus."""
    try:
        print("\n--- Synchronisiere mit GitHub... ---")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-Add: {song_name}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("--- GitHub Update ERFOLGREICH! ---")
    except Exception as e:
        print(f"--- GitHub Fehler: {e} ---")
        print("Hinweis: Vielleicht musst du einmal manuell 'git pull' machen?")

def update_playlist_file(category, filename, song_display_name):
    playlist_path = os.path.join(category, "playlist.txt")
    file_url = f"{BASE_URL}{category}/{filename}"
    entry = f"{file_url}, {song_display_name}"
    
    if os.path.exists(playlist_path):
        with open(playlist_path, "r") as f:
            if entry in f.read():
                print(f"--- Info: Song bereits in {category}/playlist.txt ---")
                return

    with open(playlist_path, "a") as f:
        f.write(entry + "\n")
    print(f"--- Success: Link in {category}/playlist.txt gespeichert ---")

def run_bacofy_encoder():
    print("====================================")
    print("   BACOFY AUTO-CONVERTER & PUSH     ")
    print("====================================")
    
    raw_url = input("YouTube URL: ")
    category = input("Genre/Ordner (z.B. Jpop): ")
    song_name = input("Song Name für Minecraft: ")
    
    safe_filename = song_name.replace(" ", "_") + ".dfpwm"
    
    if not os.path.exists(category):
        os.makedirs(category)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'noplaylist': True, 
        'ffmpeg_location': FFMPEG_DIR,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]
    }

    try:
        # 1. Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([raw_url])

        # 2. Konvertierung
        output_file = os.path.join(category, safe_filename)
        subprocess.run([
            FFMPEG_PATH, '-y', '-i', 'temp_audio.wav',
            '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm',
            output_file
        ], check=True)

        # 3. Playlist-Datei schreiben
        update_playlist_file(category, safe_filename, song_name)

        # 4. Git Upload
        run_git_commands(song_name)

        if os.path.exists('temp_audio.wav'):
            os.remove('temp_audio.wav')
            
        print("\n=== ALLES ERLEDIGT! ===")
        print(f"Song '{song_name}' ist jetzt online und bereit für Minecraft.")

    except Exception as e:
        print(f"\n!!! FEHLER: {e} !!!")

if __name__ == "__main__":
    run_bacofy_encoder()