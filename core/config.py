"""
Cross-platform configuration management for Advanced JARVIS
Handles environment variables, API keys, and system-specific settings
"""

import os
import sys
import platform
from typing import Dict, Optional, Any
from pathlib import Path
import json

class Config:
    """
    Cross-platform configuration manager
    Handles environment variables, API keys, and system settings
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.home_dir = Path.home()
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "jarvis_config.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Environment variable mappings
        self.env_vars = {
            # OpenAI
            "OPENAI_API_KEY": {
                "description": "OpenAI API key for ChatGPT models",
                "required": False,
                "service": "openai"
            },
            
            # Anthropic/Claude
            "ANTHROPIC_API_KEY": {
                "description": "Anthropic API key for Claude models",
                "required": False,
                "service": "claude"
            },
            
            # ElevenLabs
            "ELEVEN_API_KEY": {
                "description": "ElevenLabs API key for premium voice synthesis",
                "required": False,
                "service": "elevenlabs"
            },
            "ELEVENLABS_API_KEY": {
                "description": "Alternative ElevenLabs API key name",
                "required": False,
                "service": "elevenlabs"
            },
            
            # Ollama/Local LLM
            "OLLAMA_HOST": {
                "description": "Ollama server host (default: localhost:11434)",
                "required": False,
                "default": "localhost:11434",
                "service": "ollama"
            },
            
            # Azure OpenAI (alternative)
            "AZURE_OPENAI_API_KEY": {
                "description": "Azure OpenAI API key",
                "required": False,
                "service": "azure_openai"
            },
            "AZURE_OPENAI_ENDPOINT": {
                "description": "Azure OpenAI endpoint URL",
                "required": False,
                "service": "azure_openai"
            },
            
            # Google/Gemini (future)
            "GOOGLE_API_KEY": {
                "description": "Google AI API key for Gemini models",
                "required": False,
                "service": "google"
            },
            
            # Hugging Face (future)
            "HUGGINGFACE_API_KEY": {
                "description": "Hugging Face API key for models",
                "required": False,
                "service": "huggingface"
            },
            
            # System settings
            "JARVIS_LOG_LEVEL": {
                "description": "Logging level (DEBUG, INFO, WARNING, ERROR)",
                "required": False,
                "default": "INFO",
                "service": "system"
            },
            "JARVIS_CONFIG_DIR": {
                "description": "Custom configuration directory path",
                "required": False,
                "service": "system"
            }
        }
    
    def _get_config_directory(self) -> Path:
        """Get platform-specific configuration directory"""
        if self.platform == "windows":
            # Windows: %APPDATA%\JARVIS
            appdata = os.getenv("APPDATA")
            if appdata:
                return Path(appdata) / "JARVIS"
            else:
                return self.home_dir / "AppData" / "Roaming" / "JARVIS"
        
        elif self.platform == "darwin":
            # macOS: ~/Library/Application Support/JARVIS
            return self.home_dir / "Library" / "Application Support" / "JARVIS"
        
        else:
            # Linux/Unix: ~/.config/jarvis
            xdg_config = os.getenv("XDG_CONFIG_HOME")
            if xdg_config:
                return Path(xdg_config) / "jarvis"
            else:
                return self.home_dir / ".config" / "jarvis"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default configuration
        return {
            "version": "1.0.0",
            "platform": self.platform,
            "budget_limits": {
                "openai": {"daily": 5.00, "weekly": 20.00, "monthly": 50.00},
                "claude": {"daily": 3.00, "weekly": 15.00, "monthly": 30.00},
                "elevenlabs": {"daily": 2.00, "weekly": 10.00, "monthly": 20.00}
            },
            "voice_preferences": {
                "preferred_tier": "auto",
                "fallback_enabled": True
            },
            "llm_preferences": {
                "preferred_provider": "auto",
                "context_limit": 4000,
                "temperature": 0.7
            },
            "personality": {
                "efficiency_mode": True,
                "sarcasm_level": 0.3,
                "user_name": "Sir"
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config: {e}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service, checking multiple possible environment variables"""
        
        # Service-specific environment variable mappings
        service_env_vars = {
            "openai": ["OPENAI_API_KEY", "OPENAI_KEY"],
            "claude": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "ANTHROPIC_KEY"],
            "elevenlabs": ["ELEVEN_API_KEY", "ELEVENLABS_API_KEY", "ELEVEN_LABS_API_KEY"],
            "azure_openai": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_KEY"],
            "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_AI_KEY"],
            "huggingface": ["HUGGINGFACE_API_KEY", "HF_API_KEY", "HUGGING_FACE_KEY"]
        }
        
        env_vars_to_check = service_env_vars.get(service, [])
        
        # Check each possible environment variable
        for env_var in env_vars_to_check:
            value = os.getenv(env_var)
            if value and value.strip():
                return value.strip()
        
        return None
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key: str, value: Any):
        """Set a configuration setting"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def get_env_var(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with fallback to default"""
        value = os.getenv(name, default)
        
        # If no value and we have a default in config
        if not value and name in self.env_vars:
            default_value = self.env_vars[name].get("default")
            if default_value:
                return default_value
        
        return value
    
    def check_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Check status of all API keys"""
        status = {}
        
        services = ["openai", "claude", "elevenlabs", "azure_openai", "google", "huggingface"]
        
        for service in services:
            api_key = self.get_api_key(service)
            status[service] = {
                "available": bool(api_key),
                "key_preview": f"{api_key[:8]}...{api_key[-4:]}" if api_key else None,
                "length": len(api_key) if api_key else 0
            }
        
        return status
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform-specific information"""
        return {
            "platform": self.platform,
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "home_directory": str(self.home_dir),
            "config_directory": str(self.config_dir),
            "config_file": str(self.config_file)
        }
    
    def setup_environment_guide(self) -> str:
        """Generate platform-specific environment setup guide"""
        
        if self.platform == "windows":
            guide = """
# Windows Environment Setup

## Method 1: System Environment Variables (Recommended)
1. Press Win + X, select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Add your API keys:
   - Variable name: OPENAI_API_KEY
   - Variable value: your_openai_api_key_here

## Method 2: PowerShell (Temporary)
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
$env:ANTHROPIC_API_KEY="your_claude_api_key_here"
$env:ELEVEN_API_KEY="your_elevenlabs_api_key_here"
```

## Method 3: Command Prompt (Temporary)
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
set ANTHROPIC_API_KEY=your_claude_api_key_here
set ELEVEN_API_KEY=your_elevenlabs_api_key_here
```
"""
        
        elif self.platform == "darwin":
            guide = """
# macOS Environment Setup

## Method 1: ~/.zshrc or ~/.bash_profile (Recommended)
```bash
echo 'export OPENAI_API_KEY="your_openai_api_key_here"' >> ~/.zshrc
echo 'export ANTHROPIC_API_KEY="your_claude_api_key_here"' >> ~/.zshrc
echo 'export ELEVEN_API_KEY="your_elevenlabs_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

## Method 2: Temporary (Current Session)
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export ANTHROPIC_API_KEY="your_claude_api_key_here"
export ELEVEN_API_KEY="your_elevenlabs_api_key_here"
```

## Method 3: .env file in project directory
Create a file named `.env` in the project directory:
```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
ELEVEN_API_KEY=your_elevenlabs_api_key_here
```
"""
        
        else:  # Linux
            guide = """
# Linux Environment Setup

## Method 1: ~/.bashrc or ~/.profile (Recommended)
```bash
echo 'export OPENAI_API_KEY="your_openai_api_key_here"' >> ~/.bashrc
echo 'export ANTHROPIC_API_KEY="your_claude_api_key_here"' >> ~/.bashrc
echo 'export ELEVEN_API_KEY="your_elevenlabs_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## Method 2: Temporary (Current Session)
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export ANTHROPIC_API_KEY="your_claude_api_key_here"
export ELEVEN_API_KEY="your_elevenlabs_api_key_here"
```

## Method 3: .env file in project directory
Create a file named `.env` in the project directory:
```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
ELEVEN_API_KEY=your_elevenlabs_api_key_here
```

## Method 4: systemd user environment (Advanced)
```bash
systemctl --user edit --force --full jarvis-env.service
```
"""
        
        return guide.strip()
    
    def load_dotenv_file(self, file_path: Optional[str] = None):
        """Load environment variables from .env file"""
        if not file_path:
            file_path = Path(".env")
        else:
            file_path = Path(file_path)
        
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
            return True
        except IOError:
            return False

# Global configuration instance
config = Config()