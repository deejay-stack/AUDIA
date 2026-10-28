// Microphone lifecycle and UI for the tuner only. No recordings or audio uploads.
import { detectPitch, describeStringPitch, STANDARD_STRINGS, PitchStabilizer } from "./tuner_pitch.js";

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

  function clearPitch() {
    find("note").textContent = "—";
    find("octave").textContent = "";
    find("frequency").textContent = "— Hz";
    find("cents").textContent = "— cents";
    find("status").textContent = "Play a string";
    find("indicator").hidden = true;
    find("meter").setAttribute("aria-valuenow", "0");
    find("meter").setAttribute("aria-valuetext", "No reliable pitch");
    delete container.dataset.tuning;
    page.querySelectorAll("[data-tuning-note]").forEach((node) => delete node.dataset.active);
  }

  function showError(state, message) {
    find("microphone").textContent = state;
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
    find("microphone").textContent = "Microphone inactive";
    startButton.disabled = false;
    stopButton.disabled = true;
  }

  function renderPitch(frequency) {
    const pitch = describeStringPitch(frequency, find("target-string").value);
    find("target").textContent = `Target ${pitch.target.key} · ${pitch.target.frequency.toFixed(2)} Hz`;
    find("note").textContent = pitch.note;
    find("octave").textContent = pitch.octave;
    find("frequency").textContent = `${pitch.frequency.toFixed(1)} Hz`;
    const rounded = Math.round(pitch.cents);
    find("cents").textContent = `${rounded > 0 ? "+" : ""}${rounded === 0 ? 0 : rounded} cents`;
    find("status").textContent = pitch.status;
    container.dataset.tuning = pitch.tuning;
    const cents = Math.max(-50, Math.min(50, pitch.cents));
    find("indicator").hidden = false;
    positionIndicator(find("indicator"), 50 + cents);
    find("meter").setAttribute("aria-valuenow", cents.toFixed(1));
    find("meter").setAttribute("aria-valuetext", `${pitch.note}${pitch.octave}, ${rounded} cents, ${pitch.status}`);
    page.querySelectorAll("[data-tuning-note]").forEach((node) => {
      node.toggleAttribute("data-active", node.dataset.tuningNote === pitch.target.key);
    });
  }

  async function startTuner() {
    if (active || pending) return;
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
    find("microphone").textContent = "Requesting microphone";
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
      analyser.fftSize = Math.min(32768, 2 ** Math.ceil(Math.log2(audioContext.sampleRate * 0.09)));
      source = audioContext.createMediaStreamSource(microphone);
      highpass = audioContext.createBiquadFilter();
      highpass.type = "highpass"; highpass.frequency.value = 55; highpass.Q.value = 0.7;
      lowpass = audioContext.createBiquadFilter();
      lowpass.type = "lowpass"; lowpass.frequency.value = find("instrument").value === "electric" ? 1000 : 1400; lowpass.Q.value = 0.7;
      source.connect(highpass).connect(lowpass).connect(analyser);
      // No connection to destination: the microphone never plays through speakers.
      const samples = new Float32Array(analyser.fftSize);
      active = true;
      pending = false;
      lastRead = 0;
      lastReliable = performance.now();
      find("microphone").textContent = "Listening";
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
        // About twelve estimates per second keeps processing light on phones.
        if (now - lastRead >= 80) {
          lastRead = now;
          try {
            analyser.getFloatTimeDomainData(samples);
            const electric = find("instrument").value === "electric";
            const pitch = detectPitch(samples, audioContext.sampleRate, { noiseFloor: electric ? 0.004 : 0.008 });
            const frequency = pitch ? stabilizer.push(pitch.frequency) : null;
            if (frequency) { renderPitch(frequency); lastReliable = now; }
            if (now - lastReliable > 650) {
              stabilizer.reset();
              clearPitch();
              lastReliable = now;
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

  startButton.addEventListener("click", startTuner);
  function selectTarget() {
    stabilizer.reset(); clearPitch();
    const selected = STANDARD_STRINGS.find((string) => string.key === find("target-string").value);
    find("target").textContent = selected ? `Target ${selected.key} · ${selected.frequency.toFixed(2)} Hz` : "Automatic standard-string detection";
    page.querySelectorAll("[data-tuning-note]").forEach((node) => node.toggleAttribute("data-selected", node.dataset.tuningNote === selected?.key));
  }
  find("target-string").addEventListener("change", selectTarget);
  find("instrument").addEventListener("change", () => {
    stabilizer.reset(); clearPitch();
    if (lowpass) lowpass.frequency.value = find("instrument").value === "electric" ? 1000 : 1400;
  });
  page.querySelectorAll("[data-string-target]").forEach((button) => button.addEventListener("click", () => {
    find("target-string").value = button.dataset.stringTarget; selectTarget();
  }));
  stopButton.addEventListener("click", () => { stopTuner(); find("error").hidden = true; });
  window.addEventListener("pagehide", stopTuner);
  const onVisibility = () => { if (document.hidden) stopTuner(); };
  document.addEventListener("visibilitychange", onVisibility);
  return { destroy() { stopTuner(); window.removeEventListener("pagehide", stopTuner); document.removeEventListener("visibilitychange", onVisibility); } };
}
