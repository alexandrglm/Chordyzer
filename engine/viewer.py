from scales import scales
import os
import json
from chord_extractor.extractors import Chordino

def sanitize_filename(input_str):
    import unicodedata
    import re
    normalized = unicodedata.normalize('NFKD', input_str).encode('ASCII', 'ignore').decode('utf-8')
    sanitized = re.sub(r'[^\w\s-]', '', normalized)
    return sanitized.strip().replace(' ', '_')

def sanitize_url(url):
    from urllib.parse import quote
    return quote(url, safe='/:')

def generate_html_with_chords(audio_file, chords, artist_name, song_title, tempo, beat_times, tones_at_beats, keynote):
    sanitized_artist = sanitize_filename(artist_name)
    sanitized_title = sanitize_filename(song_title)
    output_file_name = f"{sanitized_artist}_{sanitized_title}.html"

    sanitized_audio_file = sanitize_url(audio_file)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="icon" href="./favicon.ico" sizes="any">
        <link rel="icon" href="./favicon.svg" type="image/svg+xml">
        <meta charset="UTF-8">
        <title>Chords from {artist_name} - {song_title}</title>
        <script src="./engine/scripts/script.js"></script>
        <link rel="stylesheet" type="text/css" href="./engine/scripts/style.css" />
    </head>
    <body>
    <header>
      <div>
        <h4>File: {sanitized_audio_file}</h4>
        <audio controls>
          <source src="{sanitized_audio_file}" type="audio/mpeg" />
          Your browser does not support the audio element.
        </audio>
        <label for="bpm-input">BPM:</label>
        <input type="number" id="bpm-input" class="bpm-input" value="{tempo}" step="1" min="30" max="300" />
        <button id="update-bpm">Update BPM</button>
        <button id="vel-up">BPM(+)</button>
        <button id="vel-down">BPM(-)</button>
        <div>
          <label for="keynote">Key:</label>
          <input type="text" id="keynote" class="keynote" value="{keynote}"  />
          <button id="transpose-up">Transpose Up (+)</button>
          <button id="transpose-down">Transpose Down (-)</button><br></br>
          Transpose: <span id="transpose-counter">0</span>, Capo:
          <span id="capo-counter">0</span>
          <input type="radio" id="guitar" name="instrument" value="guitar" checked />
          <label for="guitar">Guitar</label>
          <input type="radio" id="ukulele" name="instrument" value="ukulele" />
          <label for="ukulele">Ukulele</label>
        </div>
        <div id="dark-mode-toggle">
         <button id="toggle-dark-mode">Toggle Dark Mode</button>
        </div>
      </div>
      <div id="chord-diagram-bar">
        <img id="chord-diagram-current" src="./engine/diagrams/empty.png" />
        <h1 id="chord-current"></h1>
        <div style=" width: 2px; height: 100%; display: block; background: #8d94b4; margin: 15px; "></div>
        <img id="chord-diagram-next" src="./engine/diagrams/empty.png" />
        <h1 id="chord-next"></h1>
      </div>
    </header>
    <button id="zoom-in">zoom-in(+)</button>
    <button id="zoom-out">zoom-out(-)</button>
    <ul id="chords">
    """

    for chord in chords:
        timestamp = getattr(chord, 'timestamp', '0')
        chord_name = getattr(chord, 'chord', 'Unknown')
        html_content += f"<li id='{timestamp}'>{chord_name}</li>"

    html_content += """
        </ul>
        <h2>Tones at Beats</h2>
        <ul id="tones-at-beats">
    """
    for beat_time, tone in tones_at_beats:
        html_content += f"<li>Time: {beat_time:.2f}s - Tone: {tone}</li>"

    html_content += """
        </ul>
    </body>
    </html>
    """

    html_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', output_file_name)
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_file
