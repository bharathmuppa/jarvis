"""
Base Voice Provider Interface
Defines the common interface for all voice synthesis providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import time

@dataclass
class VoiceResponse:
    """Standardized response format for all voice providers"""
    success: bool
    provider_name: str
    voice_used: Optional[str] = None
    text_length: int = 0
    cost: float = 0.0
    synthesis_time: float = 0.0
    playback_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseVoiceProvider(ABC):
    """
    Abstract base class for all voice synthesis providers
    Defines the interface that all providers must implement
    """
    
    def __init__(self, name: str, quality_tier: str = "unknown", cost_tier: str = "unknown"):
        self.name = name
        self.quality_tier = quality_tier  # "premium", "high", "medium", "low", "basic"
        self.cost_tier = cost_tier  # "free", "low", "medium", "high", "premium"
        self.is_available = False
        self.voices = []
        self.default_voice = None
        self.supports_ssml = False
        self.supports_streaming = False
        self.max_text_length = 5000
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.total_cost = 0.0
        self.total_characters = 0
        self.avg_synthesis_time = 0.0
        
        # Initialize the provider
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> bool:
        """
        Initialize the provider (check dependencies, API keys, etc.)
        Returns True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def _synthesize_speech(self, text: str, voice: Optional[str] = None, **kwargs) -> VoiceResponse:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice: Voice to use (provider-specific)
            **kwargs: Provider-specific parameters
        
        Returns:
            VoiceResponse object with synthesis results
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[str]:
        """Get list of available voices for this provider"""
        pass
    
    @abstractmethod
    def estimate_cost(self, text: str, voice: Optional[str] = None) -> float:
        """Estimate cost for synthesizing the given text"""
        pass
    
    def speak(self, text: str, voice: Optional[str] = None, **kwargs) -> VoiceResponse:
        """
        Public method to synthesize and play speech with error handling and tracking
        
        Args:
            text: Text to speak
            voice: Voice to use (defaults to provider's default)
            **kwargs: Additional parameters
        
        Returns:
            VoiceResponse object
        """
        start_time = time.time()
        
        # Validate text
        if not text or not text.strip():
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                error_message="Empty text provided"
            )
        
        # Check text length
        if len(text) > self.max_text_length:
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                error_message=f"Text too long ({len(text)} > {self.max_text_length} characters)"
            )
        
        # Use default voice if none specified
        if voice is None:
            voice = self.default_voice
        
        # Validate voice
        available_voices = self.get_available_voices()
        if available_voices and voice not in available_voices:
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                error_message=f"Voice '{voice}' not available for provider '{self.name}'"
            )
        
        try:
            # Track request
            self.total_requests += 1
            
            # Get synthesis response
            response = self._synthesize_speech(text, voice, **kwargs)
            response.text_length = len(text)
            
            # Update statistics
            if response.success:
                self.successful_requests += 1
                self.total_cost += response.cost
                self.total_characters += len(text)
                
                # Update average synthesis time
                if response.synthesis_time > 0:
                    self.avg_synthesis_time = (
                        (self.avg_synthesis_time * (self.successful_requests - 1) + response.synthesis_time)
                        / self.successful_requests
                    )
            
            return response
            
        except Exception as e:
            return VoiceResponse(
                success=False,
                provider_name=self.name,
                text_length=len(text),
                synthesis_time=time.time() - start_time,
                error_message=f"Provider error: {str(e)}"
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status and statistics"""
        success_rate = (
            self.successful_requests / max(1, self.total_requests)
            if self.total_requests > 0 else 0.0
        )
        
        cost_per_char = (
            self.total_cost / max(1, self.total_characters)
            if self.total_characters > 0 else 0.0
        )
        
        return {
            "name": self.name,
            "quality_tier": self.quality_tier,
            "cost_tier": self.cost_tier,
            "is_available": self.is_available,
            "available_voices": self.get_available_voices(),
            "default_voice": self.default_voice,
            "supports_ssml": self.supports_ssml,
            "supports_streaming": self.supports_streaming,
            "max_text_length": self.max_text_length,
            "statistics": {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "success_rate": success_rate,
                "total_cost": self.total_cost,
                "total_characters": self.total_characters,
                "cost_per_character": cost_per_char,
                "avg_synthesis_time": self.avg_synthesis_time
            }
        }
    
    def reset_statistics(self):
        """Reset provider statistics"""
        self.total_requests = 0
        self.successful_requests = 0
        self.total_cost = 0.0
        self.total_characters = 0
        self.avg_synthesis_time = 0.0
    
    def test_voice(self, test_text: str = "Hello, this is a test.", voice: Optional[str] = None) -> Tuple[bool, str]:
        """
        Test voice synthesis
        Returns (success, message)
        """
        try:
            response = self.speak(test_text, voice)
            
            if response.success:
                return True, f"Voice test successful for {self.name}"
            else:
                return False, f"Voice test failed: {response.error_message}"
                
        except Exception as e:
            return False, f"Voice test failed: {str(e)}"
    
    def get_voice_info(self, voice: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        # Default implementation - providers can override
        return {
            "name": voice,
            "provider": self.name,
            "available": voice in self.get_available_voices()
        }
    
    def __str__(self):
        return f"{self.name} ({self.quality_tier}, {self.cost_tier}) - {'Available' if self.is_available else 'Unavailable'}"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', available={self.is_available})>"