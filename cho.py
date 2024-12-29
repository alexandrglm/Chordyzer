import os
import json
import librosa
import numpy as np
from viewer import generate_html_with_chords
from db import generate_db_html
from chord_extractor.extractors import Chordino
from engine.scales import scales

DB_FILE = "chords_db.json"

def sanitize_filename(input_str):
    import unicodedata
    import re
    normalized = unicodedata.normalize('NFKD', input_str).encode('ASCII', 'ignore').decode('utf-8')
    sanitized = re.sub(r'[^\w\s-]', '', normalized)
    return sanitized.strip().replace(' ', '_')

def extract_chords_from_audio(audio_file):
    chordino = Chordino(roll_on=1.0)
    chords = chordino.extract(audio_file)
    return chords

def get_bpm(audio_file):
    y, sr = librosa.load(audio_file)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0] if tempo.size == 1 else tempo
    return tempo, beat_times

def get_reference_pitch_segment(y, sr, start_time, end_time):
    segment = y[int(sr * start_time): int(sr * end_time)]
    pitches, magnitudes = librosa.piptrack(y=segment, sr=sr)
    magnitude_median = np.median(magnitudes)
    a4_range = (440.0 * np.power(2, -0.5), 440.0 * np.power(2, 0.5))
    a4_frequencies = [pitches[i, j] for i in range(pitches.shape[0]) for j in range(pitches.shape[1])
                      if magnitudes[i, j] > magnitude_median and a4_range[0] <= pitches[i, j] <= a4_range[1]]
    return np.mean(a4_frequencies) if a4_frequencies else 440.0

def get_tone_from_frequencies(frequencies, reference_freq):
    if len(frequencies) == 0:
        return None
    tones = librosa.hz_to_midi(frequencies)
    median_tone = np.median(tones)
    return librosa.midi_to_note(median_tone)

def get_tone_at_beats(audio_file, beat_times):
    y, sr = librosa.load(audio_file)
    tones_at_beats = []
    for i, beat_time in enumerate(beat_times[:-1]):
        start_time = beat_time
        end_time = beat_times[i + 1]
        reference_freq = get_reference_pitch_segment(y, sr, start_time, end_time)
        segment = y[int(sr * start_time): int(sr * end_time)]
        pitches, magnitudes = librosa.piptrack(y=segment, sr=sr)
        magnitude_median = np.median(magnitudes)
        significant_pitches = pitches[magnitudes > magnitude_median]
        if significant_pitches.size > 0:
            tone = get_tone_from_frequencies(significant_pitches, reference_freq)
            tones_at_beats.append((beat_time, tone))
    return tones_at_beats

def convert_ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [convert_ndarray_to_list(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_ndarray_to_list(v) for k, v in obj.items()}
    else:
        return obj

def load_scales():
    return scales

def simplify_chord(chord_name):
    if '/' in chord_name:
        chord_name = chord_name.split('/')[0]
    return chord_name

def match_chords_to_scales(chords, scales, tolerance=0.1):
    chord_names = set(simplify_chord(chord.chord) for chord in chords)
    print(f"Simplified Chord names: {chord_names}")

    best_match = None
    best_match_score = 0
    matched_scales = {}
    for keynote, scale_types in scales.items():
        for scale_name, scale_notes in scale_types.items():
            scale_notes_set = set(scale_notes)
            print(f"Checking scale: Keynote: {keynote}, Scale: {scale_name}, Notes: {scale_notes_set}")

            intersection_count = len(chord_names.intersection(scale_notes_set))
            match_score = intersection_count / len(chord_names) if chord_names else 0
            print(f"Match score for Keynote {keynote}, Scale {scale_name}: {match_score}")

            if match_score >= tolerance:
                matched_scales[(keynote, scale_name)] = match_score
                if match_score > best_match_score:
                    best_match = keynote
                    best_match_score = match_score

    print(f"Best match: {best_match}, Best match score: {best_match_score}")

    matched_scales_str_keys = {f"{keynote}-{scale_name}": score for (keynote, scale_name), score in matched_scales.items()}
    return best_match, matched_scales_str_keys

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

def main():
    audio_file = input("Enter the path to the audio file: ")
    artist_name = input("ARTIST ?: ")
    song_title = input("SONG TITLE ?: ")

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
