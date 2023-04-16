import requests
import os
import pygame
import io
from elevenlabslib import *


def eleven_lab_voice(text):
    eleven_labs_api_key = os.getenv("ELEVEN_API_KEY")
    user = ElevenLabsUser(eleven_labs_api_key)
    # This is a list because multiple voices can have the same name
    voice = user.get_voice_by_ID("ulNWt4xXCDXJ4P7TBu7t")

    voice.generate_and_play_audio(text, playInBackground=False)
