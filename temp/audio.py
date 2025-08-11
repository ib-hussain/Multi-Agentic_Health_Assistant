'''
Provide the transcript of any auditory input given by the user.
Args:
    input_path (str): Path to the audio file to be transcribed from the directory which is using this header
'''
import wave
import json
import os
import pandas as pd
import streamlit as st
import subprocess
from imageio_ffmpeg import get_ffmpeg_exe

NULLstring =str(st.secrets["NULL_STRING"])
debug = st.secrets["DEBUGGING_MODE"]
# for getting the transcript
def transcribe_audio(input_path: str = "temp/"):
    # if not convert_to_wav(input_path, input_path):
    #     return NULLstring
    from temp.vosk import Model, KaldiRecognizer
    model_path = f"{input_path}vosk_model" #vosk-model-small-en-us-0.15

    wf = wave.open(input_path + "temp_audio1.wav", "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError(f"{input_path + "temp_audio1.wav"} must be mono, 16-bit, 16kHz")
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
def convert_to_wav(input_path: str = "temp/", output_path: str = "temp/"):
    """
    Convert audio file to WAV format with normalization
    
    Args:
        input_path (str): Path to input audio file
        output_path (str): Path for output WAV file
    """
    # Check if input file exists
    input_path += "temp_audio.mp3"
    output_path += "temp_audio1.wav"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    # Add audio normalization for better preprocessing
    ffmpeg_path = get_ffmpeg_exe()
    cmd = [
        ffmpeg_path,
        "-y",                    # force overwrite without asking
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
        return True
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg conversion failed: {e}")
        return False
    except Exception as e:
        raise RuntimeError(f"Conversion error: {e}")
        return False
