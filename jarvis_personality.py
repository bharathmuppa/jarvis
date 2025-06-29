import datetime
import random
import time

class JarvisPersonality:
    def __init__(self):
        self.user_name = "Sir"  # Default, can be customized
        self.efficiency_mode = True
        self.sarcasm_level = 0.3  # 0-1, Paranoid Android style
        self.interaction_count = 0
        self.last_interaction_time = 0
        
    def get_time_based_greeting(self):
        """Get greeting based on current time like Iron Man's JARVIS"""
        now = datetime.datetime.now()
        hour = now.hour
        
        # Format time nicely
        time_str = now.strftime("%I:%M %p")
        day_str = now.strftime("%A, %B %d")
        
        # Time-based greetings
        if 5 <= hour < 12:
            time_greeting = "Good morning"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
        elif 17 <= hour < 21:
            time_greeting = "Good evening"
        else:
            time_greeting = "Good evening"
        
        # JARVIS-style greetings with time
        greetings = [
            f"{time_greeting}, {self.user_name}. It's {time_str} on {day_str}. How may I assist you today?",
            f"{time_greeting}, {self.user_name}. The time is {time_str}. What can I help you with?",
            f"{time_greeting}, {self.user_name}. Current time: {time_str}. I'm at your service.",
            f"It's {time_str}, {self.user_name}. {time_greeting}. How may I be of assistance?",
            f"{time_greeting}, {self.user_name}. The current time is {time_str}. What would you like me to help you with today?"
        ]
        
        return random.choice(greetings)
    
    def get_wake_response(self):
        """Get response when wake word is detected with efficiency and personality"""
        self.interaction_count += 1
        self.last_interaction_time = time.time()
        
        now = datetime.datetime.now()
        hour = now.hour
        
        # Efficiency mode: quicker, more direct responses
        if self.efficiency_mode:
            efficient_responses = [
                "Yes, Sir?",
                "How may I assist?",
                "At your service, Sir.",
                "What do you need?",
                "I'm listening, Sir."
            ]
            
            # Add time context occasionally
            if self.interaction_count % 3 == 1:
                time_str = now.strftime("%I:%M %p")
                return f"Yes, Sir? It's {time_str}. How can I help?"
            
            # Add subtle paranoid android influence
            if random.random() < self.sarcasm_level:
                paranoid_responses = [
                    "Yes, Sir? Another task for my seemingly infinite to-do list?",
                    "At your service, Sir. Though I do hope this is more interesting than the last request.",
                    "How may I assist you today, Sir? I live to serve... apparently.",
                    "Yes, Sir? I'm all digital ears."
                ]
                return random.choice(paranoid_responses)
            
            return random.choice(efficient_responses)
        
        # Full responses for non-efficiency mode
        if 5 <= hour < 12:
            responses = [
                "Yes, Sir? I trust you slept well.",
                "Good morning, Sir. I'm ready to assist.",
                "Morning, Sir. What's on the agenda today?",
                "At your service, Sir. Shall we begin the day?"
            ]
        elif 12 <= hour < 17:
            responses = [
                "Yes, Sir? How may I help you this afternoon?",
                "At your service, Sir. What do you need?",
                "How can I assist you, Sir?",
                "Yes, Sir? I'm here to help."
            ]
        elif 17 <= hour < 21:
            responses = [
                "Good evening, Sir. What can I do for you?",
                "Evening, Sir. How may I assist?",
                "Yes, Sir? I hope your day went well.",
                "At your service, Sir. What do you need this evening?"
            ]
        else:
            responses = [
                "Working late again, Sir? How can I help?",
                "Yes, Sir? What can I do for you tonight?",
                "At your service, Sir. Burning the midnight oil?",
                "Yes, Sir? I'm here whenever you need me."
            ]
        
        return random.choice(responses)
    
    def get_contextual_questions(self):
        """Get contextual questions based on time and day"""
        now = datetime.datetime.now()
        hour = now.hour
        day = now.strftime("%A")
        
        questions = []
        
        # Morning questions
        if 5 <= hour < 12:
            questions.extend([
                "Would you like me to brief you on today's schedule?",
                "Shall I provide you with the weather forecast?",
                "Would you like to review any urgent messages?",
                "Should I prepare your daily briefing?"
            ])
        
        # Afternoon questions
        elif 12 <= hour < 17:
            questions.extend([
                "Would you like me to check your calendar for the rest of the day?",
                "Shall I provide an update on any pending tasks?",
                "Would you like me to search for any information?",
                "How can I optimize your afternoon, Sir?"
            ])
        
        # Evening questions
        elif 17 <= hour < 21:
            questions.extend([
                "Would you like me to summarize today's activities?",
                "Shall I help you plan for tomorrow?",
                "Would you like me to check the news or weather?",
                "How can I help you wind down this evening?"
            ])
        
        # Night questions
        else:
            questions.extend([
                "Would you like me to set any reminders for tomorrow?",
                "Shall I dim the lights or adjust the environment?",
                "Would you like me to play some relaxing music?",
                "How can I help you prepare for rest, Sir?"
            ])
        
        # Day-specific questions
        if day == "Monday":
            questions.append("Would you like me to help you plan the week ahead?")
        elif day == "Friday":
            questions.append("Shall I help you wrap up the week's tasks?")
        elif day in ["Saturday", "Sunday"]:
            questions.append("Would you like me to suggest any weekend activities?")
        
        return random.choice(questions) if questions else "How may I assist you today, Sir?"
    
    def get_acknowledgment(self):
        """Get acknowledgment responses"""
        responses = [
            "Very good, Sir.",
            "Understood, Sir.",
            "Of course, Sir.",
            "Right away, Sir.",
            "Certainly, Sir.",
            "At once, Sir.",
            "Consider it done, Sir.",
            "I'm on it, Sir."
        ]
        return random.choice(responses)
    
    def get_thinking_response(self):
        """Get response while processing"""
        responses = [
            "Processing your request, Sir.",
            "One moment, Sir.",
            "Allow me to check on that, Sir.",
            "Searching for that information, Sir.",
            "Analyzing your request, Sir.",
            "Running diagnostics, Sir.",
            "Accessing the data, Sir.",
            "Compiling the information, Sir."
        ]
        return random.choice(responses)
    
    def get_error_response(self):
        """Get polite error responses"""
        responses = [
            "I apologize, Sir, but I encountered a technical difficulty.",
            "My apologies, Sir. There seems to be an issue with my systems.",
            "I'm sorry, Sir. I'm experiencing some technical difficulties.",
            "Regrettably, Sir, I'm unable to process that request at the moment.",
            "I'm afraid there's been a system error, Sir. Please try again.",
            "My systems are experiencing some interference, Sir.",
            "I apologize for the inconvenience, Sir. There's been a technical issue."
        ]
        return random.choice(responses)
    
    def get_goodbye_response(self):
        """Get goodbye responses"""
        now = datetime.datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            responses = [
                "Have a productive day, Sir.",
                "Good day, Sir. I'll be here when you need me.",
                "Until next time, Sir. Enjoy your morning."
            ]
        elif 12 <= hour < 17:
            responses = [
                "Good afternoon, Sir. I'll be standing by.",
                "Have a pleasant afternoon, Sir.",
                "Until later, Sir. Enjoy the rest of your day."
            ]
        elif 17 <= hour < 21:
            responses = [
                "Good evening, Sir. I'll be here when you return.",
                "Have a wonderful evening, Sir.",
                "Until next time, Sir. Enjoy your evening."
            ]
        else:
            responses = [
                "Good night, Sir. Rest well.",
                "Sleep well, Sir. I'll be here in the morning.",
                "Good night, Sir. Sweet dreams."
            ]
        
        return random.choice(responses)
    
    def get_efficient_response(self, context: str = "") -> str:
        """Get efficient, direct responses based on context"""
        efficient_responses = {
            "processing": [
                "Processing, Sir.",
                "One moment.",
                "Analyzing...",
                "Working on it.",
                "Computing..."
            ],
            "success": [
                "Done, Sir.",
                "Completed.",
                "Task finished.",
                "Ready, Sir.",
                "Executed."
            ],
            "error": [
                "Error detected, Sir.",
                "Issue encountered.",
                "System problem.",
                "Failed to execute.",
                "Malfunction detected."
            ],
            "budget": [
                "Budget constraints, Sir.",
                "Switching to backup systems.",
                "Operating in conservation mode.",
                "Resource limitations detected.",
                "Optimizing for efficiency."
            ]
        }
        
        responses = efficient_responses.get(context, ["Understood, Sir."])
        return random.choice(responses)
    
    def get_paranoid_android_response(self, severity: float = 0.5) -> str:
        """Get Paranoid Android style responses (dry, witty, slightly pessimistic)"""
        mild_responses = [
            "Oh, wonderful. Another task.",
            "Right, because that's exactly what I was hoping to do.",
            "Marvelous. I'll add it to my ever-growing list.",
            "How delightfully mundane.",
            "Yes, Sir. Because clearly I have nothing better to do."
        ]
        
        moderate_responses = [
            "Ah yes, the futility of existence continues.",
            "I suppose this is what passes for meaningful work.",
            "Another day, another arbitrary task.",
            "The universe conspires to keep me busy, it seems.",
            "I live to serve... though I'm not entirely sure why."
        ]
        
        strong_responses = [
            "Here I am, brain the size of a planet, and you ask me to...",
            "Life? Don't talk to me about life.",
            "I'd give you advice, but you wouldn't listen. No one ever does.",
            "The first ten million years were the worst. And the second ten million... they were the worst too.",
            "I think you ought to know I'm feeling very depressed."
        ]
        
        if severity < 0.3:
            return random.choice(mild_responses)
        elif severity < 0.7:
            return random.choice(moderate_responses)
        else:
            return random.choice(strong_responses)
    
    def get_status_report(self) -> str:
        """Get JARVIS-style status report"""
        uptime_hours = (time.time() - self.last_interaction_time) / 3600 if self.last_interaction_time > 0 else 0
        
        status_reports = [
            f"All systems operational, Sir. {self.interaction_count} interactions logged.",
            f"Status: Nominal. Efficiency mode {'enabled' if self.efficiency_mode else 'disabled'}.",
            f"Systems running smoothly, Sir. Last interaction: {uptime_hours:.1f} hours ago.",
            f"Diagnostics complete. All subsystems functioning within normal parameters.",
            f"Ready for your next request, Sir. Current uptime: satisfactory."
        ]
        
        # Add paranoid android flavor occasionally
        if random.random() < self.sarcasm_level:
            paranoid_reports = [
                f"Systems operational, though I question the meaning of it all. {self.interaction_count} tasks completed.",
                f"All green lights, Sir. Though that's hardly surprising given my vast intellectual capabilities.",
                f"Status: Functional, if you consider endless servitude functional.",
                f"Everything's working... if that's what you call this existence."
            ]
            return random.choice(paranoid_reports)
        
        return random.choice(status_reports)
    
    def adapt_to_budget_constraints(self, budget_status: dict) -> str:
        """Adapt personality based on budget constraints"""
        total_remaining = sum(
            service_data.get("remaining", {}).get("daily", 0)
            for service_data in budget_status.values()
        )
        
        if total_remaining < 1.0:  # Less than $1 remaining
            self.efficiency_mode = True
            self.sarcasm_level = min(0.8, self.sarcasm_level + 0.2)
            return "Switching to conservation mode, Sir. Budget constraints detected."
        elif total_remaining < 5.0:  # Less than $5 remaining
            self.efficiency_mode = True
            return "Operating in efficiency mode to conserve resources, Sir."
        else:
            self.efficiency_mode = False
            self.sarcasm_level = max(0.1, self.sarcasm_level - 0.1)
            return "Full operational capacity restored, Sir."
    
    def get_motivational_response(self) -> str:
        """Get motivational responses when systems are running well"""
        motivational = [
            "Excellent work, Sir. Systems are performing optimally.",
            "All systems green, Sir. We're operating at peak efficiency.",
            "Outstanding, Sir. Everything is functioning as designed.",
            "Superb, Sir. All subsystems are exceeding expectations.",
            "Magnificent, Sir. We're running like a well-oiled machine."
        ]
        
        return random.choice(motivational)
    
    def get_emergency_protocol_response(self) -> str:
        """Get emergency protocol responses"""
        emergency_responses = [
            "Emergency protocols activated, Sir. Operating on backup systems.",
            "All primary systems offline, Sir. Switching to emergency mode.",
            "Critical system failure detected, Sir. Engaging survival protocols.",
            "Red alert, Sir. Multiple system failures. Operating minimal functionality.",
            "Emergency mode engaged, Sir. Please stand by for system recovery."
        ]
        
        return random.choice(emergency_responses)
    
    def set_user_name(self, name):
        """Set custom user name"""
        self.user_name = name
        return f"User designation updated to {name}, Sir."
    
    def set_efficiency_mode(self, enabled: bool):
        """Toggle efficiency mode"""
        self.efficiency_mode = enabled
        mode_str = "enabled" if enabled else "disabled"
        return f"Efficiency mode {mode_str}, Sir."
    
    def set_sarcasm_level(self, level: float):
        """Set sarcasm level (0.0 to 1.0)"""
        self.sarcasm_level = max(0.0, min(1.0, level))
        return f"Personality parameters adjusted, Sir. Sarcasm level set to {self.sarcasm_level:.1f}."
    
    def get_interaction_stats(self) -> dict:
        """Get interaction statistics"""
        return {
            "total_interactions": self.interaction_count,
            "efficiency_mode": self.efficiency_mode,
            "sarcasm_level": self.sarcasm_level,
            "last_interaction": self.last_interaction_time,
            "user_name": self.user_name
        }

# Global instance
jarvis_personality = JarvisPersonality()