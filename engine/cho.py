import os
import json
from viewer import generate_html_with_chords
from db import generate_db_html
from music import extract_chords_from_audio, get_bpm, get_tone_at_beats, load_scales, match_chords_to_scales
from download_youtube_audio import download_audio_from_youtube
import re

DB_FILE = "chords_db.json"

def sanitize_filename(input_str):
    import unicodedata
    import re
    normalized = unicodedata.normalize('NFKD', input_str).encode('ASCII', 'ignore').decode('utf-8')
    sanitized = re.sub(r'[^\w\s-]', '', normalized)
    return sanitized.strip().replace(' ', '_')

def convert_ndarray_to_list(obj):
    import numpy as np
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [convert_ndarray_to_list(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_ndarray_to_list(v) for k, v in obj.items()}
    else:
        return obj

def update_chords_db(artist, title, chords, bpm, tempo_changes, tones_at_beats, matches):
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                chords_db = json.load(f)
        except json.JSONDecodeError:
            print("Error: Corrupted JSON...creating new json file")
            chords_db = []
    else:
        chords_db = []

    chord_counts = {}
    for chord in chords:
        chord_name = str(chord)
        chord_counts[chord_name] = chord_counts.get(chord_name, 0) + 1

    tempo_changes = convert_ndarray_to_list(tempo_changes)
    tones_at_beats_serializable = convert_ndarray_to_list(tones_at_beats)

    song_entry = {
        "artist": artist,
        "title": title,
        "chords": chord_counts,
        "bpm": bpm,
        "tempo_changes": tempo_changes,
        "tones_at_beats": tones_at_beats_serializable,
        "keynote": matches
    }

    chords_db.append(song_entry)

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(chords_db, f, indent=4, ensure_ascii=False)

    return song_entry

def is_youtube_url(url):
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    )
    return re.match(youtube_regex, url) is not None

def main():
    input_path = input("Enter the path to the audio file or YouTube URL: ")

    if is_youtube_url(input_path):
        artist_name = input("Enter the artist name: ")
        song_title = input("Enter the song title: ")
        output_dir = input("Enter the directory where the audio file should be saved: ")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        audio_file = download_audio_from_youtube(input_path, artist_name, song_title, output_dir)
    else:
        audio_file = input_path
        artist_name = input("Enter the artist name: ")
        song_title = input("Enter the song title: ")

        if not os.path.exists(audio_file):
            print("Error: File does not exist.")
            return

    tempo, beat_times = get_bpm(audio_file)
    print(f"BPM: {tempo}")
    print(f"Beat times: {beat_times}")

    tones_at_beats = get_tone_at_beats(audio_file, beat_times)

    print("Tones at detected beats:")
    for beat_time, tone in tones_at_beats:
        print(f"Time: {beat_time:.2f}s - Tone: {tone}")

    chords = extract_chords_from_audio(audio_file)

    keynote, matched_scales = match_chords_to_scales(chords, load_scales())
    print(f"Keynote: {keynote}")

    song_entry = update_chords_db(artist_name, song_title, chords, tempo, beat_times, tones_at_beats, matched_scales)

    html_file = generate_html_with_chords(audio_file, chords, artist_name, song_title, tempo, beat_times, tones_at_beats, keynote)
    print(f"Analysis complete. Results saved to {html_file}")

    generate_db_html()

if __name__ == "__main__":
    main()
