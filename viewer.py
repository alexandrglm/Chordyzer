import os
import json
from chord_extractor.extractors import Chordino
from engine.scales import scales
from db import generate_db_html

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

    html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Chords from {artist_name} - {song_title}</title>
    <script>
      document.addEventListener("DOMContentLoaded", function () {{
        const audio = document.querySelector("audio");
        const chords = document.querySelectorAll("#chords li");
        const transposeCounter = document.getElementById("transpose-counter");
        const transposeUpButton = document.getElementById("transposeUp");
        const transposeDownButton = document.getElementById("transposeDown");
        const capoCounter = document.getElementById("capo-counter");
        const keynoteInput = document.getElementById("keynote");
        const chordDiagramCurrent = document.getElementById("chord-diagram-current");
        const chordDiagramNext = document.getElementById("chord-diagram-next");
        const chordCurrent = document.getElementById("chord-current");
        const chordNext = document.getElementById("chord-next");
        const velUpButton = document.getElementById("velUp");
        const velDownButton = document.getElementById("velDown");
        const bpmInput = document.getElementById("bpmInput");
        const updateBPMButton = document.getElementById("updateBpm");
        const zoomInButton = document.getElementById("zoomIn");
        const zoomOutButton = document.getElementById("zoomOut");

        let maxChordLength = 0;
        let instrument = "guitar";
        let playbackRate = 1.0;
        let currentBPM = 120;

        chords.forEach((chord) => {{
          chord.addEventListener("click", function () {{
            audio.currentTime = chord.id;
            audio.play();
          }});
        }});

        document.querySelectorAll('input[name="instrument"]').forEach((input) => {{
          input.addEventListener("change", function () {{
            instrument = this.value;
          }});
        }});

        chords.forEach((chord, index) => {{
          var nextChord = chords[index + 1];
          if (nextChord) {{
            var length = nextChord.id - chord.id;
            chord.setAttribute("length", length);
            if (length > maxChordLength) {{
              maxChordLength = length;
            }}
          }}
        }});

        function updateChordWidth() {{
          chords.forEach((chord) => {{
            let length = chord.getAttribute("length");
            const n = 3;
            length = parseFloat(length).toFixed(n);
            let w = (length / maxChordLength.toFixed(n)) * 400;
            chord.style.width = w + "px";
          }});
        }}

        function updateAnimationDuration() {{
          chords.forEach((chord) => {{
            let length = chord.getAttribute("length");
            chord.style.setProperty("--animation-duration", (length / playbackRate) + "s");
          }});
        }}

        updateChordWidth();
        updateAnimationDuration();

        function scaleChordWidth(x) {{
          chords.forEach((chord) => {{
            let currentWidth = parseFloat(chord.style.width.replace("px", ""));
            chord.style.width = (currentWidth * x) + "px";
          }});
        }}

        zoomInButton.addEventListener("click", function () {{
          scaleChordWidth(1.5);
        }});

        zoomOutButton.addEventListener("click", function () {{
          scaleChordWidth(0.8);
        }});

        transposeUpButton.addEventListener("click", function () {{
          transposeChords(1);
          transposeCounter.innerHTML = parseInt(transposeCounter.innerHTML) + 1;
          capoCounter.innerHTML = transposeCounter.innerHTML * -1;
          updateKeynote(1);
        }});

        transposeDownButton.addEventListener("click", function () {{
          transposeChords(-1);
          transposeCounter.innerHTML = parseInt(transposeCounter.innerHTML) - 1;
          capoCounter.innerHTML = transposeCounter.innerHTML * -1;
          updateKeynote(-1);
        }});

        velUpButton.addEventListener("click", function () {{
          playbackRate = Math.min(playbackRate + 0.1, 2.0);
          audio.playbackRate = playbackRate;
          currentBPM = currentBPM * (playbackRate / (playbackRate - 0.1));
          bpmInput.value = Math.round(currentBPM);
          updateAnimationDuration();
        }});

        velDownButton.addEventListener("click", function () {{
          playbackRate = Math.max(playbackRate - 0.1, 0.5);
          audio.playbackRate = playbackRate;
          currentBPM = currentBPM * (playbackRate / (playbackRate + 0.1));
          bpmInput.value = Math.round(currentBPM);
          updateAnimationDuration();
        }});

        updateBPMButton.addEventListener("click", function () {{
          let newBPM = parseFloat(bpmInput.value);
          if (!isNaN(newBPM)) {{
            playbackRate = newBPM / currentBPM;
            playbackRate = Math.max(0.5, Math.min(2.0, playbackRate));
            audio.playbackRate = playbackRate;
            currentBPM = newBPM;
            updateAnimationDuration();
          }}
        }});

        setInterval(function () {{
          const currentTime = audio.currentTime;
          chords.forEach((chord) => {{
            if (chord.id <= currentTime) {{
              chord.classList.add("actived");
            }} else {{
              chord.classList.remove("actived");
              chord.classList.remove("active");
            }}

            if (chord.id - currentTime <= 0.3 && chord.id - currentTime >= 0) {{
              chord.classList.add("active");

              if (chordCurrent.innerHTML != chord.innerHTML) {{
                chordCurrent.innerHTML = chord.innerHTML;
                chordDiagramCurrent.src = `./engine/diagrams/${instrument}/${simplifyChord(chord.innerHTML)}.png`;
              }}

              if (chordNext.innerHTML != chord.nextElementSibling.innerHTML) {{
                chordNext.innerHTML = chord.nextElementSibling.innerHTML;
                chordDiagramNext.src = `./engine/diagrams/${instrument}/${simplifyChord(chord.nextElementSibling.innerHTML)}.png`;
              }}
            }}
          }});
        }}, 150);

        function transposeChords(amount) {{
          chords.forEach((chord) => {{
            chord.innerHTML = transposeChord(chord.innerHTML, amount);
          }});
        }}

        function transposeChord(chord, amount) {{
          var scale = [
            "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
          ];
          var normalizeMap = {{
            Cb: "B", Db: "C#", Eb: "D#", Fb: "E", Gb: "F#", Ab: "G#", Bb: "A#", "E#": "F", "B#": "C"
          }};
          return chord.replace(/[CDEFGAB](b|#)?/g, function (match) {{
            var i = (scale.indexOf(normalizeMap[match] ? normalizeMap[match] : match) + amount) % scale.length;
            return scale[i < 0 ? i + scale.length : i];
          }});
        }}

        function simplifyChord(chord) {{
          const chordMap = {{
            "C#": "Db", "C%23": "Db",
            "D#": "Eb", "D%23": "Eb",
            "F#": "Gb", "F%23": "Gb",
            "G#": "Ab", "G%23": "Ab",
            "A#": "Bb", "A%23": "Bb",
          }};

          return chord
            .replace(/\/.*/, "")
            .replace(/C%23|C#/g, "Db")
            .replace(/D%23|D#/g, "Eb")
            .replace(/F%23|F#/g, "Gb")
            .replace(/G%23|G#/g, "Ab")
            .replace(/A%23|A#/g, "Bb")
            .replace(/#/, "%23");
        }}

        function updateKeynote(amount) {{
          var scale = [
            "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
          ];
          let currentNote = keynoteInput.value;
          let currentIndex = scale.indexOf(currentNote);
          if (currentIndex === -1) return;

          let newIndex = (currentIndex + amount) % scale.length;
          if (newIndex < 0) newIndex += scale.length;
          keynoteInput.value = scale[newIndex];
        }}

        const table = document.getElementById('chords-table');
        if (table) {{
          const headers = table.querySelectorAll('th');
          headers.forEach((header, index) => {{
            header.addEventListener('click', () => {{
              const rows = Array.from(table.querySelectorAll('tbody tr'));
              const isAscending = header.classList.contains('asc');
              rows.sort((rowA, rowB) => {{
                const cellA = rowA.children[index].innerText;
                const cellB = rowB.children[index].innerText;
                if (isNaN(cellA)) {{
                  return cellA.localeCompare(cellB);
                }}
                return cellA - cellB;
              }});
              if (isAscending) {{
                rows.reverse();
              }}
              table.querySelector('tbody').append(...rows);
              headers.forEach(h => h.classList.remove('asc', 'desc'));
              header.classList.toggle('asc', !isAscending);
              header.classList.toggle('desc', isAscending);
            }});
          }});
        }}
      }});
    </script>
    <style>
      body {{
        margin: 0;
        background: #F08080;
        color: #424242;
        font-family: monospace;
      }}
      header {{
        display: grid;
        grid-template-columns: auto auto;
        height: 200px;
        position: sticky;
        top: 0;
        background: #F5F5F5;
        border-radius: 0 0 10px 10px;
        padding: 20px;
        box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
      }}

      #tempo-changes,
      #key-changes {{
        margin-top: 0px;
      }}

      .bpmInput {{
        width: 150px;
        height: 20px;
        font-size: 20px;
        padding: 5px;
        border-radius: 5px;
        border: 1px solid #ccc;
      }}

      .keynote {{
        width: 150px;
        height: 20px;
        font-size: 20px;
        padding: 5px;
        border-radius: 5px;
        border: 1px solid #ccc;
      }}

      .updateBpm,
      .velUp,
      .velDown,
      .transposeUp,
      .transposeDown {{
        background-color: #9E9D24;
        color: #FFFFFF;
        border: none;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
      }}

      .updateBpm:hover,
      .velUp:hover,
      .velDown:hover,
      .transposeUp:hover,
      .transposeDown:hover {{
        background-color: #7B7F0C;
      }}

      #chord-diagram-bar {{
        max-height: 150px;
        display: flex;
        align-items: flex-end;
        width: 378px;
      }}

      #chord-diagram-current,
      #chord-diagram-next {{
        height: 100%;
      }}

      #chord-diagram-next,
      #chord-next {{
        opacity: 0.7;
      }}

      ul#chords {{
        display: flex;
        padding: 10px;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 30px;
      }}

      ul#chords li {{
        list-style: none;
        background: #C6FF00;
        padding: 5px 10px;
        font-size: 20px;
        border-radius: 3px;
        cursor: pointer;
        color: #424242;
      }}

      ul#chords li.actived {{
        background: #FFFFFF;
      }}

      ul#chords li.active {{
        background: linear-gradient(to right, #FFFFFF 50%, #C6FF00 50%);
        background-size: 200% 100%;
        animation-name: slideBackground;
        --animation-duration: 1s;
        animation-duration: var(--animation-duration);
        animation-timing-function: linear;
      }}

      audio {{
        width: -webkit-fill-available;
      }}

      @keyframes slideBackground {{
        from {{
          background-position: right;
        }}
        to {{
          background-position: left;
        }}
      }}
    </style>
  </head>
  <body>
    <header>
      <div id="headerPart">
        <h4>File: {sanitized_audio_file}</h4>
        <audio controls>
          <source src="{sanitized_audio_file}" type="audio/mpeg" />
          Your browser does not support the audio element.
        </audio>
        <label for="bpmInput">BPM:</label>
        <input type="number" id="bpmInput" class="bpmInput" value="{tempo}" step="1" min="30" max="300" />
        <button id="updateBpm" class="updateBpm">Update BPM</button>
        <button id="velUp" class="velUp">BPM(+)</button>
        <button id="velDown" class="velDown">BPM(-)</button>
        <div>
          <label for="keynote">Key:</label>
          <input type="text" id="keynote" value="{keynote}" />
          <button id="transposeUp" class="transposeUp">Transpose Up (+)</button>
          <button id="transposeDown" class="transposeDown">Transpose Down (-)</button><br></br>
          Transpose: <span id="transpose-counter">0</span>, Capo:
          <span id="capo-counter">0</span>
          <input type="radio" id="guitar" name="instrument" value="guitar" checked />
          <label for="guitar">Guitar</label>
          <input type="radio" id="ukulele" name="instrument" value="ukulele" />
          <label for="ukulele">Ukulele</label>
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
    <button class="zoomIn" id="zoomIn">zoom-in(+)</button>
    <button class="zoomOut" id="zoomOut">zoom-out(-)</button>
    <ul id="chords"></ul>
  </body>
</html>"""

    html_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), output_file_name)
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_file
