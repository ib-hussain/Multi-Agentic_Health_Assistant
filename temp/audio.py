import wave
import json
import pandas as pd
import streamlit as st
import subprocess
from imageio_ffmpeg import get_ffmpeg_exe

debug = st.secrets["DEBUGGING_MODE"]
# for getting the transcript
def transcribe_audio(audio_file_path: str = "temp_audio1.wav"):
    from vosk import Model, KaldiRecognizer
    model_path = "vosk_model" #vosk-model-small-en-us-0.15

    wf = wave.open(audio_file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError(f"{audio_file_path} must be mono, 16-bit, 16kHz")
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
    results.append(json.loads(rec.FinalResult()))
    transcript = " ".join(r.get("text", "") for r in results)
    return transcript
# Convert the video(.mp3) files into audio(.wav) only
# Involves Pre-Processing on the audio files before conversion, to normalise all of them
ffmpeg_path = get_ffmpeg_exe()
def convert_to_wav(input_path: str = "temp_audio.mp3", output_path: str = "temp_audio1.wav"):
    """
    Convert audio file to WAV format with normalization.
    Args:
        input_path (str): Path to input audio file
        output_path (str): Path for output WAV file
    """
    from vosk import Model, KaldiRecognizer
    # Add audio normalization for better preprocessing
    cmd = [
        ffmpeg_path,
        "-i", input_path,
        "-ac", "1",           # mono channel
        "-ar", "16000",       # 16 kHz sample rate
        "-acodec", "pcm_s16le",  # 16-bit PCM encoding (standard for WAV)
        "-loglevel", "error",    # suppress verbose output
        output_path
    ]
    try:
        subprocess.run(cmd, check=True)
        if debug: print(f"Successfully converted {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg conversion failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Conversion error: {e}")
