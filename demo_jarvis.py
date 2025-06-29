#!/usr/bin/env python3
"""
Demo script showing JARVIS personality and time-based responses
"""

from jarvis_personality import jarvis_personality
import time

def demo_responses():
    """Demo the different JARVIS responses"""
    print("🎬 JARVIS PERSONALITY DEMO")
    print("=" * 50)
    
    print("\n⏰ TIME-BASED GREETING:")
    greeting = jarvis_personality.get_time_based_greeting()
    print(f"🤖 JARVIS: {greeting}")
    
    print("\n👋 WAKE RESPONSE:")
    wake_response = jarvis_personality.get_wake_response()
    print(f"🤖 JARVIS: {wake_response}")
    
    print("\n❓ CONTEXTUAL QUESTION:")
    question = jarvis_personality.get_contextual_questions()
    print(f"🤖 JARVIS: {question}")
    
    print("\n🤔 THINKING RESPONSE:")
    thinking = jarvis_personality.get_thinking_response()
    print(f"🤖 JARVIS: {thinking}")
    
    print("\n✅ ACKNOWLEDGMENT:")
    ack = jarvis_personality.get_acknowledgment()
    print(f"🤖 JARVIS: {ack}")
    
    print("\n⚠️  ERROR RESPONSE:")
    error = jarvis_personality.get_error_response()
    print(f"🤖 JARVIS: {error}")
    
    print("\n👋 GOODBYE:")
    goodbye = jarvis_personality.get_goodbye_response()
    print(f"🤖 JARVIS: {goodbye}")
    
    print("\n" + "=" * 50)
    print("💡 This is how JARVIS will respond when you say 'Jarvis'!")
    print("💡 Run: python3 app_jarvis.py to start the full system")

if __name__ == "__main__":
    demo_responses()