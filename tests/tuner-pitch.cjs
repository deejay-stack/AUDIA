// Run with node tests/tuner-pitch.cjs. No microphone or npm dependency required.
const assert = require('node:assert/strict');
const fs = require('node:fs');

(async () => {
  const code = fs.readFileSync('assets/js/tuner/tuner_pitch.js', 'utf8');
  const { detectPitch, describePitch, PitchStabilizer } = await import(
    'data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
  const targets = [[82.406889, 'E', 2], [110, 'A', 2], [146.832384, 'D', 3],
    [195.997718, 'G', 3], [246.941651, 'B', 3], [329.627557, 'E', 4]];
  for (const rate of [44100, 48000, 96000]) {
    for (const [target, note, octave] of targets) {
      for (const cents of [-25, -10, 0, 10, 25]) {
        const frequency = target * 2 ** (cents / 1200);
        // A plucked-string-like signal with harmonics and a decaying envelope.
        const samples = Float32Array.from({ length: 4096 }, (_, index) => {
          const phase = 2 * Math.PI * frequency * index / rate;
          return Math.exp(-index / rate * 3) * (.2 * Math.sin(phase) + .12 * Math.sin(phase * 2) + .06 * Math.sin(phase * 3));
        });
        const detected = detectPitch(samples, rate);
        assert.ok(detected, `${note}${octave}, ${cents} cents, ${rate} Hz`);
        const pitch = describePitch(detected.frequency);
        assert.equal(pitch.note, note); assert.equal(pitch.octave, octave);
        assert.ok(Math.abs(pitch.cents - cents) < 2, `Pitch error: ${pitch.cents - cents} cents`);
        assert.equal(pitch.status, cents === 0 ? 'In Tune' : cents < -15 ? 'Too Flat'
          : cents < 0 ? 'Slightly Flat' : cents > 15 ? 'Too Sharp' : 'Slightly Sharp');
      }
    }
  }
  assert.equal(detectPitch(new Float32Array(4096), 48000), null);
  assert.equal(detectPitch(new Float32Array(4096).fill(.2), 48000), null, 'DC input');
  assert.equal(detectPitch(Float32Array.from({ length: 4096 }, (_, i) => .001 * Math.sin(i)), 48000), null);
  let seed = 123;
  const noise = Float32Array.from({ length: 4096 }, () => {
    seed = (1664525 * seed + 1013904223) >>> 0;
    return (seed / 2 ** 32 - .5) * .3;
  });
  assert.equal(detectPitch(noise, 48000), null, 'Broadband noise');
  const smoother = new PitchStabilizer();
  assert.equal(smoother.push(110), null); assert.equal(smoother.push(110.1), null);
  assert.ok(Math.abs(smoother.push(110) - 110) < .1);
  assert.equal(smoother.push(196), null, 'One outlier cannot change the note');
  assert.equal(smoother.push(110), null); smoother.push(110);
  assert.ok(Math.abs(smoother.push(110) - 110) < .1);
  smoother.reset(); assert.equal(smoother.push(82.4), null);
  console.log('PASS: 90 harmonic pitch cases across six strings, three sample rates, flat/sharp/in-tune; silence, weak input, noise and stabilization');
})().catch(error => { console.error(error); process.exitCode = 1; });
