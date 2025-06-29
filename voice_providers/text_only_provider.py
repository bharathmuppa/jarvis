"""
Text-Only Provider for Advanced JARVIS
Fallback provider that prints text instead of synthesizing speech
"""

import time
from typing import List, Dict, Any, Optional

from .base_voice_provider import BaseVoiceProvider, VoiceResponse

class TextOnlyProvider(BaseVoiceProvider):
    """Text-only fallback provider when no voice synthesis is available"""
    
    def __init__(self):
        super().__init__(name="text_only", quality_tier="fallback", cost_tier="free")
        
        # Text-only configuration
        self.output_styles = {
            "simple": "📝 {}",
            "speech": "🗣️  JARVIS: {}",
            "quote": "💬 \"{}\"", 
            "announcement": "📢 {}",
            "whisper": "🤫 {}",
            "emphasis": "‼️  {}",
            "info": "ℹ️  {}",
            "robot": "🤖 {}"
        }
        
        self.default_voice = "speech"
        self.supports_ssml = False
        self.supports_streaming = False
        self.max_text_length = 50000  # Very high limit for text
    
    def _initialize(self) -> bool:
        """Initialize text-only provider (always succeeds)"""
        self.is_available = True
        self.voices = list(self.output_styles.keys())
        print(f"✅ {self.name}: Text-only output ready")
        return True
    
    def _synthesize_speech(self, text: str, voice: Optional[str] = None, **kwargs) -> VoiceResponse:
        """'Synthesize' speech by printing formatted text"""
        start_time = time.time()
        
        try:
            # Get style
            if voice is None:
                voice = self.default_voice
            
            style_template = self.output_styles.get(voice, self.output_styles["simple"])
            
            # Format text
            formatted_text = style_template.format(text)
            
            # Get additional formatting options
            uppercase = kwargs.get("uppercase", False)
            repeat_count = kwargs.get("repeat", 1)
            delay = kwargs.get("delay", 0.0)
            
            if uppercase:
                formatted_text = formatted_text.upper()
            
            # "Play" the text
            playback_start = time.time()
            
            for i in range(repeat_count):
                print(formatted_text)
                if delay > 0 and i < repeat_count - 1:
                    time.sleep(delay)
            
            synthesis_time = playback_start - start_time
            playback_time = time.time() - playback_start
            
            return VoiceResponse(
                success=True,
                provider_name=self.name,
                voice_used=voice,
                text_length=len(text),
                cost=0.0,  # Text output is free
                synthesis_time=synthesis_time,
                playback_time=playback_time,
                metadata={
                    "style": voice,
                    "template": style_template,
                    "uppercase": uppercase,
                    "repeat_count": repeat_count,
                    "delay": delay,
                    "formatted_text": formatted_text
                }
            )
            
        except Exception as e:
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                voice_used=voice or "simple",
                text_length=len(text),
                synthesis_time=time.time() - start_time,
                error_message=f"Text output error: {str(e)}"
            )
    
    def get_available_voices(self) -> List[str]:
        """Get list of available text styles"""
        return list(self.output_styles.keys())
    
    def estimate_cost(self, text: str, voice: Optional[str] = None) -> float:
        """Estimate cost for text output (always free)"""
        return 0.0
    
    def get_voice_info(self, voice: str) -> Dict[str, Any]:
        """Get information about a specific text style"""
        base_info = super().get_voice_info(voice)
        
        if voice in self.output_styles:
            base_info.update({
                "style_template": self.output_styles[voice],
                "quality": "fallback",
                "cost": "free",
                "output_method": "text",
                "provider_specific": True
            })
        
        return base_info
    
    def add_style(self, name: str, template: str):
        """Add a custom text output style"""
        self.output_styles[name] = template
        self.voices = list(self.output_styles.keys())
    
    def remove_style(self, name: str) -> bool:
        """Remove a text output style"""
        if name in self.output_styles and name != "simple":  # Keep simple as fallback
            del self.output_styles[name]
            self.voices = list(self.output_styles.keys())
            return True
        return False
    
    def preview_style(self, style: str, sample_text: str = "This is a sample text.") -> str:
        """Preview how text would look with a specific style"""
        template = self.output_styles.get(style, self.output_styles["simple"])
        return template.format(sample_text)
    
    def get_style_samples(self) -> Dict[str, str]:
        """Get samples of all available styles"""
        sample_text = "Hello, this is JARVIS speaking."
        return {
            style: template.format(sample_text)
            for style, template in self.output_styles.items()
        }
    
    def set_default_style(self, style: str):
        """Set default text output style"""
        if style in self.output_styles:
            self.default_voice = style
    
    def silent_mode(self, text: str) -> VoiceResponse:
        """Process text without any output (completely silent)"""
        start_time = time.time()
        
        return VoiceResponse(
            success=True,
            provider_name=self.name,
            voice_used="silent",
            text_length=len(text),
            cost=0.0,
            synthesis_time=0.0,
            playback_time=time.time() - start_time,
            metadata={
                "style": "silent",
                "output_suppressed": True
            }
        )