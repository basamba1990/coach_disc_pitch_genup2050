import openai
import streamlit as st

openai.api_key = st.secrets["openai_api_key"]

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
    return transcript["text"]
