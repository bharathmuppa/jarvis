import os
from elevenlabs import ElevenLabs, play


def eleven_lab_voice(text):
    eleven_labs_api_key = os.getenv("ELEVEN_API_KEY")
    if not eleven_labs_api_key:
        print("Warning: ELEVEN_API_KEY not found. Please set your ElevenLabs API key.")
        print(f"Text would have been spoken: {text}")
        return
    
    try:
        client = ElevenLabs(api_key=eleven_labs_api_key)
        audio = client.text_to_speech.convert(
            text=text,
            # voice_id="s2wvuS7SwITYg8dqsJdn"
            voice_id="s2wvuS7SwITYg8dqsJdn"
        )
        
        # Play the audio
        play(audio)
            
    except Exception as e:
        print(f"Error with ElevenLabs TTS: {e}")
        print(f"Text would have been spoken: {text}")
