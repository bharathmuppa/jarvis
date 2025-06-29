import os
import threading
from typing import Optional, Dict, Any
import tempfile
import time

from core.budget_manager import budget_manager

class VoiceManager:
    """
    Multi-tier voice system with intelligent fallbacks
    ElevenLabs → Free TTS → pyttsx3 → Text-only
    """
    
    def __init__(self):
        self.lock = threading.Lock()
        self.current_tier = 0  # Start with best quality
        
        # Voice tiers (best to worst)
        self.voice_tiers = [
            {
                "name": "elevenlabs",
                "available": self._check_elevenlabs_available(),
                "cost_per_char": 0.18/1000,
                "quality": "premium",
                "setup_func": self._setup_elevenlabs
            },
            {
                "name": "edge_tts",
                "available": self._check_edge_tts_available(),
                "cost_per_char": 0.0,
                "quality": "good",
                "setup_func": self._setup_edge_tts
            },
            {
                "name": "gtts",
                "available": self._check_gtts_available(),
                "cost_per_char": 0.0,
                "quality": "decent",
                "setup_func": self._setup_gtts
            },
            {
                "name": "pyttsx3",
                "available": self._check_pyttsx3_available(),
                "cost_per_char": 0.0,
                "quality": "basic",
                "setup_func": self._setup_pyttsx3
            },
            {
                "name": "text_only",
                "available": True,
                "cost_per_char": 0.0,
                "quality": "fallback",
                "setup_func": None
            }
        ]
        
        # Voice settings for different tiers
        self.voice_configs = {
            "elevenlabs": {
                "voice_id": "s2wvuS7SwITYg8dqsJdn",  # Current voice
                "model": "eleven_monolingual_v1"
            },
            "edge_tts": {
                "voice": "en-US-AriaNeural",  # Professional female voice
                "rate": "+20%",
                "pitch": "+0Hz"
            },
            "gtts": {
                "lang": "en",
                "tld": "com",
                "slow": False
            },
            "pyttsx3": {
                "rate": 150,
                "voice_id": "com.apple.speech.synthesis.voice.Alex"
            }
        }
        
        # Initialize available engines
        self.engines = {}
        self._initialize_engines()
    
    def _check_elevenlabs_available(self) -> bool:
        """Check if ElevenLabs is available"""
        try:
            from elevenlabs import ElevenLabs
            return bool(os.getenv("ELEVEN_API_KEY"))
        except ImportError:
            return False
    
    def _check_edge_tts_available(self) -> bool:
        """Check if edge-tts is available"""
        try:
            import edge_tts
            return True
        except ImportError:
            return False
    
    def _check_gtts_available(self) -> bool:
        """Check if gTTS is available"""
        try:
            from gtts import gTTS
            return True
        except ImportError:
            return False
    
    def _check_pyttsx3_available(self) -> bool:
        """Check if pyttsx3 is available"""
        try:
            import pyttsx3
            return True
        except ImportError:
            return False
    
    def _setup_elevenlabs(self):
        """Setup ElevenLabs engine"""
        try:
            from elevenlabs import ElevenLabs, play
            self.engines["elevenlabs"] = {
                "client": ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY")),
                "play_func": play
            }
            return True
        except Exception as e:
            print(f"❌ ElevenLabs setup failed: {e}")
            return False
    
    def _setup_edge_tts(self):
        """Setup Edge TTS engine"""
        try:
            import edge_tts
            import asyncio
            import pygame
            
            self.engines["edge_tts"] = {
                "edge_tts": edge_tts,
                "asyncio": asyncio,
                "pygame": pygame
            }
            
            # Initialize pygame mixer
            pygame.mixer.init()
            return True
        except Exception as e:
            print(f"❌ Edge TTS setup failed: {e}")
            return False
    
    def _setup_gtts(self):
        """Setup Google TTS engine"""
        try:
            from gtts import gTTS
            import pygame
            
            self.engines["gtts"] = {
                "gTTS": gTTS,
                "pygame": pygame
            }
            
            # Initialize pygame mixer
            pygame.mixer.init()
            return True
        except Exception as e:
            print(f"❌ gTTS setup failed: {e}")
            return False
    
    def _setup_pyttsx3(self):
        """Setup pyttsx3 engine"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            config = self.voice_configs["pyttsx3"]
            
            engine.setProperty('rate', config["rate"])
            try:
                engine.setProperty('voice', config["voice_id"])
            except:
                pass  # Use default voice if specified one not available
            
            self.engines["pyttsx3"] = {"engine": engine}
            return True
        except Exception as e:
            print(f"❌ pyttsx3 setup failed: {e}")
            return False
    
    def _initialize_engines(self):
        """Initialize all available engines"""
        for tier in self.voice_tiers:
            if tier["available"] and tier["setup_func"]:
                tier["available"] = tier["setup_func"]()
    
    def _speak_elevenlabs(self, text: str) -> bool:
        """Speak using ElevenLabs"""
        try:
            # Check budget
            char_count = len(text)
            estimated_cost = budget_manager.calculate_cost("elevenlabs", "standard", characters=char_count)
            
            can_afford, reason = budget_manager.can_afford("elevenlabs", estimated_cost)
            if not can_afford:
                print(f"💰 ElevenLabs budget exceeded: {reason}")
                return False
            
            client = self.engines["elevenlabs"]["client"]
            play_func = self.engines["elevenlabs"]["play_func"]
            config = self.voice_configs["elevenlabs"]
            
            audio = client.text_to_speech.convert(
                text=text,
                voice_id=config["voice_id"],
                model_id=config["model"]
            )
            
            play_func(audio)
            
            # Record usage
            budget_manager.record_usage("elevenlabs", estimated_cost, "standard")
            return True
            
        except Exception as e:
            print(f"❌ ElevenLabs speak failed: {e}")
            return False
    
    def _speak_edge_tts(self, text: str) -> bool:
        """Speak using Edge TTS"""
        try:
            edge_tts = self.engines["edge_tts"]["edge_tts"]
            asyncio = self.engines["edge_tts"]["asyncio"]
            pygame = self.engines["edge_tts"]["pygame"]
            config = self.voice_configs["edge_tts"]
            
            async def generate_speech():
                communicate = edge_tts.Communicate(text, config["voice"])
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            tmp_file.write(chunk["data"])
                    return tmp_file.name
            
            # Generate audio
            if hasattr(asyncio, 'run'):
                audio_file = asyncio.run(generate_speech())
            else:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio_file = loop.run_until_complete(generate_speech())
                loop.close()
            
            # Play audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Cleanup
            os.unlink(audio_file)
            return True
            
        except Exception as e:
            print(f"❌ Edge TTS speak failed: {e}")
            return False
    
    def _speak_gtts(self, text: str) -> bool:
        """Speak using Google TTS"""
        try:
            gTTS = self.engines["gtts"]["gTTS"]
            pygame = self.engines["gtts"]["pygame"]
            config = self.voice_configs["gtts"]
            
            tts = gTTS(text=text, lang=config["lang"], tld=config["tld"], slow=config["slow"])
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                os.unlink(tmp_file.name)
            
            return True
            
        except Exception as e:
            print(f"❌ gTTS speak failed: {e}")
            return False
    
    def _speak_pyttsx3(self, text: str) -> bool:
        """Speak using pyttsx3"""
        try:
            engine = self.engines["pyttsx3"]["engine"]
            engine.say(text)
            engine.runAndWait()
            return True
            
        except Exception as e:
            print(f"❌ pyttsx3 speak failed: {e}")
            return False
    
    def speak(self, text: str, force_tier: Optional[str] = None) -> Dict[str, Any]:
        """
        Speak text using best available voice tier
        Returns: {
            "success": bool,
            "tier_used": str,
            "cost": float,
            "fallback_count": int
        }
        """
        with self.lock:
            if not text.strip():
                return {"success": False, "error": "Empty text"}
            
            # If force_tier specified, try only that tier
            if force_tier:
                tier_names = [t["name"] for t in self.voice_tiers]
                if force_tier in tier_names:
                    tier_index = tier_names.index(force_tier)
                    tiers_to_try = [self.voice_tiers[tier_index]]
                else:
                    return {"success": False, "error": f"Unknown tier: {force_tier}"}
            else:
                # Try all tiers starting from current preference
                tiers_to_try = self.voice_tiers[self.current_tier:]
            
            fallback_count = 0
            
            for tier in tiers_to_try:
                if not tier["available"]:
                    fallback_count += 1
                    continue
                
                tier_name = tier["name"]
                print(f"🔊 Trying {tier_name} voice...")
                
                success = False
                cost = 0.0
                
                try:
                    if tier_name == "elevenlabs":
                        success = self._speak_elevenlabs(text)
                        if success:
                            cost = len(text) * tier["cost_per_char"]
                    elif tier_name == "edge_tts":
                        success = self._speak_edge_tts(text)
                    elif tier_name == "gtts":
                        success = self._speak_gtts(text)
                    elif tier_name == "pyttsx3":
                        success = self._speak_pyttsx3(text)
                    elif tier_name == "text_only":
                        print(f"📝 Text: {text}")
                        success = True
                    
                    if success:
                        return {
                            "success": True,
                            "tier_used": tier_name,
                            "cost": cost,
                            "fallback_count": fallback_count,
                            "quality": tier["quality"]
                        }
                    
                except Exception as e:
                    print(f"❌ {tier_name} failed: {e}")
                
                fallback_count += 1
            
            # All tiers failed
            print(f"📝 FALLBACK - Text: {text}")
            return {
                "success": False,
                "tier_used": "text_only",
                "cost": 0.0,
                "fallback_count": fallback_count,
                "error": "All voice tiers failed"
            }
    
    def set_preferred_tier(self, tier_name: str):
        """Set preferred voice tier"""
        tier_names = [t["name"] for t in self.voice_tiers]
        if tier_name in tier_names:
            self.current_tier = tier_names.index(tier_name)
            print(f"🔊 Voice preference set to {tier_name}")
        else:
            print(f"❌ Unknown voice tier: {tier_name}")
    
    def get_status(self) -> Dict:
        """Get voice system status"""
        return {
            "available_tiers": [
                {
                    "name": tier["name"],
                    "available": tier["available"],
                    "quality": tier["quality"],
                    "cost_per_char": tier["cost_per_char"]
                }
                for tier in self.voice_tiers
            ],
            "current_preference": self.voice_tiers[self.current_tier]["name"],
            "budget_status": budget_manager.get_budget_status().get("elevenlabs", {})
        }
    
    def install_missing_packages(self):
        """Helper to install missing TTS packages"""
        missing = []
        
        if not self._check_edge_tts_available():
            missing.append("edge-tts")
        if not self._check_gtts_available():
            missing.append("gtts")
        if not self._check_pyttsx3_available():
            missing.append("pyttsx3")
        
        if missing:
            print("📦 Missing TTS packages:")
            for package in missing:
                print(f"   pip install {package}")
        else:
            print("✅ All TTS packages available")


# Global voice manager instance
voice_manager = VoiceManager()