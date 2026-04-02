import yt_dlp
import os
import subprocess

# --- CONFIGURATION ---
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

def update_genre_index(category, filename, song_display_name):
    """Adds the song link to the specific genre index (e.g. Jpop/index.txt)"""
    index_path = os.path.join(category, "index.txt")
    file_url = f"{BASE_URL}{category}/{filename}"
    entry = f"{file_url}, {song_display_name}"
    
    # Check for duplicates
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            if entry in f.read():
                print(f"--- Info: {song_display_name} already exists in {category} ---")
                return

    with open(index_path, "a") as f:
        f.write(entry + "\n")
    print(f"--- Success: {song_display_name} added to {category}/index.txt ---")

def run_bacofy():
    print("=== BACOFY MUSIC ENCODER (English) ===")
    url = input("YouTube URL: ")
    category = input("Genre (Folder name, e.g., Jpop or Tekk): ")
    song_name = input("Song Name (for the UI): ")
    
    # Clean filename
    safe_filename = song_name.replace(" ", "_") + ".dfpwm"
    
    if not os.path.exists(category):
        os.makedirs(category)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'ffmpeg_location': FFMPEG_DIR,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]
    }

    try:
        print(f"--- Downloading: {song_name} ---")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"--- Converting to DFPWM ---")
        output_file = os.path.join(category, safe_filename)
        subprocess.run([
            FFMPEG_PATH, '-y', '-i', 'temp_audio.wav',
            '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm',
            output_file
        ], check=True)

        update_genre_index(category, safe_filename, song_name)

        if os.path.exists('temp_audio.wav'):
            os.remove('temp_audio.wav')
            
        print("\n=== DONE! ===")
        print(f"Folder: {category} | File: {safe_filename}")
        print("Ready for: git add . && git commit -m 'Add song' && git push")

    except Exception as e:
        print(f"!!! Error: {e} !!!")

if __name__ == "__main__":
    run_bacofy()