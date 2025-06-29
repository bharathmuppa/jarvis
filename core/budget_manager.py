import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import threading

class BudgetManager:
    """
    Manages API budgets and usage tracking for multiple services
    Supports daily, weekly, monthly limits with automatic resets
    """
    
    def __init__(self, budget_file: str = "budget_data.json"):
        self.budget_file = budget_file
        self.lock = threading.Lock()
        
        # Default budget limits (€50 total monthly budget)
        self.default_limits = {
            "openai": {
                "daily": 1.00,    # €1 per day
                "weekly": 6.00,   # €6 per week  
                "monthly": 25.00  # €25 per month
            },
            "claude": {
                "daily": 0.75,    # €0.75 per day
                "weekly": 4.50,   # €4.50 per week
                "monthly": 15.00  # €15 per month
            },
            "elevenlabs": {
                "daily": 0.50,    # €0.50 per day
                "weekly": 3.00,   # €3 per week
                "monthly": 10.00  # €10 per month
            }
        }
        
        self.budget_data = self._load_budget_data()
        
        # Cost per token/character (updated with latest models)
        self.costs = {
            "openai": {
                "gpt-4.1": {"input": 0.015/1000, "output": 0.060/1000},
                "gpt-4o": {"input": 0.005/1000, "output": 0.015/1000},
                "gpt-4o-mini": {"input": 0.0015/1000, "output": 0.006/1000},
                "gpt-4-turbo": {"input": 0.01/1000, "output": 0.03/1000},
                "gpt-4": {"input": 0.03/1000, "output": 0.06/1000},
                "gpt-3.5-turbo": {"input": 0.0015/1000, "output": 0.002/1000}
            },
            "claude": {
                "claude-3-sonnet": {"input": 0.003/1000, "output": 0.015/1000},
                "claude-3-haiku": {"input": 0.00025/1000, "output": 0.00125/1000}
            },
            "elevenlabs": {
                "standard": 0.18/1000,  # per character
                "premium": 0.30/1000
            }
        }
    
    def _load_budget_data(self) -> Dict:
        """Load budget data from file or create default"""
        if os.path.exists(self.budget_file):
            try:
                with open(self.budget_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "usage": {},
            "limits": self.default_limits.copy(),
            "last_reset": {
                "daily": datetime.now().strftime("%Y-%m-%d"),
                "weekly": datetime.now().strftime("%Y-W%U"),
                "monthly": datetime.now().strftime("%Y-%m")
            }
        }
    
    def _save_budget_data(self):
        """Save budget data to file"""
        with open(self.budget_file, 'w') as f:
            json.dump(self.budget_data, f, indent=2)
    
    def _check_and_reset_periods(self):
        """Check if we need to reset daily/weekly/monthly counters"""
        now = datetime.now()
        
        # Daily reset
        current_day = now.strftime("%Y-%m-%d")
        if self.budget_data["last_reset"]["daily"] != current_day:
            for service in self.budget_data["usage"]:
                if "daily" in self.budget_data["usage"][service]:
                    self.budget_data["usage"][service]["daily"] = 0
            self.budget_data["last_reset"]["daily"] = current_day
        
        # Weekly reset (Monday)
        current_week = now.strftime("%Y-W%U")
        if self.budget_data["last_reset"]["weekly"] != current_week:
            for service in self.budget_data["usage"]:
                if "weekly" in self.budget_data["usage"][service]:
                    self.budget_data["usage"][service]["weekly"] = 0
            self.budget_data["last_reset"]["weekly"] = current_week
        
        # Monthly reset
        current_month = now.strftime("%Y-%m")
        if self.budget_data["last_reset"]["monthly"] != current_month:
            for service in self.budget_data["usage"]:
                if "monthly" in self.budget_data["usage"][service]:
                    self.budget_data["usage"][service]["monthly"] = 0
            self.budget_data["last_reset"]["monthly"] = current_month
    
    def calculate_cost(self, service: str, model: str, input_tokens: int = 0, 
                      output_tokens: int = 0, characters: int = 0) -> float:
        """Calculate cost for API usage"""
        if service not in self.costs:
            return 0.0
        
        cost = 0.0
        
        if service in ["openai", "claude"]:
            if model in self.costs[service]:
                cost += input_tokens * self.costs[service][model]["input"]
                cost += output_tokens * self.costs[service][model]["output"]
        elif service == "elevenlabs":
            if model in self.costs[service]:
                cost += characters * self.costs[service][model]
        
        return round(cost, 6)
    
    def can_afford(self, service: str, estimated_cost: float) -> Tuple[bool, str]:
        """Check if we can afford the estimated cost"""
        with self.lock:
            self._check_and_reset_periods()
            
            if service not in self.budget_data["usage"]:
                self.budget_data["usage"][service] = {"daily": 0, "weekly": 0, "monthly": 0}
            
            usage = self.budget_data["usage"][service]
            limits = self.budget_data["limits"].get(service, self.default_limits.get(service, {}))
            
            # Check each period
            for period in ["daily", "weekly", "monthly"]:
                if period in limits:
                    current_usage = usage.get(period, 0)
                    if current_usage + estimated_cost > limits[period]:
                        return False, f"{service} {period} budget exceeded ({current_usage:.4f} + {estimated_cost:.4f} > {limits[period]:.2f})"
            
            return True, "OK"
    
    def record_usage(self, service: str, actual_cost: float, model: str = None):
        """Record actual API usage"""
        with self.lock:
            self._check_and_reset_periods()
            
            if service not in self.budget_data["usage"]:
                self.budget_data["usage"][service] = {"daily": 0, "weekly": 0, "monthly": 0}
            
            # Add to all periods
            for period in ["daily", "weekly", "monthly"]:
                self.budget_data["usage"][service][period] += actual_cost
            
            # Save updated data
            self._save_budget_data()
            
            print(f"💰 {service} cost: ${actual_cost:.6f} (Model: {model or 'unknown'})")
    
    def get_budget_status(self) -> Dict:
        """Get current budget status for all services"""
        with self.lock:
            self._check_and_reset_periods()
            
            status = {}
            for service in self.budget_data["limits"]:
                usage = self.budget_data["usage"].get(service, {"daily": 0, "weekly": 0, "monthly": 0})
                limits = self.budget_data["limits"][service]
                
                status[service] = {
                    "usage": usage,
                    "limits": limits,
                    "remaining": {
                        period: max(0, limits.get(period, 0) - usage.get(period, 0))
                        for period in ["daily", "weekly", "monthly"]
                        if period in limits
                    }
                }
            
            return status
    
    def set_budget_limit(self, service: str, period: str, amount: float):
        """Set budget limit for a service and period"""
        with self.lock:
            if service not in self.budget_data["limits"]:
                self.budget_data["limits"][service] = {}
            
            self.budget_data["limits"][service][period] = amount
            self._save_budget_data()
            
            print(f"🏦 Set {service} {period} budget to ${amount:.2f}")
    
    def get_cheapest_available_service(self, service_preferences: list) -> Optional[str]:
        """Get the cheapest available service from preferences"""
        for service in service_preferences:
            can_afford, reason = self.can_afford(service, 0.01)  # Small test amount
            if can_afford:
                return service
        
        return None
    
    def print_budget_summary(self):
        """Print a nice budget summary"""
        status = self.get_budget_status()
        
        print("\n" + "💰" + "="*50 + "💰")
        print("                BUDGET SUMMARY")
        print("💰" + "="*50 + "💰")
        
        for service, data in status.items():
            print(f"\n🔹 {service.upper()}:")
            for period in ["daily", "weekly", "monthly"]:
                if period in data["limits"]:
                    used = data["usage"][period]
                    limit = data["limits"][period]
                    remaining = data["remaining"][period]
                    percentage = (used / limit * 100) if limit > 0 else 0
                    
                    status_icon = "🟢" if percentage < 70 else "🟡" if percentage < 90 else "🔴"
                    
                    print(f"  {status_icon} {period.title()}: ${used:.4f} / ${limit:.2f} (${remaining:.4f} remaining)")
        
        print("\n" + "💰" + "="*50 + "💰\n")


# Global budget manager instance
budget_manager = BudgetManager()