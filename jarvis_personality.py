import datetime
import random

class JarvisPersonality:
    def __init__(self):
        self.user_name = "Sir"  # Default, can be customized
        
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
        """Get response when wake word is detected"""
        now = datetime.datetime.now()
        hour = now.hour
        
        # Different responses based on time
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
    
    def set_user_name(self, name):
        """Set custom user name"""
        self.user_name = name

# Global instance
jarvis_personality = JarvisPersonality()