"""
Claude (Anthropic) Provider for Advanced JARVIS
Supports Claude-3 models and future Anthropic models
"""

import os
import sys
from typing import List, Dict, Any, Optional

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import config

from .base_provider import BaseLLMProvider, LLMResponse

class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self):
        super().__init__(name="claude", cost_tier="mid")
        
        # Claude-specific configuration
        self.api_key = None
        self.client = None
        
        # Model configurations
        self.model_configs = {
            "claude-3-opus-20240229": {
                "max_tokens": 200000,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075,
                "context_window": 200000
            },
            "claude-3-sonnet-20240229": {
                "max_tokens": 200000,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
                "context_window": 200000
            },
            "claude-3-haiku-20240307": {
                "max_tokens": 200000,
                "cost_per_1k_input": 0.00025,
                "cost_per_1k_output": 0.00125,
                "context_window": 200000
            },
            "claude-3-5-sonnet-20241022": {
                "max_tokens": 200000,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
                "context_window": 200000
            }
        }
        
        # Simplified model names
        self.model_aliases = {
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-sonnet-20240229", 
            "claude-3-haiku": "claude-3-haiku-20240307",
            "claude-3.5-sonnet": "claude-3-5-sonnet-20241022"
        }
        
        self.default_model = "claude-3-haiku-20240307"
        self.supports_streaming = True
        self.supports_functions = False  # Claude doesn't support function calling yet
    
    def _initialize(self) -> bool:
        """Initialize Claude provider"""
        try:
            # Get API key from config
            self.api_key = config.get_api_key("claude")
            
            if not self.api_key:
                print(f"❌ {self.name}: No API key found")
                return False
            
            # Try to import Anthropic
            import anthropic
            
            # Set up client
            self.client = anthropic.Anthropic(api_key=self.api_key)
            
            # Test connection
            success, message = self.test_connection()
            if success:
                self.is_available = True
                self.models = list(self.model_configs.keys()) + list(self.model_aliases.keys())
                print(f"✅ {self.name}: Initialized successfully")
                return True
            else:
                print(f"❌ {self.name}: {message}")
                return False
                
        except ImportError:
            print(f"❌ {self.name}: Anthropic package not installed. Run: pip install anthropic")
            return False
        except Exception as e:
            print(f"❌ {self.name}: Initialization failed - {str(e)}")
            return False
    
    def _resolve_model_name(self, model: str) -> str:
        """Resolve model alias to full model name"""
        return self.model_aliases.get(model, model)
    
    def _get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> LLMResponse:
        """Get response from Claude API"""
        try:
            # Resolve model name
            resolved_model = self._resolve_model_name(model)
            
            # Extract parameters
            max_tokens = kwargs.get("max_tokens", 1000)
            temperature = kwargs.get("temperature", 0.7)
            
            # Convert messages to Claude format
            system_message = ""
            conversation_messages = []
            
            for msg in messages:
                if msg.get("role") == "system":
                    system_message += msg.get("content", "") + "\n"
                else:
                    conversation_messages.append({
                        "role": msg.get("role"),
                        "content": msg.get("content", "")
                    })
            
            # Estimate input tokens
            input_text = system_message + " ".join([msg.get("content", "") for msg in conversation_messages])
            input_tokens = len(input_text) // 4  # Rough token estimation
            
            # Make API call
            response = self.client.messages.create(
                model=resolved_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message.strip() if system_message.strip() else None,
                messages=conversation_messages
            )
            
            # Extract response data
            content = response.content[0].text if response.content else ""
            
            # Get token usage if available
            input_tokens = getattr(response.usage, 'input_tokens', input_tokens)
            output_tokens = getattr(response.usage, 'output_tokens', len(content) // 4)
            
            # Calculate cost
            cost = self.estimate_cost(input_tokens, output_tokens, resolved_model)
            
            return LLMResponse(
                success=True,
                content=content,
                model_used=resolved_model,
                provider_name=self.name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                metadata={
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens
                    },
                    "stop_reason": getattr(response, 'stop_reason', None),
                    "response_id": getattr(response, 'id', None)
                }
            )
            
        except Exception as e:
            error_msg = str(e)
            
            # Parse specific Claude errors
            if "rate_limit" in error_msg.lower():
                error_msg = "Claude API rate limit exceeded"
            elif "invalid_api_key" in error_msg.lower():
                error_msg = "Invalid Anthropic API key"
            elif "model_not_found" in error_msg.lower():
                error_msg = f"Claude model '{model}' not found"
            elif "insufficient_quota" in error_msg.lower():
                error_msg = "Claude API quota exceeded"
            
            return LLMResponse(
                success=False,
                content="",
                model_used=model,
                provider_name=self.name,
                error_message=error_msg
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available Claude models"""
        if self.is_available:
            return list(self.model_configs.keys()) + list(self.model_aliases.keys())
        return []
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for Claude API usage"""
        resolved_model = self._resolve_model_name(model)
        
        if resolved_model not in self.model_configs:
            return 0.0
        
        model_config = self.model_configs[resolved_model]
        
        input_cost = (input_tokens / 1000) * model_config["cost_per_1k_input"]
        output_cost = (output_tokens / 1000) * model_config["cost_per_1k_output"]
        
        return round(input_cost + output_cost, 6)
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        resolved_model = self._resolve_model_name(model)
        
        if resolved_model in self.model_configs:
            info = self.model_configs[resolved_model].copy()
            info["display_name"] = model
            info["full_name"] = resolved_model
            return info
        return {}
    
    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Claude API"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            response = self._get_response(test_messages, self.default_model, max_tokens=10)
            
            if response.success:
                return True, f"Connection to {self.name} successful"
            else:
                return False, f"Connection failed: {response.error_message}"
                
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"