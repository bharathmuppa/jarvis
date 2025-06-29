"""
Emergency Provider for Advanced JARVIS
Provides hardcoded responses when all other LLM providers fail
"""

import os
import sys
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_provider import BaseLLMProvider, LLMResponse

class EmergencyProvider(BaseLLMProvider):
    """Emergency hardcoded response provider"""
    
    def __init__(self):
        super().__init__(name="emergency", cost_tier="free")
        
        # Emergency response templates
        self.response_templates = {
            # Time-related queries
            "time": [
                "The current time is {time}, Sir.",
                "It's {time} right now, Sir.",
                "The time is currently {time}, Sir."
            ],
            
            # Weather queries
            "weather": [
                "I'm unable to check the weather in emergency mode, Sir. Please try again later.",
                "Weather services are temporarily unavailable, Sir.",
                "My weather systems are offline, Sir. I apologize for the inconvenience."
            ],
            
            # General help
            "help": [
                "I'm operating in emergency mode with limited capabilities, Sir.",
                "My systems are currently constrained, Sir. I can only provide basic assistance.",
                "Emergency protocols are active, Sir. How may I help with essential tasks?"
            ],
            
            # Greetings
            "greeting": [
                "Hello, Sir. I'm operating in emergency mode with reduced functionality.",
                "Good day, Sir. My systems are currently in conservation mode.",
                "Hello, Sir. I'm here to assist, though my capabilities are temporarily limited."
            ],
            
            # Thanks
            "thanks": [
                "You're welcome, Sir.",
                "My pleasure, Sir.",
                "At your service, Sir."
            ],
            
            # Goodbye
            "goodbye": [
                "Goodbye, Sir. I hope my systems will be fully operational soon.",
                "Until later, Sir. I'll be here when you need me.",
                "Farewell, Sir. Please try again when my systems are restored."
            ],
            
            # Status queries
            "status": [
                "My systems are currently operating in emergency mode, Sir.",
                "I'm experiencing technical limitations but remain functional, Sir.",
                "Emergency protocols are active. Core systems operational, Sir."
            ],
            
            # Unknown/default
            "unknown": [
                "I'm sorry, Sir. My systems are temporarily limited and I cannot process that request.",
                "I apologize, Sir, but I'm operating in emergency mode and cannot handle complex queries.",
                "My capabilities are currently restricted, Sir. Please try a simpler request.",
                "I'm afraid I cannot assist with that in emergency mode, Sir.",
                "System limitations prevent me from processing that request, Sir."
            ]
        }
        
        # Keyword mappings for intent detection
        self.intent_keywords = {
            "time": ["time", "clock", "hour", "minute", "when", "what time"],
            "weather": ["weather", "temperature", "rain", "sunny", "cloudy", "forecast", "outside"],
            "help": ["help", "assist", "support", "what can you do"],
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
            "thanks": ["thank", "thanks", "appreciate", "grateful"],
            "goodbye": ["goodbye", "bye", "farewell", "see you", "exit", "quit"],
            "status": ["status", "how are you", "system", "health", "operational", "working"]
        }
        
        # Always available
        self.is_available = True
        self.models = ["emergency_v1"]
        self.default_model = "emergency_v1"
    
    def _initialize(self) -> bool:
        """Initialize emergency provider (always succeeds)"""
        print(f"✅ {self.name}: Emergency response system ready")
        return True
    
    def _detect_intent(self, text: str) -> str:
        """Detect user intent from text"""
        text_lower = text.lower()
        
        # Check each intent category
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent
        
        return "unknown"
    
    def _format_response(self, template: str, user_input: str = "") -> str:
        """Format response template with dynamic data"""
        now = datetime.now()
        
        replacements = {
            "{time}": now.strftime("%I:%M %p"),
            "{date}": now.strftime("%A, %B %d, %Y"),
            "{user_input}": user_input
        }
        
        formatted = template
        for placeholder, value in replacements.items():
            formatted = formatted.replace(placeholder, value)
        
        return formatted
    
    def _get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> LLMResponse:
        """Get emergency response based on simple pattern matching"""
        try:
            # Extract the last user message
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            # Detect intent
            intent = self._detect_intent(user_message)
            
            # Get appropriate response template
            templates = self.response_templates.get(intent, self.response_templates["unknown"])
            template = random.choice(templates)
            
            # Format response
            response_content = self._format_response(template, user_message)
            
            # Estimate tokens
            input_tokens = sum(len(msg.get("content", "")) for msg in messages) // 4
            output_tokens = len(response_content) // 4
            
            return LLMResponse(
                success=True,
                content=response_content,
                model_used=model,
                provider_name=self.name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=0.0,  # Emergency responses are free
                metadata={
                    "intent": intent,
                    "template_used": template,
                    "emergency_mode": True
                }
            )
            
        except Exception as e:
            # Even emergency responses can fail, but we try to recover
            fallback_response = "I apologize, Sir, but I'm experiencing critical system errors."
            
            return LLMResponse(
                success=False,
                content=fallback_response,
                model_used=model,
                provider_name=self.name,
                error_message=f"Emergency provider error: {str(e)}"
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available emergency models"""
        return ["emergency_v1"]
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for emergency responses (always free)"""
        return 0.0
    
    def add_response_template(self, intent: str, template: str):
        """Add a new response template for an intent"""
        if intent not in self.response_templates:
            self.response_templates[intent] = []
        
        self.response_templates[intent].append(template)
    
    def add_intent_keywords(self, intent: str, keywords: List[str]):
        """Add keywords for intent detection"""
        if intent not in self.intent_keywords:
            self.intent_keywords[intent] = []
        
        self.intent_keywords[intent].extend(keywords)
    
    def get_response_stats(self) -> Dict[str, Any]:
        """Get statistics about emergency response usage"""
        return {
            "total_intents": len(self.intent_keywords),
            "total_templates": sum(len(templates) for templates in self.response_templates.values()),
            "available_intents": list(self.intent_keywords.keys()),
            "emergency_mode": True
        }
    
    def test_connection(self) -> tuple[bool, str]:
        """Test emergency provider (always succeeds)"""
        return True, "Emergency response system is always available"