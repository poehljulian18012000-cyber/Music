import yt_dlp
import os
import subprocess

def update_index(folder, filename):
    index_path = "index.txt"
    # Eintrag erstellen: "Ordner/Dateiname"
    entry = f"{folder}/{filename}"
    
    # Prüfen, ob der Song schon drin steht
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            if entry in f.read():
                print(f"--- {filename} ist schon im Index. ---")
                return

    # Song am Ende hinzufügen
    with open(index_path, "a") as f:
        f.write(entry + "\n")
    print(f"--- {filename} wurde zur index.txt hinzugefügt! ---")

def download_and_convert():
    url = input("YouTube Link: ")
    print("Verfügbare Ordner: Tekk, Jpop, Kpop")
    folder = input("In welchen Ordner? ")
    song_name = input("Wie soll der Song heißen (ohne Endung)? ")
    filename = song_name + ".dfpwm"

    if not os.path.exists(folder):
        os.makedirs(folder)

    ffmpeg_dir = r"C:\ffmpeg\bin"
    ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'ffmpeg_location': ffmpeg_dir,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
    }

    print(f"--- Lade {song_name} herunter... ---")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("--- Bacofy konvertiert... ---")
    output_path = os.path.join(folder, filename)
    subprocess.run([
        ffmpeg_exe, '-y', '-i', 'temp_audio.wav',
        '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm',
        output_path
    ])

    # Index aktualisieren
    update_index(folder, filename)

    if os.path.exists('temp_audio.wav'):
        os.remove('temp_audio.wav')
    
    print(f"--- FERTIG! Gespeichert in {output_path} ---")

if __name__ == "__main__":
    download_and_convert()