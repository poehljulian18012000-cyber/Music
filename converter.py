import yt_dlp
import os
import subprocess

def download_and_convert():
    url = input("YouTube Link: ")
    folder = input("In welchen Ordner (z.B. Tekk, Jpop, Kpop)? ")
    filename = input("Wie soll der Song heißen (ohne .dfpwm)? ") + ".dfpwm"

    # Pfad erstellen, falls Ordner nicht existiert
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

    print(f"--- Lade {filename} herunter... ---")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("--- Konvertiere... ---")
    output_path = os.path.join(folder, filename)
    subprocess.run([
        ffmpeg_exe, '-y', '-i', 'temp_audio.wav',
        '-ac', '1', '-ar', '48000', '-acodec', 'dfpwm',
        output_path
    ])

    if os.path.exists('temp_audio.wav'):
        os.remove('temp_audio.wav')
    
    print(f"--- FERTIG! Gespeichert in {output_path} ---")

download_and_convert()