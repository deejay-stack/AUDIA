// One lazy, cancellable recorded-audio voice shared by catalog and tuner.
// No context, download or playback occurs until play() is called by a click.
export const CATEGORY_AUDIO = Object.freeze({ Acoustic: "acoustic", Electric: "electric", Classical: "classical" });
export const referenceURL = (instrument, note) => `/static/audio/guitars/${instrument}/reference/${note}.m4a`;
export const previewURL = (category) => Object.hasOwn(CATEGORY_AUDIO, category) ? `/static/audio/guitars/${CATEGORY_AUDIO[category]}/previews/open-strings.m4a` : null;

export class RecordedGuitarPlayer {
  constructor() { this.context = null; this.current = null; this.cache = new Map(); }
  stop() {
    const current = this.current;
    this.current = null;
    if (!current) return;
    current.abort.abort();
    if (current.source) { current.source.onended = null; try { current.source.stop(); } catch { /* Already ended. */ } current.source.disconnect(); }
    current.gain?.disconnect();
    current.onState("stopped");
  }
  async play({ url, rate = 1, onState = () => {} }) {
    this.stop();
    const current = { abort: new AbortController(), source: null, onState };
    this.current = current;
    onState("loading");
    try {
      const AudioCtx = globalThis.AudioContext || globalThis.webkitAudioContext;
      if (!AudioCtx) throw new Error("Recorded audio is not supported in this browser.");
      if (!this.context || this.context.state === "closed") {
        this.context = new AudioCtx();
        this.context.onstatechange = () => {
          if (this.current?.source && this.context?.state !== "running") {
            const notify = this.current.onState; this.stop();
            notify("error", "Audio was interrupted. Tap the sound button again.");
          }
        };
      }
      // Start resume synchronously within the gesture before awaiting the fetch.
      const resumed = this.context.resume();
      // Mark rejection handled immediately while a slow download is pending.
      void resumed.catch(() => {});
      let buffer = this.cache.get(url);
      if (!buffer) {
        const response = await fetch(url, { signal: current.abort.signal, cache: "force-cache" });
        if (!response.ok) throw new Error("The guitar recording could not be loaded. Try again.");
        buffer = await this.context.decodeAudioData(await response.arrayBuffer());
        if (this.current !== current) return;
        if (this.cache.size >= 8) this.cache.delete(this.cache.keys().next().value);
        this.cache.set(url, buffer);
      }
      await resumed;
      if (this.current !== current) return;
      if (this.context.state !== "running") throw new Error("Audio was interrupted. Tap the sound button again.");
      const source = this.context.createBufferSource(), gain = this.context.createGain();
      current.source = source; current.gain = gain;
      source.buffer = buffer; source.playbackRate.value = rate;
      gain.gain.value = .7;
      source.connect(gain).connect(this.context.destination);
      source.onended = () => {
        if (this.current !== current) return;
        this.current = null;
        source.disconnect(); gain.disconnect(); onState("ended");
      };
      source.start();
      onState("playing");
    } catch (error) {
      if (this.current !== current) return;
      this.stop();
      onState("error", error.message || "Unable to play this guitar recording.");
    }
  }
  async dispose() {
    this.stop(); this.cache.clear();
    const context = this.context; this.context = null;
    if (context) context.onstatechange = null;
    if (context && context.state !== "closed") await context.close().catch(() => {});
  }
}
export const guitarAudio = new RecordedGuitarPlayer();
