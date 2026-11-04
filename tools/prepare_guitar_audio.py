"""Download a small, pinned CC0 guitar subset and build local web recordings.

Uses Python's standard library and an existing FFmpeg executable for offline asset
preparation only. It is not imported by Flask and adds no runtime dependencies.
Sources, revisions, licenses and SHA-256 digests are retained with shipped assets.
"""
import argparse
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import numpy as np  # Offline preparation only; already available in the project venv.

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / 'instance/audio-work'
DEST = ROOT / 'assets/audio/guitars'
REPOS = {'meta': 'facebookincubator/Meta-open-sound', 'electric': 'freepats/electric-guitar-FSBS-clean'}
REVISIONS = {'meta': '251c0be57d5d1b3242b91f53e0cde62ab1cb42d9',
             'electric': '192cf0d9bf2c4ba6ead8e3524ba3f78818e4fe91'}
STRINGS = [('LowE', 'E2', 40), ('A', 'A2', 45), ('D', 'D3', 50), ('G', 'G3', 55), ('B', 'B3', 59), ('HighE', 'E4', 64)]


def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'AUDIA-licensed-audio-preparation'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def raw(repo, revision, path):
    return f'https://raw.githubusercontent.com/{repo}/{revision}/{urllib.parse.quote(path)}'


def prepare(ffmpeg, inspect_only=False):
    WORK.mkdir(parents=True, exist_ok=True)
    revisions = REVISIONS
    sources = []
    for instrument, library, layer in [('acoustic', 'meta-steel-guitar', 'Vel02'), ('classical', 'meta-nylon-guitar', 'Vel02Pick')]:
        base = f'systems/instruments/{library}'
        manifest = json.loads(get(raw(REPOS['meta'], revisions['meta'], base+'/manifest.json')))
        available = {item['file'] for item in manifest['samples']}
        print(instrument, 'license:', manifest.get('license'), 'samples:', len(available))
        for string, note, midi in STRINGS:
            family = 'Steel' if instrument == 'acoustic' else 'Nylon'
            name = f'INSGuitar{family}_String{string}_{layer}_{note}_01.wav'
            assert name in available, name
            sources.append(dict(instrument=instrument, note=note, midi=midi,
                                path=base+'/ogg/'+name.replace('.wav', '.ogg'), repo='meta', source_midi=midi))
    sfz = get(raw(REPOS['electric'], revisions['electric'], 'EGuitarFSBS-clean bridge 20260807.sfz')).decode()
    for note, midi, name, source_midi in [('E2',40,'E2_s1_01.flac',40), ('A2',45,'A2_s2_01.flac',45),
                                        ('D3',50,'E3_s3_01.flac',52), ('G3',55,'G3_s4_01.flac',55),
                                        ('B3',59,'B3_s5_01.flac',59), ('E4',64,'E4_s6_01.flac',64)]:
        path = 'samples/bridge/'+name
        assert path in sfz, path
        sources.append(dict(instrument='electric', note=note, midi=midi, path=path, repo='electric', source_midi=source_midi))
    print('Revisions:', json.dumps(revisions))
    print('Selected recordings:', len(sources))
    if inspect_only:
        return
    assert ffmpeg and Path(ffmpeg).is_file(), 'Pass an existing FFmpeg executable with --ffmpeg.'
    evidence = DEST / 'licenses'
    evidence.mkdir(parents=True, exist_ok=True)
    for instrument, library in [('acoustic','meta-steel-guitar'), ('classical','meta-nylon-guitar')]:
        base = f'systems/instruments/{library}'
        for source_name, output_name in [('LICENSE','LICENSE.txt'),('README.md','SOURCE.md')]:
            content = get(raw(REPOS['meta'], revisions['meta'], base+'/'+source_name))
            (evidence/f'{instrument}-{output_name}').write_bytes(content)
    for source_name in ('LICENSE.txt', 'README.txt'):
        (evidence/f'electric-{source_name}').write_bytes(get(raw(REPOS['electric'], revisions['electric'], source_name)))
    assert all('CC0' in path.read_text(encoding='utf-8') for path in evidence.glob('*LICENSE.txt'))
    records = []
    for source in sources:
        revision = revisions[source['repo']]
        url = raw(REPOS[source['repo']], revision, source['path'])
        original = WORK / source['instrument'] / Path(source['path']).name
        original.parent.mkdir(parents=True, exist_ok=True)
        if not original.exists(): original.write_bytes(get(url))
        decoded = original.with_suffix('.wav')
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(original),'-ac','1','-ar','48000','-c:a','pcm_s16le',str(decoded)], check=True)
        target = DEST / source['instrument'] / 'reference' / (source['note']+'.m4a')
        target.parent.mkdir(parents=True, exist_ok=True)
        # D3 uses the real D-string E3 recording two semitones lower, matching
        # the source SFZ region. No oscillator or synthesized instrument is used.
        with wave.open(str(decoded), 'rb') as audio:
            samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2').astype(float) / 32768
        nominal = 440 * 2 ** ((source['source_midi']-69)/12)
        # Calibrate the recording's sustained fundamental, without removing its
        # natural attack, harmonics, vibrato or decay. Never applied to mic input.
        estimates = []
        for start in (0.25, 0.45, 0.65, 0.85, 1.05):
            segment = samples[int(start*48000):int((start+0.35)*48000)]
            if len(segment) < 1000: continue
            spectrum = abs(np.fft.rfft(segment*np.hanning(len(segment)), n=262144))
            lo, hi = int(nominal*.96*262144/48000), int(nominal*1.04*262144/48000)
            peak = lo + int(np.argmax(spectrum[lo:hi]))
            a, b, c = np.log(np.maximum(spectrum[peak-1:peak+2], 1e-20))
            estimates.append((peak + .5*(a-c)/(a-2*b+c))*48000/262144)
        measured = float(np.median(estimates))
        rate = 48000 * (440 * 2 ** ((source['midi']-69)/12)) / measured
        filters = f'asetrate={rate:.6f},aresample=44100,atrim=duration=6,afade=t=out:st=5.85:d=0.15'
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(decoded),'-af',filters,
                        '-ac','1','-c:a','aac','-b:a','96k','-movflags','+faststart',str(target)], check=True)
        # Small PCM copies remain ignored under instance/ for repeatable DSP tests.
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(target),'-ac','1','-ar','48000','-c:a','pcm_s16le',str(original.parent/(source['note']+'-reference.wav'))], check=True)
        records.append(dict(**source, source_url=url, revision=revision, license='CC0-1.0',
                            source_measured_hz=measured, resample_ratio=rate/48000,
                            source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                            file=target.relative_to(ROOT/'assets').as_posix(),
                            sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
        print('Prepared',target.relative_to(ROOT),target.stat().st_size)
    previews = []
    ground_truth = []
    for instrument in ('acoustic', 'electric', 'classical'):
        mix = np.zeros(48000*7)
        for index, (_, note, _) in enumerate(STRINGS):
            with wave.open(str(WORK/instrument/(note+'-reference.wav')), 'rb') as audio:
                pcm = np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2').astype(float)/32768
            nominal = next(record['midi'] for record in records if record['instrument']==instrument and record['note']==note)
            hz = 440*2**((nominal-69)/12)
            for seconds in (.18,.25,.35,.5,.7,1,1.4,1.8,2.2):
                segment = pcm[round(seconds*48000):round(seconds*48000)+8192]
                if len(segment)<8192: continue
                spectrum = abs(np.fft.rfft(segment*np.hanning(8192), n=262144))
                lo, hi = int(hz*.96*262144/48000), int(hz*1.04*262144/48000)
                peak = lo+int(np.argmax(spectrum[lo:hi]))
                a,b,c = np.log(np.maximum(spectrum[peak-1:peak+2],1e-20))
                measured=(peak+.5*(a-c)/(a-2*b+c))*48000/262144
                ground_truth.append(dict(instrument=instrument,note=note,seconds=seconds,hz=measured))
            pcm=pcm[:48000*3].copy()
            pcm[-min(4800,len(pcm)):] *= np.linspace(1,0,min(4800,len(pcm)))
            start = int(index*.65*48000)
            mix[start:start+len(pcm)] += pcm*.5
        mix *= min(1, .89/max(abs(mix)))
        preview_wav = WORK/instrument/'preview.wav'
        with wave.open(str(preview_wav),'wb') as audio:
            audio.setparams((1,2,48000,0,'NONE','not compressed'))
            audio.writeframes((mix*32767).astype('<i2').tobytes())
        target = DEST/instrument/'previews'/'open-strings.m4a'
        target.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(preview_wav),'-c:a','aac','-b:a','96k','-movflags','+faststart',str(target)],check=True)
        previews.append(dict(instrument=instrument,file=target.relative_to(ROOT/'assets').as_posix(),
                             description='Six real recorded open strings sequenced; representative category audio, not a model recording.',
                             sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    (DEST/'manifest.json').write_text(json.dumps({'revisions':revisions,'recordings':records,'previews':previews},indent=2)+'\n',encoding='utf-8')
    (WORK/'reference-ground-truth.json').write_text(json.dumps(ground_truth,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg')
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args()
    prepare(args.ffmpeg, args.inspect)
