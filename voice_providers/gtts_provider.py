"""
Google Text-to-Speech (gTTS) Provider for Advanced JARVIS
Free basic voice synthesis using Google's TTS service
"""

import os
import sys
import time
import tempfile
from typing import List, Dict, Any, Optional

from .base_voice_provider import BaseVoiceProvider, VoiceResponse

class GTTSProvider(BaseVoiceProvider):
    """Google Text-to-Speech provider implementation"""
    
    def __init__(self):
        super().__init__(name="gtts", quality_tier="medium", cost_tier="free")
        
        # gTTS specific configuration
        self.gtts = None
        self.pygame = None
        
        # Available languages/voices
        self.voice_configs = {
            # English variants
            "English (US)": {"lang": "en", "tld": "com"},
            "English (UK)": {"lang": "en", "tld": "co.uk"},
            "English (AU)": {"lang": "en", "tld": "com.au"},
            "English (CA)": {"lang": "en", "tld": "ca"},
            "English (IN)": {"lang": "en", "tld": "co.in"},
            
            # Other languages
            "Spanish": {"lang": "es", "tld": "com"},
            "French": {"lang": "fr", "tld": "com"},
            "German": {"lang": "de", "tld": "com"},
            "Italian": {"lang": "it", "tld": "com"},
            "Portuguese": {"lang": "pt", "tld": "com"},
            "Dutch": {"lang": "nl", "tld": "com"},
            "Russian": {"lang": "ru", "tld": "com"},
            "Japanese": {"lang": "ja", "tld": "com"},
            "Korean": {"lang": "ko", "tld": "com"},
            "Chinese": {"lang": "zh", "tld": "com"},
        }
        
        self.default_voice = "English (US)"
        self.supports_ssml = False
        self.supports_streaming = False
        self.max_text_length = 5000  # gTTS has character limits
    
    def _initialize(self) -> bool:
        """Initialize gTTS provider"""
        try:
            # Try to import gTTS
            from gtts import gTTS
            self.gtts = gTTS
            
            # Try to import pygame for audio playback
            import pygame
            self.pygame = pygame
            
            # Initialize pygame mixer
            pygame.mixer.init()
            
            # Test connection
            success, message = self.test_voice("Test", voice="English (US)")
            if success:
                self.is_available = True
                self.voices = list(self.voice_configs.keys())
                print(f"✅ {self.name}: Initialized successfully")
                return True
            else:
                print(f"❌ {self.name}: {message}")
                return False
                
        except ImportError as e:
            missing_package = "gtts" if "gtts" in str(e) else "pygame"
            print(f"❌ {self.name}: {missing_package} not installed. Run: pip install {missing_package}")
            return False
        except Exception as e:
            print(f"❌ {self.name}: Initialization failed - {str(e)}")
            return False
    
    def _synthesize_speech(self, text: str, voice: Optional[str] = None, **kwargs) -> VoiceResponse:
        """Synthesize speech using gTTS"""
        start_time = time.time()
        
        try:
            # Get parameters
            slow = kwargs.get("slow", False)
            
            # Get voice configuration
            if voice is None:
                voice = self.default_voice
            
            voice_config = self.voice_configs.get(voice, self.voice_configs[self.default_voice])
            lang = voice_config["lang"]
            tld = voice_config["tld"]
            
            # Create gTTS object
            tts = self.gtts(text=text, lang=lang, tld=tld, slow=slow)
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                audio_file = tmp_file.name
            
            try:
                # Save audio to file
                tts.save(audio_file)
                synthesis_time = time.time() - start_time
                
                # Play audio using pygame
                playback_start = time.time()
                self.pygame.mixer.music.load(audio_file)
                self.pygame.mixer.music.play()
                
                # Wait for playback to complete
                while self.pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                playback_time = time.time() - playback_start
                
                return VoiceResponse(
                    success=True,
                    provider_name=self.name,
                    voice_used=voice,
                    text_length=len(text),
                    cost=0.0,  # gTTS is free
                    synthesis_time=synthesis_time,
                    playback_time=playback_time,
                    metadata={
                        "language": lang,
                        "tld": tld,
                        "slow": slow,
                        "audio_file": audio_file
                    }
                )
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(audio_file)
                except:
                    pass
            
        except Exception as e:
            error_msg = str(e)
            
            # Parse specific gTTS errors
            if "HTTP Error 403" in error_msg:
                error_msg = "gTTS access forbidden - possible rate limit"
            elif "HTTP Error 503" in error_msg:
                error_msg = "gTTS service unavailable"
            elif "No text to send to TTS API" in error_msg:
                error_msg = "Empty text provided"
            elif "Language not supported" in error_msg:
                error_msg = f"Language not supported for voice '{voice}'"
            
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                voice_used=voice,
                text_length=len(text),
                synthesis_time=time.time() - start_time,
                error_message=error_msg
            )
    
    def get_available_voices(self) -> List[str]:
        """Get list of available gTTS voices"""
        if self.is_available:
            return self.voices
        return []
    
    def estimate_cost(self, text: str, voice: Optional[str] = None) -> float:
        """Estimate cost for gTTS synthesis (always free)"""
        return 0.0
    
    def get_voice_info(self, voice: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        base_info = super().get_voice_info(voice)
        
        if voice in self.voice_configs:
            voice_config = self.voice_configs[voice]
            
            base_info.update({
                "language": voice_config["lang"],
                "tld": voice_config["tld"],
                "quality": "medium",
                "cost": "free",
                "provider_specific": True
            })
        
        return base_info
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        try:
            from gtts.lang import tts_langs
            return tts_langs()
        except Exception:
            # Return basic language set if API call fails
            return {
                "en": "English",
                "es": "Spanish", 
                "fr": "French",
                "de": "German",
                "it": "Italian",
                "pt": "Portuguese",
                "nl": "Dutch",
                "ru": "Russian",
                "ja": "Japanese",
                "ko": "Korean",
                "zh": "Chinese"
            }
    
    def add_custom_voice(self, name: str, lang: str, tld: str = "com"):
        """Add a custom voice configuration"""
        self.voice_configs[name] = {"lang": lang, "tld": tld}
        if self.is_available:
            self.voices = list(self.voice_configs.keys())
    
    def set_slow_speech(self, enabled: bool = True):
        """Enable or disable slow speech mode"""
        # This would be used in the synthesis call
        return {"slow": enabled}