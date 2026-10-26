"""Word-timed transcripts from open-source Whisper, run on the member's machine.

Engines:
- whisper      openai-whisper CLI (MIT): pip install -U openai-whisper
- whisper-cpp  whisper.cpp CLI (MIT): brew install whisper-cpp, plus a ggml model file
- import       any Whisper-style JSON you already have (openai-whisper, faster-whisper, whisper.cpp -ojf)
"""
import json
import re
import shutil
import tempfile
from pathlib import Path

from .core import ShelfError, latest, next_version, read, run, write

# Whisper tends to tidy speech. A prompt that itself contains fillers nudges it to keep them.
FILLER_PROMPT = 'Umm, so, uh, let me think, like, hmm. Erm, okay, uh, here is what I mean.'


def norm(text):
    return re.sub(r"[^a-z0-9']+", ' ', text.lower()).strip()


def from_openai(data):
    words = []
    for segment in data.get('segments', []):
        for item in segment.get('words', []) or []:
            text = str(item.get('word', '')).strip()
            if text:
                words.append({'text': text, 'start': float(item['start']), 'end': float(item['end']),
                              'p': round(float(item.get('probability', 1.0)), 3)})
    return words


def from_whisper_cpp(data):
    words = []
    for segment in data.get('transcription', []):
        for token in segment.get('tokens', []) or []:
            text = str(token.get('text', ''))
            if not text.strip() or text.strip().startswith('[_') or text.strip().startswith('<|'):
                continue
            start = token['offsets']['from'] / 1000.0
            end = token['offsets']['to'] / 1000.0
            if words and not text.startswith(' ') and not norm(text) == '' and words[-1]['end'] >= start - 0.02:
                words[-1]['text'] += text
                words[-1]['end'] = max(words[-1]['end'], end)
            elif words and norm(text) == '':
                words[-1]['text'] += text.strip()
            else:
                words.append({'text': text.strip(), 'start': start, 'end': end,
                              'p': round(float(token.get('p', 1.0)), 3)})
    return words


def normalise(data):
    if isinstance(data, dict) and 'transcription' in data:
        words = from_whisper_cpp(data)
    elif isinstance(data, dict) and 'segments' in data:
        words = from_openai(data)
    elif isinstance(data, dict) and 'words' in data:
        words = [{'text': str(w['text']).strip(), 'start': float(w['start']), 'end': float(w['end']),
                  'p': float(w.get('p', 1.0))} for w in data['words']]
    else:
        raise ShelfError('Unrecognised transcript JSON. Use openai-whisper JSON with word timestamps, '
                         'faster-whisper JSON, or whisper.cpp -ojf output.')
    if not words:
        raise ShelfError('The transcript has no word timings. Run Whisper with word timestamps switched on.')
    words.sort(key=lambda w: (w['start'], w['end']))
    out = []
    for i, w in enumerate(words):
        end = max(w['end'], w['start'] + 0.02)
        out.append({'id': i, 'text': w['text'], 'word': norm(w['text']), 'start': round(w['start'], 3),
                    'end': round(end, 3), 'p': w['p']})
    return out


def extract_wav(source, folder):
    wav = Path(folder) / 'audio_16k.wav'
    run(['ffmpeg', '-v', 'error', '-y', '-i', source, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav])
    return wav


def run_whisper(source, folder, model, language):
    if not shutil.which('whisper'):
        raise ShelfError('openai-whisper is not installed. Run: python3 -m pip install --user -U openai-whisper '
                         '(or use --engine whisper-cpp, or --engine import with your own JSON).')
    with tempfile.TemporaryDirectory(prefix='shelf-video-') as tmp:
        wav = extract_wav(source, tmp)
        args = ['whisper', wav, '--model', model, '--word_timestamps', 'True', '--output_format', 'json',
                '--output_dir', tmp, '--initial_prompt', FILLER_PROMPT, '--condition_on_previous_text', 'False',
                '--fp16', 'False', '--verbose', 'False']
        if language and not model.endswith('.en'):
            args += ['--language', language]
        run(args)
        raw = Path(tmp) / 'audio_16k.json'
        if not raw.exists():
            raise ShelfError('Whisper finished without writing JSON.')
        return json.loads(raw.read_text()), {'engine': 'openai-whisper', 'model': model}


def run_whisper_cpp(source, folder, model_path, language):
    binary = shutil.which('whisper-cli') or shutil.which('whisper-cpp')
    if not binary:
        raise ShelfError('whisper.cpp is not installed. Run: brew install whisper-cpp')
    if not model_path or not Path(model_path).expanduser().exists():
        raise ShelfError('whisper.cpp needs a model file. Download one, for example ggml-small.en.bin from '
                         'https://huggingface.co/ggerganov/whisper.cpp, then pass --model-path <file>.')
    with tempfile.TemporaryDirectory(prefix='shelf-video-') as tmp:
        wav = extract_wav(source, tmp)
        base = Path(tmp) / 'out'
        run([binary, '-m', Path(model_path).expanduser(), '-f', wav, '-ojf', '-of', base, '-l', language or 'en',
             '--prompt', FILLER_PROMPT, '-np'])
        raw = Path(str(base) + '.json')
        return json.loads(raw.read_text()), {'engine': 'whisper.cpp', 'model': Path(model_path).name}


def transcribe(root, project, engine='whisper', model='small.en', language='en', model_path=None,
               import_json=None, force=False):
    folder = Path(root) / 'transcript'
    folder.mkdir(exist_ok=True)
    existing = latest(folder, 'words', '.json')
    if existing and not force and not import_json:
        data = read(existing)
        if data.get('source_sha256') == project['source_sha256']:
            return existing, data, True
    if import_json:
        raw = json.loads(Path(import_json).expanduser().read_text())
        how = {'engine': 'import', 'model': Path(import_json).name}
    elif engine == 'whisper':
        raw, how = run_whisper(project['source'], folder, model, language)
    elif engine == 'whisper-cpp':
        raw, how = run_whisper_cpp(project['source'], folder, model_path, language)
    else:
        raise ShelfError('Unknown engine: ' + engine)
    words = normalise(raw)
    target = next_version(folder, 'words', '.json')
    raw_copy = target.with_name(target.name.replace('words_', 'raw_'))
    write(raw_copy, raw)
    data = dict(how, source_sha256=project['source_sha256'], raw=raw_copy.name, words=words)
    write(target, data)
    text = ' '.join(w['text'] for w in words)
    target.with_suffix('.txt').write_text(text + '\n')
    return target, data, False

