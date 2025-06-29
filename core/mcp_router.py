import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Callable
import threading
from concurrent.futures import ThreadPoolExecutor
import uuid

class MCPAgent:
    """Represents a remote MCP agent"""
    
    def __init__(self, name: str, endpoint: str, capabilities: List[str], 
                 auth_token: Optional[str] = None, priority: int = 1):
        self.name = name
        self.endpoint = endpoint
        self.capabilities = capabilities
        self.auth_token = auth_token
        self.priority = priority
        self.is_healthy = True
        self.last_health_check = 0
        self.response_times = []
        self.success_rate = 1.0
        self.total_requests = 0
        self.successful_requests = 0
    
    def update_stats(self, success: bool, response_time: float):
        """Update agent performance statistics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        
        self.response_times.append(response_time)
        if len(self.response_times) > 10:  # Keep last 10 response times
            self.response_times.pop(0)
        
        self.success_rate = self.successful_requests / self.total_requests
    
    def get_avg_response_time(self) -> float:
        """Get average response time"""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
    
    def __repr__(self):
        return f"MCPAgent(name={self.name}, healthy={self.is_healthy}, success_rate={self.success_rate:.2f})"


class MCPRouter:
    """
    Routes requests to appropriate MCP agents with load balancing and failover
    """
    
    def __init__(self):
        self.agents = {}  # name -> MCPAgent
        self.capability_map = {}  # capability -> List[agent_names]
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.lock = threading.Lock()
        self.health_check_interval = 30  # seconds
        self.last_health_check = 0
        
        # Default system capabilities
        self.system_capabilities = {
            "time": self._handle_time_request,
            "weather": self._handle_weather_request,
            "calculator": self._handle_calculator_request,
            "system_info": self._handle_system_info_request
        }
        
        # Initialize with some example agents
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize with some default MCP agents"""
        # Example agents - replace with real endpoints
        default_agents = [
            {
                "name": "weather_agent",
                "endpoint": "http://localhost:8001/mcp",
                "capabilities": ["weather", "forecast", "climate"],
                "priority": 1
            },
            {
                "name": "search_agent",
                "endpoint": "http://localhost:8002/mcp",
                "capabilities": ["web_search", "research", "information"],
                "priority": 2
            },
            {
                "name": "code_agent",
                "endpoint": "http://localhost:8003/mcp",
                "capabilities": ["code_analysis", "programming", "debug"],
                "priority": 1
            },
            {
                "name": "data_agent",
                "endpoint": "http://localhost:8004/mcp",
                "capabilities": ["data_analysis", "visualization", "statistics"],
                "priority": 2
            }
        ]
        
        for agent_config in default_agents:
            self.register_agent(**agent_config)
    
    def register_agent(self, name: str, endpoint: str, capabilities: List[str], 
                      auth_token: Optional[str] = None, priority: int = 1):
        """Register a new MCP agent"""
        with self.lock:
            agent = MCPAgent(name, endpoint, capabilities, auth_token, priority)
            self.agents[name] = agent
            
            # Update capability map
            for capability in capabilities:
                if capability not in self.capability_map:
                    self.capability_map[capability] = []
                if name not in self.capability_map[capability]:
                    self.capability_map[capability].append(name)
            
            print(f"📡 Registered MCP agent: {name} with capabilities: {capabilities}")
    
    def unregister_agent(self, name: str):
        """Unregister an MCP agent"""
        with self.lock:
            if name in self.agents:
                agent = self.agents[name]
                
                # Remove from capability map
                for capability in agent.capabilities:
                    if capability in self.capability_map:
                        if name in self.capability_map[capability]:
                            self.capability_map[capability].remove(name)
                        if not self.capability_map[capability]:
                            del self.capability_map[capability]
                
                del self.agents[name]
                print(f"📡 Unregistered MCP agent: {name}")
    
    async def _call_agent(self, agent: MCPAgent, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP agent"""
        try:
            import aiohttp
            
            start_time = time.time()
            
            headers = {}
            if agent.auth_token:
                headers["Authorization"] = f"Bearer {agent.auth_token}"
            headers["Content-Type"] = "application/json"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    agent.endpoint,
                    json=request,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        agent.update_stats(True, response_time)
                        return {
                            "success": True,
                            "data": result,
                            "agent": agent.name,
                            "response_time": response_time
                        }
                    else:
                        agent.update_stats(False, response_time)
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "agent": agent.name
                        }
        
        except Exception as e:
            agent.update_stats(False, time.time() - start_time)
            return {
                "success": False,
                "error": str(e),
                "agent": agent.name
            }
    
    def _get_agents_for_capability(self, capability: str) -> List[MCPAgent]:
        """Get available agents for a capability, sorted by priority and health"""
        with self.lock:
            agent_names = self.capability_map.get(capability, [])
            agents = [self.agents[name] for name in agent_names if name in self.agents]
            
            # Filter healthy agents and sort by priority and success rate
            healthy_agents = [a for a in agents if a.is_healthy]
            healthy_agents.sort(key=lambda x: (x.priority, -x.success_rate, x.get_avg_response_time()))
            
            return healthy_agents
    
    async def _health_check_agent(self, agent: MCPAgent):
        """Perform health check on an agent"""
        try:
            health_request = {
                "id": str(uuid.uuid4()),
                "method": "health_check",
                "params": {}
            }
            
            result = await self._call_agent(agent, health_request)
            agent.is_healthy = result["success"]
            
        except Exception:
            agent.is_healthy = False
    
    async def _perform_health_checks(self):
        """Perform health checks on all agents"""
        if time.time() - self.last_health_check < self.health_check_interval:
            return
        
        print("🔍 Performing MCP agent health checks...")
        
        health_tasks = []
        for agent in self.agents.values():
            health_tasks.append(self._health_check_agent(agent))
        
        if health_tasks:
            await asyncio.gather(*health_tasks, return_exceptions=True)
        
        self.last_health_check = time.time()
        
        # Print health status
        healthy_count = sum(1 for a in self.agents.values() if a.is_healthy)
        total_count = len(self.agents)
        print(f"💚 {healthy_count}/{total_count} MCP agents healthy")
    
    def _handle_time_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle time-related requests locally"""
        from datetime import datetime
        
        format_type = params.get("format", "default")
        
        now = datetime.now()
        
        if format_type == "timestamp":
            result = {"timestamp": now.timestamp()}
        elif format_type == "iso":
            result = {"time": now.isoformat()}
        else:
            result = {
                "time": now.strftime("%I:%M %p"),
                "date": now.strftime("%A, %B %d, %Y"),
                "timezone": str(now.astimezone().tzinfo)
            }
        
        return {"success": True, "data": result}
    
    def _handle_weather_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weather requests - fallback when no agent available"""
        return {
            "success": False,
            "error": "Weather service temporarily unavailable. No MCP weather agents connected."
        }
    
    def _handle_calculator_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle basic calculator requests locally"""
        try:
            expression = params.get("expression", "")
            if not expression:
                return {"success": False, "error": "No expression provided"}
            
            # Simple safe evaluation (be careful with eval!)
            allowed_chars = set("0123456789+-*/.() ")
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return {"success": True, "data": {"result": result, "expression": expression}}
            else:
                return {"success": False, "error": "Invalid expression"}
        
        except Exception as e:
            return {"success": False, "error": f"Calculation error: {str(e)}"}
    
    def _handle_system_info_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system info requests locally"""
        import platform
        import psutil
        
        try:
            info = {
                "system": platform.system(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
            return {"success": True, "data": info}
        except Exception as e:
            return {"success": False, "error": f"System info error: {str(e)}"}
    
    async def route_request(self, capability: str, params: Dict[str, Any], 
                          max_retries: int = 2) -> Dict[str, Any]:
        """
        Route a request to the best available agent for the capability
        """
        request_id = str(uuid.uuid4())
        
        # Check for health status
        await self._perform_health_checks()
        
        # Try system capabilities first
        if capability in self.system_capabilities:
            print(f"🏠 Handling '{capability}' locally")
            return self.system_capabilities[capability](params)
        
        # Get agents for this capability
        agents = self._get_agents_for_capability(capability)
        
        if not agents:
            return {
                "success": False,
                "error": f"No agents available for capability: {capability}",
                "capability": capability
            }
        
        # Try agents in order of preference
        for attempt in range(max_retries + 1):
            for agent in agents:
                print(f"📡 Routing '{capability}' to {agent.name} (attempt {attempt + 1})")
                
                request = {
                    "id": request_id,
                    "method": capability,
                    "params": params
                }
                
                result = await self._call_agent(agent, request)
                
                if result["success"]:
                    return result
                else:
                    print(f"❌ {agent.name} failed: {result.get('error')}")
                    
                    # Mark as unhealthy if multiple failures
                    if agent.success_rate < 0.5:
                        agent.is_healthy = False
        
        return {
            "success": False,
            "error": f"All agents failed for capability: {capability}",
            "capability": capability,
            "attempts": max_retries + 1
        }
    
    def route_request_sync(self, capability: str, params: Dict[str, Any], 
                          max_retries: int = 2) -> Dict[str, Any]:
        """Synchronous wrapper for route_request"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.route_request(capability, params, max_retries))
    
    def get_capabilities(self) -> List[str]:
        """Get all available capabilities"""
        capabilities = set(self.system_capabilities.keys())
        capabilities.update(self.capability_map.keys())
        return sorted(list(capabilities))
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        with self.lock:
            return {
                "total_agents": len(self.agents),
                "healthy_agents": sum(1 for a in self.agents.values() if a.is_healthy),
                "capabilities": self.get_capabilities(),
                "agents": {
                    name: {
                        "healthy": agent.is_healthy,
                        "success_rate": agent.success_rate,
                        "avg_response_time": agent.get_avg_response_time(),
                        "capabilities": agent.capabilities,
                        "total_requests": agent.total_requests
                    }
                    for name, agent in self.agents.items()
                }
            }
    
    def discover_agents(self, discovery_endpoints: List[str]):
        """Discover MCP agents from discovery endpoints"""
        # This would implement agent discovery protocol
        # For now, it's a placeholder
        print(f"🔍 Discovering agents from {len(discovery_endpoints)} endpoints...")
        # Implementation would go here


# Global MCP router instance
mcp_router = MCPRouter()