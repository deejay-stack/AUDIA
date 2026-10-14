// Pure pitch calculations, separate from microphone controls and page rendering.
// YIN: de Cheveigné & Kawahara (2002), doi:10.1121/1.1458024.
const NOTE_NAMES = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];

export function detectPitch(input, sampleRate) {
  if (!input.length || !Number.isFinite(sampleRate) || sampleRate <= 0) return null;
  let mean = 0;
  for (const value of input) mean += value;
  mean /= input.length;
  let energy = 0;
  for (const value of input) energy += (value - mean) ** 2;
  if (Math.sqrt(energy / input.length) < 0.008) return null;

  // Average groups of samples to reduce work while preserving guitar pitches.
  const step = Math.max(1, Math.floor(sampleRate / 12000));
  const rate = sampleRate / step;
  const samples = new Float32Array(Math.floor(input.length / step));
  for (let index = 0; index < samples.length; index++) {
    let sum = 0;
    for (let offset = 0; offset < step; offset++) sum += input[index * step + offset] - mean;
    samples[index] = sum / step;
  }
  const minLag = Math.floor(rate / 420);
  const maxLag = Math.ceil(rate / 65);
  const windowSize = samples.length - maxLag - 1;
  if (windowSize < maxLag) return null;
  const difference = new Float32Array(maxLag + 1);
  difference[0] = 1;
  let runningSum = 0;
  for (let lag = 1; lag <= maxLag; lag++) {
    let sum = 0;
    for (let index = 0; index < windowSize; index++) {
      const delta = samples[index] - samples[index + lag];
      sum += delta * delta;
    }
    runningSum += sum;
    // Cumulative mean normalized difference rejects nonperiodic input.
    difference[lag] = runningSum ? (sum * lag) / runningSum : 1;
  }
  let lag = minLag;
  while (lag < maxLag && difference[lag] >= 0.15) lag++;
  if (lag >= maxLag) return null;
  while (lag + 1 <= maxLag && difference[lag + 1] < difference[lag]) lag++;
  if (lag >= maxLag) return null;
  const left = difference[lag - 1];
  const center = difference[lag];
  const right = difference[lag + 1];
  const denominator = left - 2 * center + right;
  const refinedLag = lag + (denominator ? (left - right) / (2 * denominator) : 0);
  const frequency = rate / refinedLag;
  if (!Number.isFinite(frequency) || frequency < 65 || frequency > 420) return null;
  return { frequency, confidence: 1 - center };
}

export function describePitch(frequency) {
  const midi = Math.round(69 + 12 * Math.log2(frequency / 440));
  const target = 440 * 2 ** ((midi - 69) / 12);
  const cents = 1200 * Math.log2(frequency / target);
  const note = NOTE_NAMES[((midi % 12) + 12) % 12];
  const octave = Math.floor(midi / 12) - 1;
  const magnitude = Math.abs(cents);
  const status = magnitude <= 5 ? "In Tune"
    : cents < 0 ? (magnitude <= 15 ? "Slightly Flat" : "Too Flat")
    : magnitude <= 15 ? "Slightly Sharp" : "Too Sharp";
  return { note, octave, frequency, cents, status,
    tuning: magnitude <= 5 ? "in-tune" : cents < 0 ? "flat" : "sharp" };
}

export class PitchStabilizer {
  constructor() { this.reset(); }
  reset() { this.readings = []; this.smoothed = null; }
  push(frequency) {
    const semitones = 69 + 12 * Math.log2(frequency / 440);
    if (this.readings.length && Math.abs(semitones - this.readings.at(-1)) > 0.35) {
      this.readings = [];
    }
    this.readings.push(semitones);
    if (this.readings.length > 5) this.readings.shift();
    if (this.readings.length < 3) return null;
    const sorted = [...this.readings].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];
    this.smoothed = this.smoothed === null || Math.abs(median - this.smoothed) > 0.5
      ? median : this.smoothed * 0.6 + median * 0.4;
    return 440 * 2 ** ((this.smoothed - 69) / 12);
  }
}
