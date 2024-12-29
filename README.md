# Chordyzer ~~v0.5~~ v.0.3 - Musical analyzer from localfile songs ~~& YouTube links~~  

A python and HTML/CSS/JS based tool to **extract chords from any song**, 
which **creates a database to analyze and show** chord-key data by different criteria as *title*, *artist*, by *chord type*, *number of times* a chord appears; by song, by a group of songs or globally.

## REQUIREMENTS

- ([GitHub - ohollo/chord-extractor: Python library for extracting chords from multiple sound file formats](https://github.com/ohollo/chord-extractor)) needs to be compiled or added to your Python environment. Please note that Anaconda/Miniconda environments do not have access to this library.

- Python 3.9.x for modules' compatibility.
- Python libraries: numpy librosa chord-extractor json ~~yt-dlp~~
- `ffmpeg` package system-wide.

### Development in progress - To Do:

[ ] Fundamental scale detection: The current method, rooted in a mathematical analysis of semitonic intervals, is rather fragile due to the high tonal density of the twelve-tone equal temperament system. The inherent ambiguity of this system hinders the unambiguous identification of the underlying tonal scale.  
  
[ ] Scale database: The scale database and the associated comparison logic require a thorough overhaul. Currently, the high frequency of false positives, especially for scales like the Hungarians, highlights the need to refine the matching criteria.  
  
[ ]  Rhythm and meter detection: The excessive reliance on floating-point calculations in the rhythm and meter detection algorithms introduces undesirable variability in the results. Greater robustness is required in these modules to ensure more accurate and reliable detection, prior to tonal analysis.


### USAGE

- Run an analisys:
  
  ```
  $ python cho.py
  ```
  
- ~~Generate a chord list~~  
  
- Manage your database:  
  
  ```
  $ ./chords_database.html
  ```
![test_v0 3](https://github.com/user-attachments/assets/d84eb007-197e-48ea-b3f4-25d373c852e8)

## INCLUDES
 - Chord extracting from any MP3, WAV, MIDI file, ~~or directly a Youtube link~~.
 - Chord Visualizer with GUITAR diagrams, HTML5-webkit compatible.
 - ~~Chord carts transposing with live changing diagrams.~~
 - ~~Bar/Time Signatures counting, Tempo/BPM analyzer tool & live rhythm change.~~
 - ~~Keynote analysis on each bar, A4 referencial frequency identifier.~~
 - A database generation for analysing purposses capable of sorting chords, how many times used, the most and least used chords; by song, globally, ....
 - ~~Modular functions, python based, can be easilly added ... my framework works over numbers, and numbers, and their analyse~~.
 - The fewer external libraries and dependences used here, the better. Only chord-extractor and librosa for the audio analysing and controls. NumPy for anything numbers related. jQuery, Chart.js are also used for scripting database support.

The program generates:
1. _Artist_Title.html_ file. The visualizer of each song.
2. _chord_database.html_ and _chord_db.json_ files. A full database of all the song's with data analysis tools. Both files are updated automatically.

**In order to generatethe files both,  you are told to provide some info as:**
 *- ARTIST NAME*
 *- SONG TITLE*
![chordizer_info1](https://github.com/user-attachments/assets/edddabfb-23f0-4d63-b49c-1d4dd3900452)




Parked on 2024 September, 16th.
