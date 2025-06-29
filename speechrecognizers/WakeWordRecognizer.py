import speech_recognition as sr
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add parent directory to path to import jarvis_personality
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jarvis_personality import jarvis_personality

class JarvisWakeWordDetector:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.wake_words = ["jarvis", "hey jarvis", "ok jarvis", "jarvis wake up"]
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Optimized settings for wake word detection
        self.recognizer.energy_threshold = 2000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.3
        
        # Calibrate microphone
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        """Quick microphone calibration"""
        print("🎙️  Calibrating microphone for wake word detection...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("✅ Ready to detect 'Jarvis' wake word!")
    
    def listen_for_wake_word(self):
        """Continuously listen for wake word"""
        print("👂 Listening for 'Jarvis'... (say 'Jarvis' to activate)")
        
        while True:
            try:
                with self.microphone as source:
                    # Listen with shorter timeout for wake word
                    audio = self.recognizer.listen(
                        source, 
                        timeout=1,  # Short timeout to avoid blocking
                        phrase_time_limit=3  # Max 3 seconds for wake word
                    )
                
                # Process in background thread
                future = self.executor.submit(self._process_wake_word, audio)
                try:
                    result = future.result(timeout=2)
                    if result:
                        return True  # Wake word detected
                except:
                    continue  # Continue listening
                    
            except sr.WaitTimeoutError:
                # Normal timeout, continue listening silently
                continue
            except Exception as e:
                print(f"⚠️  Wake word detection error: {e}")
                time.sleep(0.5)
                continue
    
    def _process_wake_word(self, audio):
        """Process audio for wake word detection"""
        try:
            text = self.recognizer.recognize_google(audio, language='en-US')
            text_lower = text.lower().strip()
            
            # Check for wake words
            for wake_word in self.wake_words:
                if wake_word in text_lower:
                    print(f"🎯 Wake word detected: '{text}'")
                    return True
            
            return False
            
        except sr.UnknownValueError:
            return False
        except sr.RequestError:
            return False
    
    def listen_for_command(self, speak_callback=None):
        """Listen for actual command after wake word"""
        # Get JARVIS-style wake response with time
        wake_response = jarvis_personality.get_wake_response()
        print(f"🤖 JARVIS: {wake_response}")
        
        # Speak the response if callback provided
        if speak_callback:
            speak_callback(wake_response)
        
        # Sometimes ask a contextual question
        if time.time() % 3 < 1:  # Randomly ask questions
            question = jarvis_personality.get_contextual_questions()
            print(f"🤖 JARVIS: {question}")
            if speak_callback:
                speak_callback(question)
        
        print("🎤 Listening for your command...")
        
        try:
            with self.microphone as source:
                # Give user time to speak command
                audio = self.recognizer.listen(
                    source, 
                    timeout=5,  # Wait up to 5 seconds for command to start
                    phrase_time_limit=15  # Allow longer commands
                )
            
            # Show thinking message
            thinking_msg = jarvis_personality.get_thinking_response()
            print(f"🤖 JARVIS: {thinking_msg}")
            
            # Process command
            text = self.recognizer.recognize_google(audio)
            return text.strip()
            
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "unclear"
        except sr.RequestError as e:
            return f"error: {e}"


# Global wake word detector instance
wake_detector = JarvisWakeWordDetector()

def listen_with_wake_word(speak_callback=None):
    """Main function that waits for wake word then listens for command"""
    # Wait for wake word
    wake_detector.listen_for_wake_word()
    
    # Get command after wake word with JARVIS personality
    command = wake_detector.listen_for_command(speak_callback)
    return command

def continuous_wake_word_mode():
    """Continuous mode that keeps listening for wake word"""
    print("\n" + "="*60)
    print("🤖 JARVIS WAKE WORD DETECTION ACTIVE")
    print("💡 Say 'Jarvis' followed by your command")
    print("💡 Example: 'Jarvis, what's the weather?'")
    print("💡 Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    error_count = 0
    max_errors = 3
    
    while True:
        try:
            # Wait for wake word
            if wake_detector.listen_for_wake_word():
                # Get command
                command = wake_detector.listen_for_command()
                
                if command == "timeout":
                    print("⏰ No command received after wake word. Listening again...")
                    continue
                elif command == "unclear":
                    print("❓ I didn't catch that. Please try again...")
                    error_count += 1
                    if error_count >= max_errors:
                        print(f"🔄 Too many unclear commands. Restarting wake word detection...")
                        error_count = 0
                    continue
                elif command.startswith("error:"):
                    print(f"🚫 {command}")
                    continue
                else:
                    error_count = 0  # Reset error count on successful command
                    return command
                    
        except KeyboardInterrupt:
            print("\n👋 Wake word detection stopped.")
            break
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")
            time.sleep(1)
            continue