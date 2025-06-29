"""
Base LLM Provider Interface
Defines the common interface for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time

@dataclass
class LLMResponse:
    """Standardized response format for all LLM providers"""
    success: bool
    content: str
    model_used: str
    provider_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    response_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers
    Defines the interface that all providers must implement
    """
    
    def __init__(self, name: str, cost_tier: str = "unknown"):
        self.name = name
        self.cost_tier = cost_tier  # "free", "low", "medium", "high", "premium"
        self.is_available = False
        self.models = []
        self.default_model = None
        self.max_tokens = 4096
        self.supports_streaming = False
        self.supports_functions = False
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.total_cost = 0.0
        self.avg_response_time = 0.0
        
        # Initialize the provider
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> bool:
        """
        Initialize the provider (check API keys, test connection, etc.)
        Returns True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def _get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> LLMResponse:
        """
        Get response from the LLM provider
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use
            **kwargs: Provider-specific parameters
        
        Returns:
            LLMResponse object with standardized response data
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for a request"""
        pass
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         model: Optional[str] = None, **kwargs) -> LLMResponse:
        """
        Public method to generate response with error handling and tracking
        
        Args:
            messages: List of message dictionaries
            model: Model to use (defaults to provider's default)
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse object
        """
        start_time = time.time()
        
        # Use default model if none specified
        if model is None:
            model = self.default_model
        
        # Validate model
        if model not in self.get_available_models():
            return LLMResponse(
                success=False,
                content="",
                model_used=model or "unknown",
                provider_name=self.name,
                error_message=f"Model '{model}' not available for provider '{self.name}'"
            )
        
        try:
            # Track request
            self.total_requests += 1
            
            # Get response from provider
            response = self._get_response(messages, model, **kwargs)
            response.response_time = time.time() - start_time
            
            # Update statistics
            if response.success:
                self.successful_requests += 1
                self.total_cost += response.cost
                
                # Update average response time
                self.avg_response_time = (
                    (self.avg_response_time * (self.successful_requests - 1) + response.response_time)
                    / self.successful_requests
                )
            
            return response
            
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                model_used=model or "unknown",
                provider_name=self.name,
                response_time=time.time() - start_time,
                error_message=f"Provider error: {str(e)}"
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status and statistics"""
        success_rate = (
            self.successful_requests / max(1, self.total_requests)
            if self.total_requests > 0 else 0.0
        )
        
        return {
            "name": self.name,
            "cost_tier": self.cost_tier,
            "is_available": self.is_available,
            "available_models": self.get_available_models(),
            "default_model": self.default_model,
            "supports_streaming": self.supports_streaming,
            "supports_functions": self.supports_functions,
            "statistics": {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "success_rate": success_rate,
                "total_cost": self.total_cost,
                "avg_response_time": self.avg_response_time
            }
        }
    
    def reset_statistics(self):
        """Reset provider statistics"""
        self.total_requests = 0
        self.successful_requests = 0
        self.total_cost = 0.0
        self.avg_response_time = 0.0
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to the provider
        Returns (success, message)
        """
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            response = self.generate_response(test_messages)
            
            if response.success:
                return True, f"Connection to {self.name} successful"
            else:
                return False, f"Connection failed: {response.error_message}"
                
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def __str__(self):
        return f"{self.name} ({self.cost_tier}) - {'Available' if self.is_available else 'Unavailable'}"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', available={self.is_available})>"