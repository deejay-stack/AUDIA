// Microphone lifecycle and UI for the tuner only. No recordings or audio uploads.
import { detectPitch, describePitch, PitchStabilizer } from "./tuner_pitch.js";

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
    if (context) {
      context.onstatechange = null;
      if (context.state !== "closed") void context.close().catch(() => {});
    }
    stream = context = source = analyser = null;
    stabilizer.reset();
    clearPitch();
    find("microphone").textContent = "Microphone inactive";
    startButton.disabled = false;
    stopButton.disabled = true;
  }

  function renderPitch(frequency) {
    const pitch = describePitch(frequency);
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
      node.toggleAttribute("data-active", node.dataset.tuningNote === `${pitch.note}${pitch.octave}`);
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
      analyser.fftSize = 4096;
      source = audioContext.createMediaStreamSource(microphone);
      source.connect(analyser);
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
            const pitch = detectPitch(samples, audioContext.sampleRate);
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
  stopButton.addEventListener("click", () => { stopTuner(); find("error").hidden = true; });
  window.addEventListener("pagehide", stopTuner);
  document.addEventListener("visibilitychange", () => { if (document.hidden) stopTuner(); });
}
