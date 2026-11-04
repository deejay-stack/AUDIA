// Live microphone stays local. Recorded reference playback always stops the mic.
import { detectPitch, describeStringPitch, STANDARD_STRINGS, tuningStrings, PitchStabilizer } from "./tuner_pitch.js";
import { guitarAudio, referenceURL } from "../shared/guitar_audio.js";

// Only the visual marker position is dynamic. Its timing is owned by tuner_meter.css.
const indicatorPositions = new WeakMap();
function positionIndicator(node, percent) {
  const previous = indicatorPositions.get(node);
  if (previous?.percent === percent) return;
  const style = getComputedStyle(node);
  const start = style.left;
  const duration = parseFloat(style.transitionDuration) * 1000;
  const easing = style.transitionTimingFunction;
  previous?.animation.cancel();
  const animation = node.animate([{ left: start }, { left: `${percent}%` }], {
    duration, easing, fill: "forwards",
  });
  indicatorPositions.set(node, { animation, percent });
}

export function mountTuner(page) {
  const find = (id) => page.querySelector(`#tuner-${id}`);
  const say = (id, value) => { const node = find(id); if (node.textContent !== value) node.textContent = value; };
  const startButton = find("start");
  const stopButton = find("stop");
  const container = page.querySelector(".tuner-container");
  const stabilizer = new PitchStabilizer();
  let stream = null;
  let context = null;
  let source = null;
  let analyser = null;
  let highpass = null, lowpass = null;
  let frame = null;
  let generation = 0;
  let active = false;
  let pending = false;
  let lastRead = 0;
  let lastReliable = 0;
  let lastSignal = 0;
  let referenceButton = null;
  const listeners = new AbortController();
  const on = (node, event, handler) => node.addEventListener(event, handler, { signal: listeners.signal });

  function clearPitch() {
    find("note").textContent = "—";
    find("octave").textContent = "";
    find("frequency").textContent = "— Hz";
    find("cents").textContent = "— cents";
    say("status", "Play a string");
    find("quality").textContent = "Waiting for a clear note";
    find("indicator").hidden = true;
    find("meter").setAttribute("aria-valuenow", "0");
    find("meter").setAttribute("aria-valuetext", "No reliable pitch");
    delete container.dataset.tuning;
    page.querySelectorAll("[data-tuning-string]").forEach((node) => delete node.dataset.active);
  }

  function showError(state, message) {
    say("microphone", state);
    find("error").textContent = message;
    find("error").hidden = false;
  }

  function stopTuner() {
    generation++;
    active = false;
    pending = false;
    cancelAnimationFrame(frame);
    frame = null;
    if (stream) stream.getTracks().forEach((track) => track.stop());
    if (source) source.disconnect();
    if (analyser) analyser.disconnect();
    highpass?.disconnect();
    lowpass?.disconnect();
    if (context) {
      context.onstatechange = null;
      if (context.state !== "closed") void context.close().catch(() => {});
    }
    stream = context = source = analyser = null;
    highpass = lowpass = null;
    stabilizer.reset();
    clearPitch();
    say("microphone", "Microphone inactive");
    startButton.disabled = false;
    stopButton.disabled = true;
  }

  function renderPitch(frequency) {
    const pitch = describeStringPitch(frequency, find("target-string").value, find("preset").value);
    find("target").textContent = `Target ${pitch.target.key} · ${pitch.target.frequency.toFixed(2)} Hz`;
    find("note").textContent = pitch.note;
    find("octave").textContent = pitch.octave;
    find("frequency").textContent = `${pitch.frequency.toFixed(1)} Hz`;
    const rounded = Math.round(pitch.cents);
    find("cents").textContent = `${rounded > 0 ? "+" : ""}${rounded === 0 ? 0 : rounded} cents`;
    say("status", pitch.status);
    container.dataset.tuning = pitch.tuning;
    const cents = Math.max(-50, Math.min(50, pitch.cents));
    find("indicator").hidden = false;
    positionIndicator(find("indicator"), 50 + cents);
    find("meter").setAttribute("aria-valuenow", cents.toFixed(1));
    find("meter").setAttribute("aria-valuetext", `${pitch.note}${pitch.octave}, ${rounded} cents, ${pitch.status}`);
    page.querySelectorAll("[data-tuning-string]").forEach((node) => {
      node.toggleAttribute("data-active", Number(node.dataset.tuningString) === pitch.target.string);
    });
  }

  async function startTuner() {
    if (active || pending) return;
    guitarAudio.stop();
    find("error").hidden = true;
    if (!window.isSecureContext) {
      showError("Microphone unavailable", "Microphone access requires HTTPS or localhost. Open AUDIA using a secure address.");
      return;
    }
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!navigator.mediaDevices?.getUserMedia || !AudioContextClass) {
      showError("Microphone unavailable", "Your browser does not support the audio features required by the tuner.");
      return;
    }
    const ticket = ++generation;
    pending = true;
    startButton.disabled = true;
    stopButton.disabled = false;
    say("microphone", "Requesting microphone");
    try {
      // Resume directly from the button gesture, including on mobile browsers.
      const audioContext = new AudioContextClass();
      context = audioContext;
      await audioContext.resume();
      if (ticket !== generation) return;
      const microphone = await navigator.mediaDevices.getUserMedia({ audio: {
        echoCancellation: false, noiseSuppression: false, autoGainControl: false,
      } });
      // Stop may be pressed while the browser's permission prompt is still open.
      if (ticket !== generation) {
        microphone.getTracks().forEach((track) => track.stop());
        return;
      }
      stream = microphone;
      analyser = audioContext.createAnalyser();
      // Keep enough waveform cycles even on high-sample-rate audio devices.
      analyser.fftSize = Math.min(32768, 2 ** Math.ceil(Math.log2(audioContext.sampleRate * 0.12)));
      source = audioContext.createMediaStreamSource(microphone);
      highpass = audioContext.createBiquadFilter();
      highpass.type = "highpass"; highpass.frequency.value = 35; highpass.Q.value = 0.7;
      lowpass = audioContext.createBiquadFilter();
      lowpass.type = "lowpass"; lowpass.frequency.value = 2000; lowpass.Q.value = 0.7;
      source.connect(highpass).connect(lowpass).connect(analyser);
      // No connection to destination: the microphone never plays through speakers.
      const samples = new Float32Array(analyser.fftSize);
      active = true;
      pending = false;
      lastRead = 0;
      lastReliable = performance.now();
      lastSignal = lastReliable;
      // Allow room/speaker decay after stopping a reference before measuring.
      const readyAt = lastReliable + 350;
      say("microphone", "Listening");
      microphone.getTracks().forEach((track) => track.addEventListener("ended", () => {
        if (ticket !== generation) return;
        stopTuner();
        showError("Microphone unavailable", "The microphone was disconnected. Reconnect it and start the tuner again.");
      }, { once: true }));
      audioContext.onstatechange = () => {
        if (!active || ticket !== generation || audioContext.state === "running") return;
        stopTuner();
        showError("Microphone inactive", "Audio was interrupted. Press Start Tuner to listen again.");
      };

      function listen(now) {
        if (!active || ticket !== generation) return;
        if (now >= readyAt && now - lastRead >= 50) {
          lastRead = now;
          try {
            analyser.getFloatTimeDomainData(samples);
            const baseFloor = find("instrument").value === "electric" ? .003 : .006;
            const noiseFloor = baseFloor * 2 ** ((50-Number(find("sensitivity").value))/20);
            const pitch = detectPitch(samples, audioContext.sampleRate, { noiseFloor });
            const frequency = pitch ? stabilizer.push(pitch.frequency, pitch.confidence, now) : null;
            if (pitch) { lastSignal = now; say("microphone", "Listening · signal detected"); }
            else if (now-lastSignal > 150) stabilizer.reset();
            if (frequency) {
              renderPitch(frequency); lastReliable = now;
              find("quality").textContent = `Periodicity ${Math.round(pitch.confidence*100)}% · A4 = 440 Hz`;
            }
            if (now - lastReliable > 350) {
              clearPitch();
              say("microphone", "Listening · pluck one string");
            }
          } catch {
            stopTuner();
            showError("Microphone unavailable", "Audio could not be processed. Stop other audio apps and try again.");
            return;
          }
        }
        frame = requestAnimationFrame(listen);
      }
      frame = requestAnimationFrame(listen);
    } catch (error) {
      if (ticket !== generation) return;
      stopTuner();
      if (["NotAllowedError", "PermissionDeniedError", "SecurityError"].includes(error.name)) {
        showError("Permission denied", "Microphone access is required to use the guitar tuner. Please allow microphone access in your browser settings.");
      } else if (["NotFoundError", "DevicesNotFoundError"].includes(error.name)) {
        showError("Microphone unavailable", "No microphone was detected on this device.");
      } else {
        showError("Microphone unavailable", "The microphone could not be started. It may be in use by another app. Close it and try again.");
      }
    }
  }

  on(startButton, "click", startTuner);
  function selectTarget() {
    stabilizer.reset(); clearPitch();
    const strings = tuningStrings(find("preset").value);
    const selected = strings.find((string) => String(string.string) === find("target-string").value);
    find("target").textContent = selected ? `Target ${selected.key} · ${selected.frequency.toFixed(2)} Hz` :
      find("target-string").value === "chromatic" ? "Chromatic · nearest note · A4 = 440 Hz" : "Automatic open-string detection · A4 = 440 Hz";
    strings.forEach((string) => {
      const row = page.querySelector(`[data-tuning-string="${string.string}"]`);
      row.toggleAttribute("data-selected", string.string === selected?.string);
      row.querySelector("strong").textContent = string.key;
      row.querySelector("[data-string-frequency]").textContent = `${string.frequency.toFixed(2)} Hz`;
      const button = row.querySelector("button");
      button.setAttribute("aria-pressed", String(string.string === selected?.string));
      button.setAttribute("aria-label", `Select string ${string.string}, ${string.key}, and play its recorded reference`);
      find("target-string").querySelector(`[value="${string.string}"]`).textContent = `String ${string.string} · ${string.key}`;
    });
  }
  on(find("target-string"), "change", selectTarget);
  on(find("preset"), "change", () => { guitarAudio.stop(); selectTarget(); });
  on(find("sensitivity"), "input", () => { stabilizer.reset(); clearPitch(); });
  on(find("instrument"), "change", () => {
    guitarAudio.stop();
    stabilizer.reset(); clearPitch();
  });
  page.querySelectorAll("[data-string-target]").forEach((button) => on(button, "click", () => {
    if (referenceButton === button && guitarAudio.current) { guitarAudio.stop(); return; }
    stopTuner();
    find("error").hidden = true;
    find("target-string").value = button.dataset.stringTarget;
    selectTarget();
    const index = 6 - Number(button.dataset.stringTarget);
    const target = tuningStrings(find("preset").value)[index];
    const original = STANDARD_STRINGS[index];
    void guitarAudio.play({
      url: referenceURL(find("instrument").value, original.key),
      rate: target.frequency/original.frequency,
      onState(state, message) {
        const playing = state === "playing", loading = state === "loading";
        if (loading) referenceButton = button;
        button.toggleAttribute("data-playing", playing);
        button.setAttribute("aria-busy", String(loading));
        button.querySelector("[data-reference-label]").textContent = loading ? "Loading… tap to cancel" : playing ? "Stop reference" : "Play reference";
        find("reference-status").textContent = loading ? "Loading recorded guitar…" : playing ?
          `${target.key} reference playing · microphone off` : state === "error" ? message : "Reference stopped. Press Start Tuner to listen to your guitar.";
        if (!playing && !loading) referenceButton = null;
      },
    });
  }));
  on(stopButton, "click", () => { stopTuner(); guitarAudio.stop(); find("error").hidden = true; });
  const stopAll = () => { stopTuner(); void guitarAudio.dispose(); };
  on(window, "pagehide", stopAll);
  on(document, "visibilitychange", () => { if (document.hidden) stopAll(); });
  selectTarget();
  return { destroy() { stopAll(); listeners.abort(); } };
}
