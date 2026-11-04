// Pure DSP: YIN cumulative mean normalized difference (de Cheveigné & Kawahara,
// 2002, doi:10.1121/1.1458024). No target-dependent frequency folding.
const NOTE_NAMES = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];
export const midiFrequency = (midi) => 440 * 2 ** ((midi - 69) / 12);
export const TUNINGS = Object.freeze({
  standard: { name: "Standard", midi: [40, 45, 50, 55, 59, 64] },
  dropD: { name: "Drop D", midi: [38, 45, 50, 55, 59, 64] },
  halfStep: { name: "Half step down", midi: [39, 44, 49, 54, 58, 63] },
});
export function tuningStrings(preset = "standard") {
  return (TUNINGS[preset] || TUNINGS.standard).midi.map((midi, index) => ({
    string: 6 - index, midi, key: `${NOTE_NAMES[midi % 12]}${Math.floor(midi / 12) - 1}`,
    frequency: midiFrequency(midi),
  }));
}
export const STANDARD_STRINGS = tuningStrings();

export function detectPitch(input, sampleRate, { noiseFloor = 0.006, minConfidence = 0.90 } = {}) {
  if (!input.length || !Number.isFinite(sampleRate) || sampleRate < 8000) return null;
  let mean = 0;
  for (const value of input) { if (!Number.isFinite(value)) return null; mean += value; }
  mean /= input.length;
  let energy = 0;
  for (const value of input) energy += (value - mean) ** 2;
  const rms = Math.sqrt(energy / input.length);
  if (rms < noiseFloor) return null;
  // The microphone's low-pass filter precedes this box-average decimation.
  const step = Math.max(1, Math.floor(sampleRate / 24000));
  const rate = sampleRate / step;
  const samples = new Float32Array(Math.floor(input.length / step));
  for (let i = 0; i < samples.length; i++) {
    let sum = 0;
    for (let j = 0; j < step; j++) sum += input[i * step + j] - mean;
    samples[i] = sum / step;
  }
  const minLag = Math.max(2, Math.floor(rate / 1400));
  const maxLag = Math.ceil(rate / 55);
  const size = Math.min(samples.length - maxLag - 1, Math.ceil(rate * 0.06));
  if (size < maxLag * 2) return null;
  const cmnd = new Float32Array(maxLag + 1);
  cmnd[0] = 1;
  let cumulative = 0;
  for (let lag = 1; lag <= maxLag; lag++) {
    let sum = 0;
    for (let i = 0; i < size; i++) {
      const delta = samples[i] - samples[i + lag];
      sum += delta * delta;
    }
    cumulative += sum;
    cmnd[lag] = cumulative ? sum * lag / cumulative : 1;
  }
  let lag = minLag;
  while (lag < maxLag && cmnd[lag] >= 0.12) lag++;
  if (lag >= maxLag) return null;
  while (lag < maxLag && cmnd[lag + 1] < cmnd[lag]) lag++;
  const minimum = (index) => {
    const left = cmnd[index-1], center = cmnd[index], right = cmnd[index+1];
    const curve = left - 2*center + right;
    return Math.max(0, center - (curve > 0 ? (left-right)**2/(8*curve) : 0));
  };
  // Strong overtones can cross YIN's threshold first. Adopt a longer period
  // only when its periodicity is materially better, without forcing a target.
  const first = lag;
  for (const multiple of [2, 3, 4]) {
    const center = first * multiple;
    if (center >= maxLag) break;
    let candidate = Math.round(center);
    const radius = Math.max(2, Math.round(center * 0.02));
    for (let i = Math.max(minLag, center - radius); i <= Math.min(maxLag - 1, center + radius); i++) {
      if (cmnd[i] < cmnd[candidate]) candidate = i;
    }
    // Compare interpolated minima: integer-lag rounding alone must not cause
    // a pure high note to be mistaken for its octave below.
    if (minimum(candidate) < minimum(lag) * 0.35 && minimum(lag) - minimum(candidate) > 0.006) lag = candidate;
  }
  const confidence = 1 - cmnd[lag];
  if (confidence < minConfidence || lag >= maxLag) return null;
  const denominator = cmnd[lag-1] - 2*cmnd[lag] + cmnd[lag+1];
  const coarse = lag + (denominator ? (cmnd[lag-1]-cmnd[lag+1])/(2*denominator) : 0);
  // Refine at the device sample rate to avoid decimation's high-note bias.
  const center = Math.round(coarse * step);
  const width = Math.min(input.length - center - step * 2 - 2, Math.ceil(sampleRate * 0.06));
  const difference = (offset) => {
    let sum = 0;
    for (let i = 0; i < width; i++) sum += (input[i] - input[i+offset]) ** 2;
    return sum;
  };
  let best = center, value = difference(center);
  for (let i = Math.max(2, center-step*2); i <= center+step*2; i++) {
    const next = difference(i);
    if (next < value) { best = i; value = next; }
  }
  const left = difference(best-1), right = difference(best+1);
  const curvature = left - 2*value + right;
  const period = best + (curvature ? Math.max(-.5, Math.min(.5, (left-right)/(2*curvature))) : 0);
  let frequency = sampleRate / period;
  if (!Number.isFinite(frequency) || frequency < 55 || frequency > 1400) return null;
  // Real strings have slightly stretched upper partials. YIN's period can be
  // pulled sharp by these; refine the *present fundamental* with a local Hann
  // spectral peak. The narrow search cannot change the detected note/octave.
  const weighted = new Float32Array(input.length);
  let weightSum = 0;
  for (let i=0; i<input.length; i++) {
    const weight = .5 - .5*Math.cos(2*Math.PI*i/(input.length-1));
    weighted[i] = (input[i]-mean)*weight; weightSum += weight;
  }
  const power = (hz) => {
    const angle = 2*Math.PI*hz/sampleRate, dc = Math.cos(angle), ds = Math.sin(angle);
    let c=1, s=0, real=0, imag=0;
    for (let i=0; i<weighted.length; i++) {
      real += weighted[i]*c; imag += weighted[i]*s;
      const next = c*dc - s*ds; s = s*dc + c*ds; c = next;
    }
    return real*real + imag*imag;
  };
  const lower = frequency*2**(-45/1200), upper = frequency*2**(45/1200);
  let a=lower, b=upper, c=b-(b-a)*.618033989, d=a+(b-a)*.618033989;
  let pc=power(c), pd=power(d);
  for (let i=0; i<16; i++) {
    if (pc>pd) { b=d; d=c; pd=pc; c=b-(b-a)*.618033989; pc=power(c); }
    else { a=c; c=d; pc=pd; d=a+(b-a)*.618033989; pd=power(d); }
  }
  const refined = (a+b)/2;
  if (2*Math.sqrt(Math.max(pc,pd))/weightSum > rms*.01 && refined>lower*1.001 && refined<upper/1.001) frequency=refined;
  return { frequency, confidence, rms };
}

export function describePitch(frequency, tolerance = 5) {
  const midi = Math.round(69 + 12 * Math.log2(frequency / 440));
  const cents = 1200 * Math.log2(frequency / midiFrequency(midi));
  const note = NOTE_NAMES[((midi % 12) + 12) % 12], octave = Math.floor(midi / 12) - 1;
  const inTune = Math.abs(cents) <= tolerance;
  return { note, octave, frequency, cents, midi,
    tuning: inTune ? "in-tune" : cents < 0 ? "flat" : "sharp",
    status: inTune ? "In tune" : cents < 0 ? "Flat · tighten slightly" : "Sharp · loosen slightly" };
}

export function describeStringPitch(frequency, selected = "auto", preset = "standard", tolerance = 5) {
  const detected = describePitch(frequency, tolerance);
  if (selected === "chromatic") return { ...detected, target: { key: `${detected.note}${detected.octave}`, frequency: midiFrequency(detected.midi) } };
  const strings = tuningStrings(preset);
  const target = strings.find((s) => String(s.string) === String(selected) || s.key === selected) ||
    strings.reduce((best, s) => Math.abs(Math.log2(frequency/s.frequency)) < Math.abs(Math.log2(frequency/best.frequency)) ? s : best);
  const cents = 1200 * Math.log2(frequency / target.frequency);
  const inTune = Math.abs(cents) <= tolerance;
  return { ...detected, target, cents, tuning: inTune ? "in-tune" : cents < 0 ? "flat" : "sharp",
    status: Math.abs(cents) > 200 ? "Check the string and octave before adjusting" :
      inTune ? "In tune" : cents < 0 ? "Flat · tighten slightly" : "Sharp · loosen slightly" };
}

export class PitchStabilizer {
  constructor() { this.reset(); }
  reset() { this.readings = []; this.smoothed = null; this.lastTime = null; }
  push(frequency, confidence = 1, now = performance.now()) {
    if (!Number.isFinite(frequency) || frequency <= 0 || confidence < .90) return null;
    if (this.lastTime !== null && now - this.lastTime > 150) this.reset();
    const midi = 69 + 12 * Math.log2(frequency / 440);
    if (this.readings.length && Math.abs(midi - this.readings.at(-1)) > .6) this.readings = [];
    this.readings.push(midi);
    if (this.readings.length > 5) this.readings.shift();
    const elapsed = this.lastTime === null ? 50 : now - this.lastTime;
    this.lastTime = now;
    if (this.readings.length < 3) return null;
    const median = [...this.readings].sort((a,b) => a-b)[Math.floor(this.readings.length/2)];
    const alpha = 1 - Math.exp(-elapsed/55);
    this.smoothed = this.smoothed === null || Math.abs(median-this.smoothed) > .6 ? median : this.smoothed + alpha*(median-this.smoothed);
    return midiFrequency(this.smoothed);
  }
}
