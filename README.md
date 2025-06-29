# 🤖 JARVIS - Advanced AI Assistant

A sophisticated voice assistant inspired by Iron Man's JARVIS with intelligent budget management, multi-tier fallbacks, and voice capabilities.

## ✨ Key Features

- **🧠 Intelligent LLM Orchestration**: Multi-provider support (OpenAI, Claude, Ollama) with automatic fallbacks
- **🔊 Multi-Tier Voice System**: ElevenLabs → Edge TTS → gTTS → pyttsx3 with cost optimization  
- **💰 Smart Budget Management**: Real-time API cost tracking with automatic tier switching
- **🎭 JARVIS Personality**: Iron Man style responses with configurable wit and efficiency modes
- **📡 MCP Integration**: Remote agent connectivity and load balancing

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python3 install_dependencies.py
```

### 2. Set API Keys
```bash
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_claude_key"      # Optional
export ELEVEN_API_KEY="your_elevenlabs_key"    # Optional
```

### 3. Run JARVIS
```bash
# Basic version
python3 app.py

# Advanced version with full features
python3 app_advanced_jarvis.py

# Check system status
python3 app_advanced_jarvis.py --system-status
```

## 🎮 Usage

### Voice Commands
- **"Jarvis"** - Wake word to activate
- **"Jarvis, system status"** - Get diagnostics
- **"Jarvis, budget status"** - Check API costs
- **"Jarvis, efficiency mode on/off"** - Toggle response mode
- **"Jarvis, exit"** - Shutdown

### Budget Management
The system automatically switches between providers based on cost:
- ChatGPT-4 (Premium) → Claude (Mid-tier) → Llama (Free) → Emergency fallback

## 📁 Project Structure

```
jarvis/
├── app.py                    # Basic JARVIS
├── app_advanced_jarvis.py    # Full-featured version
├── core/                     # Core system modules
│   ├── budget_manager.py     # API cost tracking
│   ├── llm_orchestrator.py   # Multi-provider LLM management
│   ├── voice_manager.py      # Voice synthesis tiers
│   └── mcp_router.py         # Remote agent routing
├── llm_providers/            # LLM integrations
├── voice_providers/          # Voice synthesis options
├── speechrecognizers/        # Voice input handlers
└── Agents/                   # Custom AI agents
```

## ⚙️ Configuration

### Budget Limits (core/budget_manager.py)
```python
self.default_limits = {
    "openai": {"daily": 10.00, "weekly": 50.00, "monthly": 100.00},
    "elevenlabs": {"daily": 5.00, "weekly": 25.00, "monthly": 50.00}
}
```

### Personality Settings
```python
jarvis_personality.set_efficiency_mode(True)  # Short responses
jarvis_personality.set_sarcasm_level(0.7)     # Paranoid Android mode
```

## 🛠️ Development

### Using Poetry
```bash
poetry install
poetry shell
python app.py
```

### Adding Custom Agents
Extend the `Agents/` directory with new AI capabilities following the existing patterns.

---

**Created with 🤖 by JARVIS**  
*"I am JARVIS. How may I assist you today, Sir?"*
