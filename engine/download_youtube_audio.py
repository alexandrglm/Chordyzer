import os
import yt_dlp as youtube_dl
from pydub import AudioSegment

def download_audio_from_youtube(youtube_url, artist, title, output_dir):
    artist = artist.replace('/', '_').replace('\\', '_')
    title = title.replace('/', '_').replace('\\', '_')

    filename = f"{artist} - {title}.mp3"
    output_path = os.path.join(output_dir, filename)

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': output_path,
        'noplaylist': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(youtube_url, download=True)

    return output_path

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube URL: ")
    artist = input("Enter the artist name: ")
    title = input("Enter the song title: ")
    output_dir = input("Enter the directory where the audio file should be saved: ")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    audio_file_path = download_audio_from_youtube(youtube_url, artist, title, output_dir)
    print(f"Audio file saved to: {audio_file_path}")
