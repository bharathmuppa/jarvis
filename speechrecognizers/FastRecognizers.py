import speech_recognition as sr
import pyaudio
import wave
import threading
import time
import os
from concurrent.futures import ThreadPoolExecutor

# Alternative fast speech recognition implementation
class FastSpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Optimized settings for low latency
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5  # Very short pause
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.5
        
        # Pre-calibrate microphone
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        """Quick microphone calibration"""
        print("Quick microphone calibration...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Calibration complete!")
    
    def listen_with_vad(self, timeout=10, silent_mode=False):
        """Voice Activity Detection based listening"""
        try:
            with self.microphone as source:
                if not silent_mode:
                    print("🎤 Listening... (speak now)")
                # Quick listen with shorter timeouts
                audio = self.recognizer.listen(
                    source, 
                    timeout=2,  # Max wait time for speech to start
                    phrase_time_limit=8  # Max recording time
                )
                if not silent_mode:
                    print("🔄 Processing...")
                
            # Process in background thread for faster response
            future = self.executor.submit(self.recognizer.recognize_google, audio)
            text = future.result(timeout=5)  # 5 second processing timeout
            
            return text if text.strip() else "silent"
            
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "unclear"
        except sr.RequestError as e:
            return f"network_error: {e}"
        except Exception as e:
            return f"system_error: {e}"
    
    def continuous_listen(self):
        """Continuous background listening"""
        def callback(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio)
                if text.strip() and len(text) > 2:  # Filter out noise
                    print(f"👂 Heard: {text}")
                    return text
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Recognition error: {e}")
        
        print("🔄 Starting continuous listening...")
        stop_listening = self.recognizer.listen_in_background(
            self.microphone, 
            callback,
            phrase_time_limit=5
        )
        
        return stop_listening


# Global instance
fast_recognizer = FastSpeechRecognizer()

def recognize_speech_ultrafast():
    """Ultra-fast speech recognition with minimal latency"""
    return fast_recognizer.listen_with_vad()

def start_continuous_listening():
    """Start continuous background listening"""
    return fast_recognizer.continuous_listen()


# Alternative using OpenAI Whisper for better accuracy (if available)
def recognize_with_whisper():
    """Use OpenAI Whisper for local speech recognition (requires whisper package)"""
    try:
        import whisper
        import tempfile
        import sounddevice as sd
        import soundfile as sf
        
        # Load tiny model for speed
        model = whisper.load_model("tiny")
        
        print("🎤 Recording with Whisper...")
        # Record for 5 seconds
        duration = 5
        sample_rate = 16000
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          dtype='float32')
        sd.wait()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, recording, sample_rate)
            temp_path = f.name
        
        # Transcribe
        result = model.transcribe(temp_path)
        os.unlink(temp_path)  # Clean up
        
        return result["text"].strip()
        
    except ImportError:
        return "Whisper not available - install with: pip install openai-whisper sounddevice soundfile"
    except Exception as e:
        return f"Whisper error: {e}"