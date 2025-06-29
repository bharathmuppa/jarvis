#!/usr/bin/env python3
"""
Advanced JARVIS - Multi-tier AI System with Budget Management
Iron Man + Paranoid Android personality with intelligent fallbacks
"""

import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import argparse

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.budget_manager import budget_manager
from core.llm_orchestrator import llm_orchestrator
from core.voice_manager import voice_manager
from core.mcp_router import mcp_router
from jarvis_personality import jarvis_personality
from speechrecognizers.WakeWordRecognizer import listen_with_wake_word

class AdvancedJarvis:
    """
    The main JARVIS system orchestrating all components
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.is_running = True
        self.system_health = {
            "budget": "green",
            "llm": "green", 
            "voice": "green",
            "mcp": "green"
        }
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize all JARVIS subsystems"""
        print("🤖" + "="*60 + "🤖")
        print("           ADVANCED JARVIS INITIALIZATION")
        print("🤖" + "="*60 + "🤖")
        
        # Check budget status
        print("\n💰 Initializing Budget Manager...")
        budget_status = budget_manager.get_budget_status()
        budget_manager.print_budget_summary()
        
        # Adapt personality to budget
        adaptation_msg = jarvis_personality.adapt_to_budget_constraints(budget_status)
        print(f"🧠 {adaptation_msg}")
        
        # Check LLM availability
        print("\n🧠 Initializing LLM Orchestrator...")
        llm_status = llm_orchestrator.get_status()
        available_llms = [llm["name"] for llm in llm_status["available_llms"] if llm["available"]]
        print(f"✅ Available LLMs: {', '.join(available_llms)}")
        
        # Check voice systems
        print("\n🔊 Initializing Voice Manager...")
        voice_status = voice_manager.get_status()
        available_voices = [tier["name"] for tier in voice_status["available_tiers"] if tier["available"]]
        print(f"✅ Available Voice Tiers: {', '.join(available_voices)}")
        
        # Check MCP agents
        print("\n📡 Initializing MCP Router...")
        mcp_status = mcp_router.get_agent_status()
        print(f"✅ MCP Agents: {mcp_status['healthy_agents']}/{mcp_status['total_agents']} healthy")
        print(f"✅ Available Capabilities: {', '.join(mcp_status.get('capabilities', [])[:5])}...")
        
        # System ready
        greeting = jarvis_personality.get_time_based_greeting()
        print(f"\n🤖 JARVIS: {greeting}")
        print("🤖 JARVIS: Advanced systems online. Say 'Jarvis' to begin.")
        
        # Speak greeting
        self._speak_async(greeting)
        time.sleep(1)
        self._speak_async("Advanced systems online. Say 'Jarvis' to begin.")
    
    def _speak_async(self, text: str):
        """Speak text asynchronously"""
        def speak():
            try:
                result = voice_manager.speak(text)
                if not result["success"]:
                    print(f"🔊 Voice fallback: {text}")
            except Exception as e:
                print(f"🔊 Voice error: {e}")
                print(f"📝 Text: {text}")
        
        self.executor.submit(speak)
    
    def _process_command_advanced(self, command: str) -> dict:
        """Process command using advanced multi-tier system"""
        start_time = time.time()
        
        # Check if it's an MCP-routable request
        mcp_keywords = {
            "weather": "weather",
            "calculate": "calculator", 
            "time": "time",
            "system": "system_info"
        }
        
        for keyword, capability in mcp_keywords.items():
            if keyword in command.lower():
                print(f"📡 Routing to MCP: {capability}")
                try:
                    mcp_result = mcp_router.route_request_sync(capability, {"query": command})
                    if mcp_result["success"]:
                        return {
                            "response": mcp_result["data"],
                            "source": f"mcp_{mcp_result.get('agent', 'system')}",
                            "processing_time": time.time() - start_time,
                            "cost": 0.0
                        }
                except Exception as e:
                    print(f"❌ MCP routing failed: {e}")
        
        # Fall back to LLM orchestrator
        print("🧠 Processing with LLM Orchestrator...")
        system_message = (
            "You are JARVIS, Tony Stark's AI assistant. Be efficient, helpful, and occasionally witty. "
            "Keep responses concise and professional. Address the user as 'Sir'."
        )
        
        llm_result = llm_orchestrator.get_response(command, system_message)
        llm_result["processing_time"] = time.time() - start_time
        
        return llm_result
    
    def _handle_system_commands(self, command: str) -> tuple[bool, str]:
        """Handle special system commands"""
        cmd_lower = command.lower().strip()
        
        if any(word in cmd_lower for word in ["exit", "quit", "shutdown", "goodbye"]):
            farewell = jarvis_personality.get_goodbye_response()
            return True, farewell
        
        elif "budget status" in cmd_lower or "budget summary" in cmd_lower:
            budget_manager.print_budget_summary()
            return True, "Budget summary displayed, Sir."
        
        elif "system status" in cmd_lower or "diagnostics" in cmd_lower:
            status_report = jarvis_personality.get_status_report()
            return True, status_report
        
        elif "efficiency mode" in cmd_lower:
            if "enable" in cmd_lower or "on" in cmd_lower:
                response = jarvis_personality.set_efficiency_mode(True)
            elif "disable" in cmd_lower or "off" in cmd_lower:
                response = jarvis_personality.set_efficiency_mode(False)
            else:
                current_mode = "enabled" if jarvis_personality.efficiency_mode else "disabled"
                response = f"Efficiency mode is currently {current_mode}, Sir."
            return True, response
        
        elif "sarcasm" in cmd_lower:
            if "increase" in cmd_lower or "more" in cmd_lower:
                new_level = min(1.0, jarvis_personality.sarcasm_level + 0.2)
                response = jarvis_personality.set_sarcasm_level(new_level)
            elif "decrease" in cmd_lower or "less" in cmd_lower:
                new_level = max(0.0, jarvis_personality.sarcasm_level - 0.2)
                response = jarvis_personality.set_sarcasm_level(new_level)
            else:
                response = f"Current sarcasm level: {jarvis_personality.sarcasm_level:.1f}, Sir."
            return True, response
        
        elif "voice" in cmd_lower and "tier" in cmd_lower:
            voice_status = voice_manager.get_status()
            available = [t["name"] for t in voice_status["available_tiers"] if t["available"]]
            return True, f"Available voice tiers: {', '.join(available)}. Current: {voice_status['current_preference']}"
        
        elif "paranoid" in cmd_lower:
            paranoid_response = jarvis_personality.get_paranoid_android_response(0.8)
            return True, paranoid_response
        
        return False, ""
    
    def _update_system_health(self):
        """Update system health indicators"""
        # Check budget health
        budget_status = budget_manager.get_budget_status()
        total_remaining = sum(
            service.get("remaining", {}).get("daily", 0) 
            for service in budget_status.values()
        )
        
        if total_remaining < 1.0:
            self.system_health["budget"] = "red"
        elif total_remaining < 5.0:
            self.system_health["budget"] = "yellow"
        else:
            self.system_health["budget"] = "green"
        
        # Check LLM health
        llm_status = llm_orchestrator.get_status()
        available_count = sum(1 for llm in llm_status["available_llms"] if llm["available"])
        if available_count == 0:
            self.system_health["llm"] = "red"
        elif available_count == 1:
            self.system_health["llm"] = "yellow"
        else:
            self.system_health["llm"] = "green"
        
        # Check voice health
        voice_status = voice_manager.get_status()
        if not any(tier["available"] for tier in voice_status["available_tiers"]):
            self.system_health["voice"] = "red"
        else:
            self.system_health["voice"] = "green"
        
        # Check MCP health
        mcp_status = mcp_router.get_agent_status()
        healthy_ratio = mcp_status["healthy_agents"] / max(1, mcp_status["total_agents"])
        if healthy_ratio < 0.5:
            self.system_health["mcp"] = "red"
        elif healthy_ratio < 0.8:
            self.system_health["mcp"] = "yellow"
        else:
            self.system_health["mcp"] = "green"
    
    def run(self):
        """Main JARVIS execution loop"""
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while self.is_running:
            try:
                print("\n" + "🎯" + "-"*50 + "🎯")
                print("👂 Waiting for 'Jarvis' wake word...")
                
                # Update system health
                self._update_system_health()
                
                # Health status indicator
                health_icons = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
                health_display = " ".join([
                    f"{component}:{health_icons[status]}" 
                    for component, status in self.system_health.items()
                ])
                print(f"📊 System Health: {health_display}")
                print("🎯" + "-"*50 + "🎯")
                
                # Listen for wake word and command
                command = listen_with_wake_word(self._speak_async)
                
                # Handle different response types
                if command in ["timeout", "unclear"]:
                    consecutive_errors += 1
                    
                    if consecutive_errors == 1:
                        if jarvis_personality.efficiency_mode:
                            response = jarvis_personality.get_efficient_response("error")
                        else:
                            response = "I didn't catch that, Sir. Could you repeat your request?"
                        
                        print(f"🤖 JARVIS: {response}")
                        self._speak_async(response)
                    
                    if consecutive_errors >= max_consecutive_errors:
                        print("💤 Entering quiet mode...")
                        consecutive_errors = 0
                    
                    continue
                
                elif command.startswith("error:"):
                    print(f"🚫 System error: {command}")
                    error_response = jarvis_personality.get_error_response()
                    self._speak_async(error_response)
                    continue
                
                # Valid command received
                consecutive_errors = 0
                print(f"👤 You: {command}")
                
                # Handle system commands
                is_system_cmd, system_response = self._handle_system_commands(command)
                if is_system_cmd:
                    if "exit" in command.lower() or "quit" in command.lower():
                        print(f"🤖 JARVIS: {system_response}")
                        self._speak_async(system_response)
                        time.sleep(3)
                        break
                    else:
                        print(f"🤖 JARVIS: {system_response}")
                        self._speak_async(system_response)
                        continue
                
                # Process command through advanced system
                if jarvis_personality.efficiency_mode:
                    thinking_msg = jarvis_personality.get_efficient_response("processing")
                else:
                    thinking_msg = jarvis_personality.get_thinking_response()
                
                print(f"🤖 JARVIS: {thinking_msg}")
                
                # Process command
                result = self._process_command_advanced(command)
                
                if result["success"]:
                    response = result["response"]
                    source = result["source"]
                    cost = result.get("cost", 0.0)
                    processing_time = result.get("processing_time", 0.0)
                    
                    # Format response if it's structured data
                    if isinstance(response, dict):
                        if "time" in response:
                            response = f"The current time is {response['time']}, Sir."
                        elif "result" in response:
                            response = f"The result is {response['result']}, Sir."
                        else:
                            response = str(response)
                    
                    print(f"🤖 JARVIS: {response}")
                    print(f"📊 Source: {source} | Cost: ${cost:.6f} | Time: {processing_time:.2f}s")
                    
                    # Speak response
                    self._speak_async(response)
                    
                else:
                    error_msg = jarvis_personality.get_error_response()
                    print(f"❌ JARVIS: {error_msg}")
                    self._speak_async(error_msg)
                
            except KeyboardInterrupt:
                print("\n👋 JARVIS interrupted by user.")
                farewell = jarvis_personality.get_goodbye_response()
                print(f"🤖 JARVIS: {farewell}")
                self._speak_async(farewell)
                time.sleep(2)
                break
            
            except Exception as e:
                print(f"❌ Unexpected system error: {e}")
                emergency_response = jarvis_personality.get_emergency_protocol_response()
                print(f"🚨 JARVIS: {emergency_response}")
                self._speak_async(emergency_response)
                time.sleep(1)
                continue
        
        # Cleanup
        self.executor.shutdown(wait=True)
        print("🤖 JARVIS systems shutdown complete.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Advanced JARVIS AI Assistant")
    parser.add_argument("--budget-summary", action="store_true", help="Show budget summary and exit")
    parser.add_argument("--system-status", action="store_true", help="Show system status and exit")
    parser.add_argument("--voice-test", type=str, help="Test voice system with given text")
    parser.add_argument("--install-packages", action="store_true", help="Show missing package installation commands")
    
    args = parser.parse_args()
    
    if args.budget_summary:
        budget_manager.print_budget_summary()
        return
    
    if args.system_status:
        print("🔍 SYSTEM STATUS")
        print("="*50)
        
        # LLM Status
        llm_status = llm_orchestrator.get_status()
        print("\n🧠 LLM Status:")
        for llm in llm_status["available_llms"]:
            status_icon = "✅" if llm["available"] else "❌"
            print(f"  {status_icon} {llm['name']} ({llm['cost_tier']})")
        
        # Voice Status
        voice_status = voice_manager.get_status()
        print("\n🔊 Voice Status:")
        for tier in voice_status["available_tiers"]:
            status_icon = "✅" if tier["available"] else "❌"
            print(f"  {status_icon} {tier['name']} ({tier['quality']})")
        
        # MCP Status
        mcp_status = mcp_router.get_agent_status()
        print(f"\n📡 MCP Status: {mcp_status['healthy_agents']}/{mcp_status['total_agents']} agents healthy")
        
        budget_manager.print_budget_summary()
        return
    
    if args.voice_test:
        print(f"🔊 Testing voice system with: '{args.voice_test}'")
        result = voice_manager.speak(args.voice_test)
        print(f"Result: {result}")
        return
    
    if args.install_packages:
        voice_manager.install_missing_packages()
        return
    
    # Run main JARVIS system
    jarvis = AdvancedJarvis()
    jarvis.run()


if __name__ == "__main__":
    main()