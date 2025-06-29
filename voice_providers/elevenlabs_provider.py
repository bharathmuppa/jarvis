"""
ElevenLabs Voice Provider for Advanced JARVIS
Premium voice synthesis with natural-sounding voices
"""

import os
import sys
import time
from typing import List, Dict, Any, Optional

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import config

from .base_voice_provider import BaseVoiceProvider, VoiceResponse

class ElevenLabsProvider(BaseVoiceProvider):
    """ElevenLabs premium voice synthesis provider"""
    
    def __init__(self):
        super().__init__(name="elevenlabs", quality_tier="premium", cost_tier="premium")
        
        # ElevenLabs-specific configuration
        self.api_key = None
        self.client = None
        
        # Available voices (will be populated from API)
        self.voice_configs = {
            # Pre-defined popular voices
            "Rachel": "21m00Tcm4TlvDq8ikWAM",
            "Domi": "AZnzlk1XvdvUeBnXmlld", 
            "Bella": "EXAVITQu4vr4xnSDxMaL",
            "Antoni": "ErXwobaYiN019PkySvjV",
            "Elli": "MF3mGyEYCl7XYWbV9V6O",
            "Josh": "TxGEqnHWrfWFTfGW9XjX",
            "Arnold": "VR6AewLTigWG4xSOukaG",
            "Adam": "pNInz6obpgDQGcFmaJgB",
            "Sam": "yoZ06aMxZJJ28mfd3POQ"
        }
        
        # Model configurations
        self.models = {
            "eleven_monolingual_v1": {
                "cost_per_char": 0.30 / 1000,  # $0.30 per 1K characters
                "quality": "high",
                "latency": "medium"
            },
            "eleven_multilingual_v1": {
                "cost_per_char": 0.30 / 1000,
                "quality": "high", 
                "latency": "medium"
            },
            "eleven_multilingual_v2": {
                "cost_per_char": 0.30 / 1000,
                "quality": "premium",
                "latency": "low"
            }
        }
        
        self.default_voice = "Rachel"
        self.default_model = "eleven_monolingual_v1"
        self.supports_ssml = True
        self.supports_streaming = True
        self.max_text_length = 5000
    
    def _initialize(self) -> bool:
        """Initialize ElevenLabs provider"""
        try:
            # Get API key from config
            self.api_key = config.get_api_key("elevenlabs")
            
            if not self.api_key:
                print(f"❌ {self.name}: No API key found")
                return False
            
            # Try to import ElevenLabs
            from elevenlabs import ElevenLabs, play
            
            # Set up client
            self.client = ElevenLabs(api_key=self.api_key)
            self.play_function = play
            
            # Test connection and get available voices
            success, message = self.test_voice("Test", voice="Rachel")
            if success:
                self.is_available = True
                self.voices = list(self.voice_configs.keys())
                print(f"✅ {self.name}: Initialized successfully")
                
                # Try to get additional voices from API
                try:
                    self._fetch_available_voices()
                except Exception:
                    pass  # Use predefined voices if API call fails
                
                return True
            else:
                print(f"❌ {self.name}: {message}")
                return False
                
        except ImportError:
            print(f"❌ {self.name}: ElevenLabs package not installed. Run: pip install elevenlabs")
            return False
        except Exception as e:
            print(f"❌ {self.name}: Initialization failed - {str(e)}")
            return False
    
    def _fetch_available_voices(self):
        """Fetch available voices from ElevenLabs API"""
        try:
            voices_response = self.client.voices.get_all()
            
            # Update voice configs with API data
            for voice in voices_response.voices:
                self.voice_configs[voice.name] = voice.voice_id
            
            self.voices = list(self.voice_configs.keys())
            
        except Exception as e:
            print(f"⚠️ Could not fetch ElevenLabs voices: {e}")
    
    def _synthesize_speech(self, text: str, voice: Optional[str] = None, **kwargs) -> VoiceResponse:
        """Synthesize speech using ElevenLabs API"""
        start_time = time.time()
        
        try:
            # Get parameters
            model = kwargs.get("model", self.default_model)
            voice_settings = kwargs.get("voice_settings", {})
            
            # Get voice ID
            if voice is None:
                voice = self.default_voice
            
            voice_id = self.voice_configs.get(voice, voice)  # Allow direct voice ID usage
            
            # Estimate cost
            estimated_cost = self.estimate_cost(text, voice)
            
            # Generate audio
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=model,
                voice_settings=voice_settings or None
            )
            
            synthesis_time = time.time() - start_time
            
            # Play audio
            playback_start = time.time()
            self.play_function(audio_generator)
            playback_time = time.time() - playback_start
            
            return VoiceResponse(
                success=True,
                provider_name=self.name,
                voice_used=voice,
                text_length=len(text),
                cost=estimated_cost,
                synthesis_time=synthesis_time,
                playback_time=playback_time,
                metadata={
                    "model": model,
                    "voice_id": voice_id,
                    "voice_settings": voice_settings
                }
            )
            
        except Exception as e:
            error_msg = str(e)
            
            # Parse specific ElevenLabs errors
            if "quota" in error_msg.lower():
                error_msg = "ElevenLabs quota exceeded"
            elif "unauthorized" in error_msg.lower():
                error_msg = "Invalid ElevenLabs API key"
            elif "voice_not_found" in error_msg.lower():
                error_msg = f"Voice '{voice}' not found"
            elif "rate_limit" in error_msg.lower():
                error_msg = "ElevenLabs rate limit exceeded"
            
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                voice_used=voice,
                text_length=len(text),
                synthesis_time=time.time() - start_time,
                error_message=error_msg
            )
    
    def get_available_voices(self) -> List[str]:
        """Get list of available ElevenLabs voices"""
        if self.is_available:
            return self.voices
        return []
    
    def estimate_cost(self, text: str, voice: Optional[str] = None) -> float:
        """Estimate cost for ElevenLabs synthesis"""
        char_count = len(text)
        cost_per_char = self.models[self.default_model]["cost_per_char"]
        return round(char_count * cost_per_char, 6)
    
    def get_voice_info(self, voice: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        base_info = super().get_voice_info(voice)
        
        if voice in self.voice_configs:
            base_info.update({
                "voice_id": self.voice_configs[voice],
                "quality": "premium",
                "language": "en",  # Most voices are English
                "provider_specific": True
            })
        
        return base_info
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model in self.models:
            return self.models[model].copy()
        return {}
    
    def set_voice_settings(self, voice: str, settings: Dict[str, Any]):
        """Set custom voice settings for a voice"""
        # This would be used in the synthesis call
        # Settings like: {"stability": 0.5, "similarity_boost": 0.8}
        pass
    
    def clone_voice(self, voice_name: str, audio_files: List[str]) -> bool:
        """Clone a voice from audio files (if supported by plan)"""
        try:
            # This is a premium feature - implementation would depend on 
            # ElevenLabs API capabilities and user's subscription
            print(f"Voice cloning not implemented for {voice_name}")
            return False
        except Exception as e:
            print(f"Voice cloning failed: {e}")
            return False