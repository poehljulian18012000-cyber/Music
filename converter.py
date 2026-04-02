import yt_dlp
import os
import subprocess

# --- CONFIGURATION ---
BASE_URL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/"
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_DIR = r"C:\ffmpeg\bin"

def update_category_index(category, filename, song_display_name):
    """Updates the index.txt inside the specific category folder for Bacofy Pocket."""
    index_path = os.path.join(category, "index.txt")
    
    # Format for Bacofy Pocket: DirectURL, SongName
    file_url = f"{BASE_URL}{category}/{filename}"
    entry = f"{file_url}, {song_display_name}"
    
    # Check if entry already exists
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            if entry in f.read():
                print(f"--- Info: {song_display_name} already exists in {category}/index.txt ---")
                return

    # Append to the category index
    with open(index_path, "a") as f:
        f.write(entry + "\n")
    print(f"--- Success: Added to {category}/index.txt ---")

def download_and_convert():
    print("==============================")
    print("   BACOFY SYSTEM - ENCODER    ")
    print("==============================")
    
    url = input("YouTube URL: ")
    print("\nAvailable Categories (e.g., Tekk, Jpop, Kpop)")
    category = input("Enter Category: ")
    song_input = input("Enter Song Name (as shown in Minecraft): ")
    
    # Format filename for filesystem (no spaces)
    filename = song_input.replace(" ", "_") + ".dfpwm"

    # Ensure folder exists
    if not os.path.exists(category):
        os.makedirs(category)

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'ffmpeg_location': FFMPEG_DIR,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
    }

    try:
        print(f"\n--- Action: Downloading {song_input}... ---")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("--- Action: Converting to DFPWM... ---")
        output_path = os.path.join(category, filename)
        
        # FFmpeg conversion
        subprocess.run([
            FFMPEG_PATH, '-y', '-i', 'temp_audio.wav',
            '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm',
            output_path
        ], check=True)

        # Update the index file for the Pocket Client
        update_category_index(category, filename, song_input)

        # Cleanup
        if os.path.exists('temp_audio.wav'):
            os.remove('temp_audio.wav')
        
        print(f"\n=== FINISHED! ===")
        print(f"File: {output_path}")
        print("Now run: git add . && git commit -m 'New Song' && git push")

    except Exception as e:
        print(f"\n!!! ERROR: {e} !!!")

if __name__ == "__main__":
    download_and_convert()