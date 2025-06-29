"""
PyTTSx3 Provider for Advanced JARVIS
Offline voice synthesis using system TTS engines
"""

import os
import sys
import time
import platform
from typing import List, Dict, Any, Optional

from .base_voice_provider import BaseVoiceProvider, VoiceResponse

class PyTTSx3Provider(BaseVoiceProvider):
    """PyTTSx3 offline voice synthesis provider"""
    
    def __init__(self):
        super().__init__(name="pyttsx3", quality_tier="basic", cost_tier="free")
        
        # PyTTSx3 specific configuration
        self.engine = None
        self.system = platform.system().lower()
        
        # Voice settings
        self.default_rate = 150
        self.default_volume = 0.9
        
        # Available voices (will be populated from system)
        self.system_voices = []
        
        self.supports_ssml = False
        self.supports_streaming = False
        self.max_text_length = 10000
    
    def _initialize(self) -> bool:
        """Initialize PyTTSx3 provider"""
        try:
            # Try to import pyttsx3
            import pyttsx3
            
            # Initialize engine with platform-specific driver
            if self.system == "darwin":  # macOS
                try:
                    self.engine = pyttsx3.init('nsss')
                except:
                    self.engine = pyttsx3.init()
            elif self.system == "windows":
                try:
                    self.engine = pyttsx3.init('sapi5')
                except:
                    self.engine = pyttsx3.init()
            else:  # Linux
                try:
                    self.engine = pyttsx3.init('espeak')
                except:
                    self.engine = pyttsx3.init()
            
            if self.engine is None:
                print(f"❌ {self.name}: Could not initialize TTS engine")
                return False
            
            # Set default properties
            self.engine.setProperty('rate', self.default_rate)
            self.engine.setProperty('volume', self.default_volume)
            
            # Get available voices
            self._get_system_voices()
            
            # Test the engine
            success, message = self.test_voice("Test")
            if success:
                self.is_available = True
                print(f"✅ {self.name}: Initialized successfully")
                return True
            else:
                print(f"❌ {self.name}: {message}")
                return False
                
        except ImportError:
            print(f"❌ {self.name}: pyttsx3 not installed. Run: pip install pyttsx3")
            return False
        except Exception as e:
            print(f"❌ {self.name}: Initialization failed - {str(e)}")
            return False
    
    def _get_system_voices(self):
        """Get available system voices"""
        try:
            voices = self.engine.getProperty('voices')
            self.system_voices = []
            
            if voices:
                for voice in voices:
                    voice_info = {
                        "id": voice.id,
                        "name": voice.name if hasattr(voice, 'name') else str(voice.id),
                        "languages": getattr(voice, 'languages', []),
                        "gender": getattr(voice, 'gender', 'unknown'),
                        "age": getattr(voice, 'age', 'unknown')
                    }
                    self.system_voices.append(voice_info)
                
                # Set default voice
                if self.system_voices:
                    self.default_voice = self.system_voices[0]["id"]
                    
                    # Try to find a good default voice
                    for voice in self.system_voices:
                        name = voice["name"].lower()
                        if any(keyword in name for keyword in ["alex", "samantha", "microsoft", "david"]):
                            self.default_voice = voice["id"]
                            break
            
            self.voices = [voice["name"] for voice in self.system_voices]
            
        except Exception as e:
            print(f"⚠️ Could not get system voices: {e}")
            self.system_voices = []
            self.voices = ["Default"]
            self.default_voice = None
    
    def _get_voice_id(self, voice_name: str) -> Optional[str]:
        """Get voice ID from voice name"""
        if not voice_name:
            return self.default_voice
        
        # Direct ID match
        for voice in self.system_voices:
            if voice["id"] == voice_name:
                return voice["id"]
        
        # Name match
        for voice in self.system_voices:
            if voice["name"] == voice_name:
                return voice["id"]
        
        # Partial name match
        voice_name_lower = voice_name.lower()
        for voice in self.system_voices:
            if voice_name_lower in voice["name"].lower():
                return voice["id"]
        
        return self.default_voice
    
    def _synthesize_speech(self, text: str, voice: Optional[str] = None, **kwargs) -> VoiceResponse:
        """Synthesize speech using PyTTSx3"""
        start_time = time.time()
        
        try:
            # Get parameters
            rate = kwargs.get("rate", self.default_rate)
            volume = kwargs.get("volume", self.default_volume)
            
            # Set voice
            voice_id = self._get_voice_id(voice)
            if voice_id:
                try:
                    self.engine.setProperty('voice', voice_id)
                except:
                    pass  # Use current voice if setting fails
            
            # Set properties
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # Synthesize and play
            playback_start = time.time()
            self.engine.say(text)
            self.engine.runAndWait()
            
            total_time = time.time() - start_time
            synthesis_time = playback_start - start_time
            playback_time = total_time - synthesis_time
            
            return VoiceResponse(
                success=True,
                provider_name=self.name,
                voice_used=voice or "Default",
                text_length=len(text),
                cost=0.0,  # PyTTSx3 is free
                synthesis_time=synthesis_time,
                playback_time=playback_time,
                metadata={
                    "voice_id": voice_id,
                    "rate": rate,
                    "volume": volume,
                    "system": self.system
                }
            )
            
        except Exception as e:
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                voice_used=voice or "Default",
                text_length=len(text),
                synthesis_time=time.time() - start_time,
                error_message=f"PyTTSx3 error: {str(e)}"
            )
    
    def get_available_voices(self) -> List[str]:
        """Get list of available PyTTSx3 voices"""
        if self.is_available:
            return self.voices
        return []
    
    def estimate_cost(self, text: str, voice: Optional[str] = None) -> float:
        """Estimate cost for PyTTSx3 synthesis (always free)"""
        return 0.0
    
    def get_voice_info(self, voice: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        base_info = super().get_voice_info(voice)
        
        # Find voice in system voices
        for system_voice in self.system_voices:
            if system_voice["name"] == voice or system_voice["id"] == voice:
                base_info.update({
                    "voice_id": system_voice["id"],
                    "languages": system_voice.get("languages", []),
                    "gender": system_voice.get("gender", "unknown"),
                    "age": system_voice.get("age", "unknown"),
                    "quality": "basic",
                    "cost": "free",
                    "system": self.system,
                    "provider_specific": True
                })
                break
        
        return base_info
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        try:
            self.engine.setProperty('rate', rate)
            self.default_rate = rate
        except Exception as e:
            print(f"Could not set rate: {e}")
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to valid range
            self.engine.setProperty('volume', volume)
            self.default_volume = volume
        except Exception as e:
            print(f"Could not set volume: {e}")
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current engine settings"""
        try:
            return {
                "rate": self.engine.getProperty('rate'),
                "volume": self.engine.getProperty('volume'),
                "voice": self.engine.getProperty('voice')
            }
        except Exception:
            return {
                "rate": self.default_rate,
                "volume": self.default_volume,
                "voice": self.default_voice
            }
    
    def refresh_voices(self):
        """Refresh the list of system voices"""
        self._get_system_voices()
    
    def stop_speech(self):
        """Stop current speech"""
        try:
            self.engine.stop()
        except Exception as e:
            print(f"Could not stop speech: {e}")