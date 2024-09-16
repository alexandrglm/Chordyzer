import librosa
import numpy as np
from scipy import stats
import os

def smooth_intervals(intervals, window_size=5):
    if len(intervals) < window_size:
        return intervals
    return np.convolve(intervals, np.ones(window_size)/window_size, mode='valid')

def determine_meter(beat_times, estimated_bpm):
    if len(beat_times) < 2:
        return "Unknown"

    measure_duration = 60 / estimated_bpm

    durations = np.diff(beat_times)
    mean_duration = np.mean(durations)

    tolerance = 0.05

    if abs(mean_duration - measure_duration) < tolerance:
        return "4/4"
    elif abs(mean_duration - measure_duration * (3 / 4)) < tolerance:
        return "3/4"
    elif abs(mean_duration - measure_duration * (3 / 3)) < tolerance:
        return "3/3"
    else:
        return "Unknown"

def analyze_beats_and_meter(audio_file):
    y, sr = librosa.load(audio_file, sr=22050 * 2)

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    beat_intervals = np.diff(beat_times)

    smoothed_intervals = smooth_intervals(beat_intervals)

    tempo_value = tempo[0] if isinstance(tempo, np.ndarray) else tempo
    bpm_real = tempo_value
    bpm_fixed = round(bpm_real)

    meter = determine_meter(beat_times, bpm_real)

    total_duration = librosa.get_duration(y=y, sr=sr)
    measures = round(total_duration * bpm_fixed / 60)

    if bpm_fixed > 0 and measures > 0:
        measure_duration = 60 / bpm_fixed
        measure_times = [i * measure_duration for i in range(measures)]
    else:
        measure_times = []

    return bpm_real, bpm_fixed, measures, meter, measure_times

def main():
    audio_file = input("MP3 PATH?: ")
    bpm_real, bpm_fixed, measures, meter, measure_times = analyze_beats_and_meter(audio_file)

    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    output_file = f"./{base_name}_analysis.txt"

    with open(output_file, "w") as f:
        f.write(f"BPM real: {bpm_real:.6f}\n")
        f.write(f"BPM fixed: {bpm_fixed}\n")
        f.write(f"Bar estimated: {measures}\n")
        f.write(f"Bar type estimated: {meter}\n")
        f.write(f"Bar timestampt:\n")
        for i, time in enumerate(measure_times):
            f.write(f"Bar {i + 1}: {time:.6f}s\n")

    print(f"saved at {output_file}")

if __name__ == "__main__":
    main()
