"""
OpenAI Provider for Advanced JARVIS
Supports GPT-3.5-turbo, GPT-4, and future OpenAI models
"""

import os
import sys
from typing import List, Dict, Any, Optional

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import config

from .base_provider import BaseLLMProvider, LLMResponse

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider implementation"""
    
    def __init__(self):
        super().__init__(name="openai", cost_tier="premium")
        
        # OpenAI-specific configuration
        self.api_key = None
        self.client = None
        self.organization = None
        
        # Model configurations with latest models and pricing
        self.model_configs = {
            "gpt-4.1": {
                "max_tokens": 1000000,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.060,
                "context_window": 1000000,
                "description": "Latest GPT-4.1 with 1M context and June 2024 knowledge cutoff"
            },
            "gpt-4o": {
                "max_tokens": 128000,
                "cost_per_1k_input": 0.005,
                "cost_per_1k_output": 0.015,
                "context_window": 128000,
                "description": "Most advanced multimodal model, faster and cheaper than GPT-4 Turbo"
            },
            "gpt-4o-mini": {
                "max_tokens": 128000,
                "cost_per_1k_input": 0.0015,
                "cost_per_1k_output": 0.006,
                "context_window": 128000,
                "description": "Most cost-efficient small model with vision capabilities"
            },
            "gpt-4-turbo": {
                "max_tokens": 128000,
                "cost_per_1k_input": 0.01,
                "cost_per_1k_output": 0.03,
                "context_window": 128000,
                "description": "GPT-4 Turbo with 128k context and fresher knowledge"
            },
            "gpt-4": {
                "max_tokens": 8192,
                "cost_per_1k_input": 0.03,
                "cost_per_1k_output": 0.06,
                "context_window": 8192,
                "description": "Original GPT-4 model"
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "cost_per_1k_input": 0.0015,
                "cost_per_1k_output": 0.002,
                "context_window": 4096,
                "description": "Fast and economical model for simple tasks"
            }
        }
        
        self.default_model = "gpt-4o-mini"
        self.supports_streaming = True
        self.supports_functions = True
    
    def _initialize(self) -> bool:
        """Initialize OpenAI provider"""
        try:
            # Get API key from config
            self.api_key = config.get_api_key("openai")
            
            if not self.api_key:
                print(f"❌ {self.name}: No API key found")
                return False
            
            # Try to import OpenAI
            import openai
            
            # Set up client
            openai.api_key = self.api_key
            
            # Get organization if available
            self.organization = config.get_env_var("OPENAI_ORG_ID")
            if self.organization:
                openai.organization = self.organization
            
            self.client = openai
            
            # Test connection
            success, message = self.test_connection()
            if success:
                self.is_available = True
                self.models = list(self.model_configs.keys())
                print(f"✅ {self.name}: Initialized successfully")
                return True
            else:
                print(f"❌ {self.name}: {message}")
                return False
                
        except ImportError:
            print(f"❌ {self.name}: OpenAI package not installed. Run: pip install openai")
            return False
        except Exception as e:
            print(f"❌ {self.name}: Initialization failed - {str(e)}")
            return False
    
    def _get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> LLMResponse:
        """Get response from OpenAI API"""
        try:
            # Extract parameters
            max_tokens = kwargs.get("max_tokens", 1000)
            temperature = kwargs.get("temperature", 0.7)
            top_p = kwargs.get("top_p", 1.0)
            
            # Estimate input tokens (rough approximation)
            input_text = " ".join([msg.get("content", "") for msg in messages])
            input_tokens = len(input_text) // 4  # Rough token estimation
            
            # Make API call
            response = self.client.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                **{k: v for k, v in kwargs.items() 
                   if k not in ["max_tokens", "temperature", "top_p"]}
            )
            
            # Extract response data
            content = response.choices[0].message.content
            
            # Get token usage if available
            usage = response.get("usage", {})
            actual_input_tokens = usage.get("prompt_tokens", input_tokens)
            output_tokens = usage.get("completion_tokens", len(content) // 4)
            
            # Calculate cost
            cost = self.estimate_cost(actual_input_tokens, output_tokens, model)
            
            return LLMResponse(
                success=True,
                content=content,
                model_used=model,
                provider_name=self.name,
                input_tokens=actual_input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                metadata={
                    "usage": usage,
                    "finish_reason": response.choices[0].get("finish_reason"),
                    "response_id": response.get("id")
                }
            )
            
        except Exception as e:
            error_msg = str(e)
            
            # Parse specific OpenAI errors
            if "insufficient_quota" in error_msg:
                error_msg = "OpenAI API quota exceeded"
            elif "invalid_api_key" in error_msg:
                error_msg = "Invalid OpenAI API key"
            elif "model_not_found" in error_msg:
                error_msg = f"Model '{model}' not found"
            elif "rate_limit" in error_msg:
                error_msg = "OpenAI API rate limit exceeded"
            
            return LLMResponse(
                success=False,
                content="",
                model_used=model,
                provider_name=self.name,
                error_message=error_msg
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        if self.is_available:
            return list(self.model_configs.keys())
        return []
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for OpenAI API usage"""
        if model not in self.model_configs:
            return 0.0
        
        config = self.model_configs[model]
        
        input_cost = (input_tokens / 1000) * config["cost_per_1k_input"]
        output_cost = (output_tokens / 1000) * config["cost_per_1k_output"]
        
        return round(input_cost + output_cost, 6)
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        if model in self.model_configs:
            return self.model_configs[model].copy()
        return {}
    
    def set_organization(self, org_id: str):
        """Set OpenAI organization ID"""
        self.organization = org_id
        if self.client:
            self.client.organization = org_id