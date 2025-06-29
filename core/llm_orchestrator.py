import os
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading

from core.budget_manager import budget_manager

class LLMOrchestrator:
    """
    Intelligent LLM manager that handles fallbacks and budget-aware switching
    ChatGPT-4 → Claude → Local Llama → Emergency Responses
    """
    
    def __init__(self):
        self.lock = threading.Lock()
        self.context_history = []
        self.max_context_length = 4000  # tokens
        
        # LLM preference order (most preferred first)
        self.llm_chain = [
            {
                "name": "openai",
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "available": self._check_openai_available(),
                "cost_tier": "premium"
            },
            {
                "name": "claude",
                "models": ["claude-3-sonnet", "claude-3-haiku"],
                "available": self._check_claude_available(),
                "cost_tier": "mid"
            },
            {
                "name": "llama",
                "models": ["llama-7b", "llama-13b"],
                "available": self._check_llama_available(),
                "cost_tier": "free"
            },
            {
                "name": "emergency",
                "models": ["hardcoded"],
                "available": True,
                "cost_tier": "free"
            }
        ]
        
        # Emergency responses for when all else fails
        self.emergency_responses = [
            "I'm experiencing technical difficulties, Sir. My systems are temporarily limited.",
            "My apologies, Sir. I'm operating in emergency mode with reduced capabilities.",
            "Systems are currently constrained, Sir. I'll provide basic assistance.",
            "Technical limitations detected, Sir. Running on backup protocols.",
            "I'm in conservation mode, Sir. How may I assist with essential tasks?"
        ]
        
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def _check_openai_available(self) -> bool:
        """Check if OpenAI API is available"""
        return bool(os.getenv("OPENAI_API_KEY"))
    
    def _check_claude_available(self) -> bool:
        """Check if Claude API is available"""
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    
    def _check_llama_available(self) -> bool:
        """Check if local Llama is available"""
        try:
            # Check if ollama or local LLM server is running
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars = 1 token)"""
        return max(1, len(text) // 4)
    
    def _compress_context(self, messages: List[Dict]) -> List[Dict]:
        """Compress context to fit within limits while preserving essential info"""
        if not messages:
            return []
        
        total_tokens = sum(self._estimate_tokens(str(msg)) for msg in messages)
        
        if total_tokens <= self.max_context_length:
            return messages
        
        # Keep system message and last few exchanges
        compressed = []
        
        # Always keep system message if present
        if messages and messages[0].get("role") == "system":
            compressed.append(messages[0])
            messages = messages[1:]
        
        # Keep the most recent messages that fit in budget
        remaining_tokens = self.max_context_length - sum(self._estimate_tokens(str(msg)) for msg in compressed)
        
        for msg in reversed(messages):
            msg_tokens = self._estimate_tokens(str(msg))
            if msg_tokens <= remaining_tokens:
                compressed.insert(-len([m for m in compressed if m.get("role") != "system"]), msg)
                remaining_tokens -= msg_tokens
            else:
                break
        
        # Add summary if we compressed a lot
        if len(compressed) < len(messages) + (1 if messages and messages[0].get("role") == "system" else 0):
            summary_msg = {
                "role": "system",
                "content": f"[Previous conversation context compressed. Continuing conversation with essential context preserved.]"
            }
            if compressed and compressed[0].get("role") == "system":
                compressed.insert(1, summary_msg)
            else:
                compressed.insert(0, summary_msg)
        
        return compressed
    
    def _call_openai(self, messages: List[Dict], model: str = "gpt-3.5-turbo") -> Tuple[str, float]:
        """Call OpenAI API"""
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            # Estimate cost
            input_tokens = sum(self._estimate_tokens(msg.get("content", "")) for msg in messages)
            estimated_cost = budget_manager.calculate_cost("openai", model, input_tokens, input_tokens // 2)
            
            # Check budget
            can_afford, reason = budget_manager.can_afford("openai", estimated_cost)
            if not can_afford:
                raise Exception(f"Budget exceeded: {reason}")
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            
            # Record actual usage
            output_tokens = self._estimate_tokens(result)
            actual_cost = budget_manager.calculate_cost("openai", model, input_tokens, output_tokens)
            budget_manager.record_usage("openai", actual_cost, model)
            
            return result, actual_cost
            
        except Exception as e:
            raise Exception(f"OpenAI error: {str(e)}")
    
    def _call_claude(self, messages: List[Dict], model: str = "claude-3-haiku") -> Tuple[str, float]:
        """Call Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            
            # Convert messages format
            system_msg = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg += msg["content"] + "\n"
                else:
                    user_messages.append(msg)
            
            # Estimate cost
            input_tokens = sum(self._estimate_tokens(msg.get("content", "")) for msg in messages)
            estimated_cost = budget_manager.calculate_cost("claude", model, input_tokens, input_tokens // 2)
            
            # Check budget
            can_afford, reason = budget_manager.can_afford("claude", estimated_cost)
            if not can_afford:
                raise Exception(f"Budget exceeded: {reason}")
            
            response = client.messages.create(
                model=model,
                max_tokens=1000,
                system=system_msg,
                messages=user_messages
            )
            
            result = response.content[0].text
            
            # Record actual usage
            output_tokens = self._estimate_tokens(result)
            actual_cost = budget_manager.calculate_cost("claude", model, input_tokens, output_tokens)
            budget_manager.record_usage("claude", actual_cost, model)
            
            return result, actual_cost
            
        except Exception as e:
            raise Exception(f"Claude error: {str(e)}")
    
    def _call_llama(self, messages: List[Dict], model: str = "llama2") -> Tuple[str, float]:
        """Call local Llama model"""
        try:
            import requests
            
            # Convert messages to prompt
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n"
                elif msg["role"] == "user":
                    prompt += f"Human: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
            
            prompt += "Assistant: "
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 500,
                        "temperature": 0.7
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                return result.strip(), 0.0  # Local is free
            else:
                raise Exception(f"Llama server error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Local Llama error: {str(e)}")
    
    def _get_emergency_response(self, user_input: str) -> str:
        """Get emergency hardcoded response"""
        import random
        
        # Simple keyword matching for basic responses
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["time", "clock", "hour"]):
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%I:%M %p')}, Sir."
        
        elif any(word in user_lower for word in ["weather", "temperature"]):
            return "I'm unable to check the weather in emergency mode, Sir. Please try again later."
        
        elif any(word in user_lower for word in ["hello", "hi", "hey"]):
            return "Hello, Sir. I'm operating in emergency mode with limited capabilities."
        
        elif any(word in user_lower for word in ["thank", "thanks"]):
            return "You're welcome, Sir."
        
        elif any(word in user_lower for word in ["goodbye", "bye", "exit"]):
            return "Goodbye, Sir. I hope my systems will be fully operational soon."
        
        else:
            return random.choice(self.emergency_responses)
    
    def get_response(self, user_input: str, system_message: str = None) -> Dict[str, Any]:
        """
        Get response using intelligent LLM fallback chain
        Returns: {
            "response": str,
            "source": str,
            "cost": float,
            "model": str,
            "context_compressed": bool
        }
        """
        with self.lock:
            # Build messages
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            # Add compressed context
            compressed_context = self._compress_context(self.context_history)
            messages.extend(compressed_context)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            context_was_compressed = len(compressed_context) < len(self.context_history)
            
            # Try each LLM in order
            for llm_config in self.llm_chain:
                if not llm_config["available"]:
                    continue
                
                llm_name = llm_config["name"]
                models = llm_config["models"]
                
                print(f"🤖 Trying {llm_name}...")
                
                for model in models:
                    try:
                        if llm_name == "openai":
                            response, cost = self._call_openai(messages, model)
                        elif llm_name == "claude":
                            response, cost = self._call_claude(messages, model)
                        elif llm_name == "llama":
                            response, cost = self._call_llama(messages, model)
                        elif llm_name == "emergency":
                            response = self._get_emergency_response(user_input)
                            cost = 0.0
                        
                        # Success! Update context and return
                        self.context_history.append({"role": "user", "content": user_input})
                        self.context_history.append({"role": "assistant", "content": response})
                        
                        # Keep context manageable
                        if len(self.context_history) > 20:
                            self.context_history = self.context_history[-16:]
                        
                        return {
                            "response": response,
                            "source": llm_name,
                            "cost": cost,
                            "model": model,
                            "context_compressed": context_was_compressed,
                            "success": True
                        }
                        
                    except Exception as e:
                        print(f"❌ {llm_name} ({model}) failed: {str(e)}")
                        continue
            
            # If we get here, everything failed
            emergency_response = self._get_emergency_response(user_input)
            return {
                "response": emergency_response,
                "source": "emergency_fallback",
                "cost": 0.0,
                "model": "hardcoded",
                "context_compressed": False,
                "success": False,
                "error": "All LLMs failed"
            }
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            "available_llms": [
                {
                    "name": llm["name"],
                    "available": llm["available"],
                    "cost_tier": llm["cost_tier"]
                }
                for llm in self.llm_chain
            ],
            "context_length": len(self.context_history),
            "budget_status": budget_manager.get_budget_status()
        }
    
    def clear_context(self):
        """Clear conversation context"""
        with self.lock:
            self.context_history.clear()
            print("🧹 Context cleared")
    
    def set_context_limit(self, limit: int):
        """Set maximum context length"""
        self.max_context_length = limit
        print(f"📏 Context limit set to {limit} tokens")


# Global orchestrator instance
llm_orchestrator = LLMOrchestrator()