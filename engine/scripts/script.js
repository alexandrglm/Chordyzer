// 2024 Oct, 31 Pending: Reordering & adding db js non-externals 

document.addEventListener("DOMContentLoaded", function () {
  // audio engine
  const audio = document.querySelector("audio";
  const chords = document.querySelectorAll("#chords li");
  // player 
  const darkModeToggle = document.getElementById("dark-mode-toggle"); /* revisar */
  const transposeCounter = document.getElementById("transpose-counter");
  const transposeUpButton = document.getElementById("transpose-up");
  const transposeDownButton = document.getElementById("transpose-down");
  const capoCounter = document.getElementById("capo-counter");
  const keynoteInput = document.getElementById("keynote");
  const chordDiagramCurrent = document.getElementById("chord-diagram-current");
  const chordDiagramNext = document.getElementById("chord-diagram-next");
  const chordCurrent = document.getElementById("chord-current");
  const chordNext = document.getElementById("chord-next");
  const velUpButton = document.getElementById("vel-up");
  const velDownButton = document.getElementById("vel-down");
  const bpmInput = document.getElementById("bpm-input");
  const updateBPMButton = document.getElementById("update-bpm");
  const zoomInButton = document.getElementById("zoom-in");
  const zoomOutButton = document.getElementById("zoom-out");
  // db
  /* const grepData1 = document.getElementById("Order by A"); */
  /* const grepData2 = document.getElementById("Order by B"); */
  /* const grepData3 = document.getElementById("Order by D"); */ 
  /* const grepData4 = document.getElementById("Order by X"); */

  let maxChordLength = 0;
  let instrument = "guitar"; "ukelele"
  let playbackRate = 1.0;
  let currentBPM = 120;

  // from const darkModeToggle
  function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
  }

  darkModeToggle.addEventListener("click", toggleDarkMode);

  /* player chord defs */
  chords.forEach((chord) => {
    chord.addEventListener("click", function () {
      audio.currentTime = chord.id;
      audio.play();
    });
  });

  document.querySelectorAll('input[name="instrument"]').forEach((input) => {
    input.addEventListener("change", function () {
      instrument = this.value;
    });
  });

  chords.forEach((chord, index) => {
    var nextChord = chords[index + 1];
    if (nextChord) {
      var length = nextChord.id - chord.id;
      chord.setAttribute("length", length);
      if (length > maxChordLength) {
        maxChordLength = length;
      }
    }
  });

  function updateChordWidth() {
    chords.forEach((chord) => {
      let length = chord.getAttribute("length");
      const n = 3;
      length = parseFloat(length).toFixed(n);
      let w = (length / maxChordLength.toFixed(n)) * 400;
      chord.style.width = w + "px";
    });
  }

  /* player chords slidedown */
  function updateAnimationDuration() {
    chords.forEach((chord) => {
      let length = chord.getAttribute("length");
      chord.style.setProperty("--animation-duration", (length / playbackRate) + "s");
    });
  }

  updateChordWidth();
  updateAnimationDuration();

  function scaleChordWidth(x) {
    chords.forEach((chord) => {
      let currentWidth = parseFloat(chord.style.width.replace("px", ""));
      chord.style.width = (currentWidth * x) + "px";
    });
  }

  /* player zoom/transpose/bpm buttons */
  zoomInButton.addEventListener("click", function () {
    scaleChordWidth(1.5);
  });

  zoomOutButton.addEventListener("click", function () {
    scaleChordWidth(0.8);
  });

  transposeUpButton.addEventListener("click", function () {
    transposeChords(1);
    transposeCounter.innerHTML = parseInt(transposeCounter.innerHTML) + 1;
    capoCounter.innerHTML = transposeCounter.innerHTML * -1;
    updateKeynote(1);
  });

  transposeDownButton.addEventListener("click", function () {
    transposeChords(-1);
    transposeCounter.innerHTML = parseInt(transposeCounter.innerHTML) - 1;
    capoCounter.innerHTML = transposeCounter.innerHTML * -1;
    updateKeynote(-1);
  });

  velUpButton.addEventListener("click", function () {
    playbackRate = Math.min(playbackRate + 0.1, 2.0);
    audio.playbackRate = playbackRate;
    currentBPM = currentBPM * (playbackRate / (playbackRate - 0.1));
    bpmInput.value = Math.round(currentBPM);
    updateAnimationDuration();
  });

  velDownButton.addEventListener("click", function () {
    playbackRate = Math.max(playbackRate - 0.1, 0.5);
    audio.playbackRate = playbackRate;
    currentBPM = currentBPM * (playbackRate / (playbackRate + 0.1));
    bpmInput.value = Math.round(currentBPM);
    updateAnimationDuration();
  });

  updateBPMButton.addEventListener("click", function () {
    let newBPM = parseFloat(bpmInput.value);
    if (!isNaN(newBPM)) {
      playbackRate = newBPM / currentBPM;
      playbackRate = Math.max(0.5, Math.min(2.0, playbackRate));
      audio.playbackRate = playbackRate;
      currentBPM = newBPM;
      updateAnimationDuration();
    }
  });

  /* from chords to player */
  setInterval(function () {
    const currentTime = audio.currentTime;
    chords.forEach((chord) => {
      if (chord.id <= currentTime) {
        chord.classList.add("actived");
      } else {
        chord.classList.remove("actived");
        chord.classList.remove("active");
      }

      if (chord.id - currentTime <= 0.3 && chord.id - currentTime >= 0) {
        chord.classList.add("active");

        if (chordCurrent.innerHTML != chord.innerHTML) {
          chordCurrent.innerHTML = chord.innerHTML;
          chordDiagramCurrent.src = `./engine/diagrams/${instrument}/${simplifyChord(chord.innerHTML)}.png`;
        }

        if (chordNext.innerHTML != chord.nextElementSibling.innerHTML) {
          chordNext.innerHTML = chord.nextElementSibling.innerHTML;
          chordDiagramNext.src = `./engine/diagrams/${instrument}/${simplifyChord(chord.nextElementSibling.innerHTML)}.png`;
        }
      }
    });
  }, 150);

  /* transpose code */
  function transposeChords(amount) {
    chords.forEach((chord) => {
      chord.innerHTML = transposeChord(chord.innerHTML, amount);
    });
  }

  /* fixing sharps; 2024 oct, 31: need to improve */
  /* three functions */
  function transposeChord(chord, amount) {
    var scale = [
      "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
    ];
    var normalizeMap = {
      Cb: "B", Db: "C#", Eb: "D#", Fb: "E", Gb: "F#", Ab: "G#", Bb: "A#", "E#": "F", "B#": "C"
    };
    return chord.replace(/[CDEFGAB](b|#)?/g, function (match) {
      var i = (scale.indexOf(normalizeMap[match] ? normalizeMap[match] : match) + amount) % scale.length;
      return scale[i < 0 ? i + scale.length : i];
    });
  }

  function simplifyChord(chord) {
    const chordMap = {
      "C#": "Db", "C%23": "Db",
      "D#": "Eb", "D%23": "Eb",
      "F#": "Gb", "F%23": "Gb",
      "G#": "Ab", "G%23": "Ab",
      "A#": "Bb", "A%23": "Bb",
    };

    return chord
      .replace(/\/.*/, "")
      .replace(/C%23|C#/g, "Db")
      .replace(/D%23|D#/g, "Eb")
      .replace(/F%23|F#/g, "Gb")
      .replace(/G%23|G#/g, "Ab")
      .replace(/A%23|A#/g, "Bb");
  }

  function updateKeynote(amount) {  /* real transposing to player */
    const scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    let currentNote = keynoteInput.value;
    let currentIndex = scale.indexOf(currentNote);
    if (currentIndex === -1) return;

    let newIndex = (currentIndex + amount) % scale.length;
    if (newIndex < 0) newIndex += scale.length;
    keynoteInput.value = scale[newIndex];
  }
});
