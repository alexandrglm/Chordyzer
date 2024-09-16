import os
import librosa
import numpy as np
from chord_extractor.extractors import Chordino
from scales import scales

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

def simplify_chord(chord_name):
    if '/' in chord_name:
        chord_name = chord_name.split('/')[0]
    return chord_name

def match_chords_to_scales(chords, scales, tolerance=0.0150):
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

def load_scales():
    return scales
