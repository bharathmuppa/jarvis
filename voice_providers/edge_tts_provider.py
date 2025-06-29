"""
Microsoft Edge TTS Provider for
 Advanced JARVIS
High-quality free voice synthesis using Microsoft Edge TTS
"""

import os
import sys
import time
import tempfile
import asyncio
from typing import List, Dict, Any, Optional

from .base_voice_provider import BaseVoiceProvider, VoiceResponse

class EdgeTTSProvider(BaseVoiceProvider):
    """Microsoft Edge TTS provider implementation"""
    
    def __init__(self):
        super().__init__(name="edge_tts", quality_tier="high", cost_tier="free")
        
        # Edge TTS specific configuration
        self.edge_tts = None
        self.pygame = None
        
        # Available voices
        self.voice_configs = {
            # English voices
            "Aria": "en-US-AriaNeural",
            "Jenny": "en-US-JennyNeural", 
            "Guy": "en-US-GuyNeural",
            "Ana": "en-US-AnaNeural",
            "Christopher": "en-US-ChristopherNeural",
            "Eric": "en-US-EricNeural",
            "Michelle": "en-US-MichelleNeural",
            "Roger": "en-US-RogerNeural",
            "Steffan": "en-US-SteffanNeural",
            
            # British English
            "Libby": "en-GB-LibbyNeural",
            "Maisie": "en-GB-MaisieNeural", 
            "Ryan": "en-GB-RyanNeural",
            "Sonia": "en-GB-SoniaNeural",
            "Thomas": "en-GB-ThomasNeural",
            
            # Australian English
            "Natasha": "en-AU-NatashaNeural",
            "William": "en-AU-WilliamNeural",
            
            # Canadian English
            "Clara": "en-CA-ClaraNeural",
            "Liam": "en-CA-LiamNeural"
        }
        
        self.default_voice = "Aria"
        self.supports_ssml = True
        self.supports_streaming = False
        self.max_text_length = 10000
    
    def _initialize(self) -> bool:
        """Initialize Edge TTS provider"""
        try:
            # Try to import edge-tts
            import edge_tts
            self.edge_tts = edge_tts
            
            # Try to import pygame for audio playback
            import pygame
            self.pygame = pygame
            
            # Initialize pygame mixer
            pygame.mixer.init()
            
            # Test connection
            success, message = self.test_voice("Test", voice="Aria")
            if success:
                self.is_available = True
                self.voices = list(self.voice_configs.keys())
                print(f"✅ {self.name}: Initialized successfully")
                return True
            else:
                print(f"❌ {self.name}: {message}")
                return False
                
        except ImportError as e:
            missing_package = "edge-tts" if "edge_tts" in str(e) else "pygame"
            print(f"❌ {self.name}: {missing_package} not installed. Run: pip install {missing_package}")
            return False
        except Exception as e:
            print(f"❌ {self.name}: Initialization failed - {str(e)}")
            return False
    
    def _synthesize_speech(self, text: str, voice: Optional[str] = None, **kwargs) -> VoiceResponse:
        """Synthesize speech using Edge TTS"""
        start_time = time.time()
        
        try:
            # Get parameters
            rate = kwargs.get("rate", "+0%")
            pitch = kwargs.get("pitch", "+0Hz")
            
            # Get voice name
            if voice is None:
                voice = self.default_voice
            
            voice_name = self.voice_configs.get(voice, voice)
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                audio_file = tmp_file.name
            
            try:
                # Generate speech asynchronously
                async def generate_speech():
                    communicate = self.edge_tts.Communicate(text, voice_name, rate=rate, pitch=pitch)
                    await communicate.save(audio_file)
                
                # Run the async function
                if hasattr(asyncio, 'run'):
                    asyncio.run(generate_speech())
                else:
                    # Fallback for older Python versions
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(generate_speech())
                    loop.close()
                
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
                    cost=0.0,  # Edge TTS is free
                    synthesis_time=synthesis_time,
                    playback_time=playback_time,
                    metadata={
                        "voice_name": voice_name,
                        "rate": rate,
                        "pitch": pitch,
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
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                voice_used=voice,
                text_length=len(text),
                synthesis_time=time.time() - start_time,
                error_message=f"Edge TTS error: {str(e)}"
            )
    
    def get_available_voices(self) -> List[str]:
        """Get list of available Edge TTS voices"""
        if self.is_available:
            return self.voices
        return []
    
    def estimate_cost(self, text: str, voice: Optional[str] = None) -> float:
        """Estimate cost for Edge TTS synthesis (always free)"""
        return 0.0
    
    def get_voice_info(self, voice: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        base_info = super().get_voice_info(voice)
        
        if voice in self.voice_configs:
            voice_name = self.voice_configs[voice]
            
            # Parse voice information from name
            parts = voice_name.split('-')
            language = f"{parts[0]}-{parts[1]}" if len(parts) >= 2 else "en-US"
            
            base_info.update({
                "voice_name": voice_name,
                "language": language,
                "quality": "high",
                "cost": "free",
                "provider_specific": True
            })
        
        return base_info
    
    async def get_all_voices(self) -> List[Dict[str, Any]]:
        """Get all available voices from Edge TTS (async)"""
        try:
            voices = await self.edge_tts.list_voices()
            return [
                {
                    "name": voice["ShortName"],
                    "display_name": voice["FriendlyName"],
                    "language": voice["Locale"],
                    "gender": voice["Gender"]
                }
                for voice in voices
            ]
        except Exception as e:
            print(f"Could not fetch Edge TTS voices: {e}")
            return []
    
    def refresh_voices(self) -> bool:
        """Refresh the list of available voices"""
        try:
            # This would require async handling
            # For now, we use the predefined voice list
            print("Voice refresh not implemented for Edge TTS")
            return True
        except Exception as e:
            print(f"Voice refresh failed: {e}")
            return False
    
    def set_voice_parameters(self, voice: str, rate: str = "+0%", pitch: str = "+0Hz") -> Dict[str, str]:
        """Set voice parameters for synthesis"""
        return {
            "rate": rate,
            "pitch": pitch
        }