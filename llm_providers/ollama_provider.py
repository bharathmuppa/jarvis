"""
Ollama Provider for Advanced JARVIS
Supports local Llama models and other models running on Ollama
"""

import os
import sys
import requests
import json
from typing import List, Dict, Any, Optional

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import config

from .base_provider import BaseLLMProvider, LLMResponse

class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider implementation"""
    
    def __init__(self):
        super().__init__(name="ollama", cost_tier="free")
        
        # Ollama-specific configuration
        self.host = config.get_env_var("OLLAMA_HOST", "localhost:11434")
        self.base_url = f"http://{self.host}"
        self.timeout = 60  # seconds
        
        # Available models (will be populated dynamically)
        self.available_models = []
        
        # Common model configurations
        self.model_configs = {
            "llama2": {
                "max_tokens": 4096,
                "context_window": 4096,
                "size": "7B"
            },
            "llama2:13b": {
                "max_tokens": 4096,
                "context_window": 4096,
                "size": "13B"
            },
            "llama2:70b": {
                "max_tokens": 4096,
                "context_window": 4096,
                "size": "70B"
            },
            "codellama": {
                "max_tokens": 4096,
                "context_window": 4096,
                "size": "7B",
                "specialty": "code"
            },
            "mistral": {
                "max_tokens": 8192,
                "context_window": 8192,
                "size": "7B"
            },
            "phi": {
                "max_tokens": 2048,
                "context_window": 2048,
                "size": "2.7B"
            },
            "gemma": {
                "max_tokens": 8192,
                "context_window": 8192,
                "size": "7B"
            }
        }
        
        self.default_model = "llama2"
        self.supports_streaming = True
        self.supports_functions = False
    
    def _initialize(self) -> bool:
        """Initialize Ollama provider"""
        try:
            # Test connection to Ollama server
            success, message = self._test_ollama_connection()
            
            if not success:
                print(f"❌ {self.name}: {message}")
                return False
            
            # Get available models
            self.available_models = self._get_ollama_models()
            
            if not self.available_models:
                print(f"❌ {self.name}: No models available")
                return False
            
            # Set default model to first available
            if self.available_models:
                # Prefer llama2 if available, otherwise use first model
                if "llama2" in self.available_models:
                    self.default_model = "llama2"
                else:
                    self.default_model = self.available_models[0]
            
            self.is_available = True
            self.models = self.available_models
            print(f"✅ {self.name}: Initialized with {len(self.available_models)} models")
            return True
            
        except Exception as e:
            print(f"❌ {self.name}: Initialization failed - {str(e)}")
            return False
    
    def _test_ollama_connection(self) -> tuple[bool, str]:
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"Server returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"Cannot connect to Ollama server at {self.host}"
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def _get_ollama_models(self) -> List[str]:
        """Get list of models available in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return models
            return []
        except Exception:
            return []
    
    def _get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> LLMResponse:
        """Get response from Ollama API"""
        try:
            # Extract parameters
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1000)
            
            # Convert messages to prompt format
            prompt = self._messages_to_prompt(messages)
            
            # Estimate input tokens
            input_tokens = len(prompt) // 4  # Rough estimation
            
            # Prepare request
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            # Make API call
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("response", "")
                
                # Estimate output tokens
                output_tokens = len(content) // 4
                
                return LLMResponse(
                    success=True,
                    content=content,
                    model_used=model,
                    provider_name=self.name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=0.0,  # Local models are free
                    metadata={
                        "total_duration": data.get("total_duration"),
                        "load_duration": data.get("load_duration"),
                        "prompt_eval_count": data.get("prompt_eval_count"),
                        "eval_count": data.get("eval_count"),
                        "done": data.get("done")
                    }
                )
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", f"HTTP {response.status_code}")
                
                return LLMResponse(
                    success=False,
                    content="",
                    model_used=model,
                    provider_name=self.name,
                    error_message=f"Ollama API error: {error_msg}"
                )
                
        except requests.exceptions.Timeout:
            return LLMResponse(
                success=False,
                content="",
                model_used=model,
                provider_name=self.name,
                error_message="Request timeout - model may be slow to respond"
            )
        except requests.exceptions.ConnectionError:
            return LLMResponse(
                success=False,
                content="",
                model_used=model,
                provider_name=self.name,
                error_message="Cannot connect to Ollama server"
            )
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                model_used=model,
                provider_name=self.name,
                error_message=f"Ollama error: {str(e)}"
            )
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to a prompt format suitable for Ollama"""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        # Add final prompt for assistant response
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        if self.is_available:
            return self.available_models
        return []
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for Ollama usage (always free)"""
        return 0.0
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        # Check if we have predefined config
        if model in self.model_configs:
            return self.model_configs[model].copy()
        
        # Try to get info from Ollama
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "size": data.get("details", {}).get("parameter_size", "unknown"),
                    "family": data.get("details", {}).get("family", "unknown"),
                    "format": data.get("details", {}).get("format", "unknown"),
                    "modified_at": data.get("modified_at"),
                    "size_bytes": data.get("size")
                }
        except Exception:
            pass
        
        return {"size": "unknown", "type": "local"}
    
    def refresh_models(self) -> List[str]:
        """Refresh the list of available models"""
        self.available_models = self._get_ollama_models()
        self.models = self.available_models
        return self.available_models
    
    def pull_model(self, model_name: str) -> tuple[bool, str]:
        """Pull a model to Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minutes for model download
            )
            
            if response.status_code == 200:
                # Refresh available models
                self.refresh_models()
                return True, f"Model '{model_name}' pulled successfully"
            else:
                return False, f"Failed to pull model: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Model pull timeout (this is normal for large models)"
        except Exception as e:
            return False, f"Error pulling model: {str(e)}"
    
    def delete_model(self, model_name: str) -> tuple[bool, str]:
        """Delete a model from Ollama"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/delete",
                json={"name": model_name},
                timeout=30
            )
            
            if response.status_code == 200:
                # Refresh available models
                self.refresh_models()
                return True, f"Model '{model_name}' deleted successfully"
            else:
                return False, f"Failed to delete model: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Error deleting model: {str(e)}"