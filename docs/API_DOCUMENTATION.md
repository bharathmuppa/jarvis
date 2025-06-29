# 📚 Advanced JARVIS API Documentation

## Overview

Advanced JARVIS is built with a modular, extensible architecture that allows for easy integration of new LLM providers, voice synthesis services, and other components.

## Core Architecture

```
Advanced JARVIS/
├── core/                   # Core system components
│   ├── config.py          # Cross-platform configuration management
│   ├── budget_manager.py  # API cost tracking and limits
│   ├── llm_orchestrator.py # LLM provider management (DEPRECATED - use new system)
│   ├── voice_manager.py   # Voice provider management (DEPRECATED - use new system)
│   └── mcp_router.py      # MCP agent coordination
├── llm_providers/         # Extensible LLM provider system
│   ├── base_provider.py   # Abstract base class for LLM providers
│   ├── openai_provider.py # OpenAI GPT models
│   ├── claude_provider.py # Anthropic Claude models
│   ├── ollama_provider.py # Local Ollama/Llama models
│   └── emergency_provider.py # Hardcoded fallback responses
├── voice_providers/       # Extensible voice synthesis system
│   ├── base_voice_provider.py # Abstract base class for voice providers
│   ├── elevenlabs_provider.py # ElevenLabs premium TTS
│   ├── edge_tts_provider.py   # Microsoft Edge TTS (free)
│   ├── gtts_provider.py       # Google TTS (free)
│   ├── pyttsx3_provider.py    # System TTS (offline)
│   └── text_only_provider.py  # Text-only fallback
└── speechrecognizers/     # Voice input processing
    ├── WakeWordRecognizer.py # Wake word detection
    └── FastRecognizers.py    # Optimized speech recognition
```

## Core Components

### Configuration Management (`core/config.py`)

The configuration system provides cross-platform environment management and API key handling.

#### Key Features:
- **Cross-platform compatibility**: Windows, macOS, Linux
- **Environment variable management**: Automatic detection from multiple sources
- **Configuration persistence**: JSON-based config storage
- **API key validation**: Multi-source key detection

#### Usage:

```python
from core.config import config

# Get API keys
openai_key = config.get_api_key("openai")
claude_key = config.get_api_key("claude")

# Get configuration settings
budget_limits = config.get_setting("budget_limits.openai")
efficiency_mode = config.get_setting("personality.efficiency_mode", True)

# Set configuration values
config.set_setting("voice_preferences.preferred_tier", "elevenlabs")

# Check API key status
key_status = config.check_api_keys()
```

#### Environment Variables:

| Variable | Service | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | OpenAI | GPT models API key |
| `ANTHROPIC_API_KEY` | Claude | Claude models API key |
| `ELEVEN_API_KEY` | ElevenLabs | Premium voice synthesis |
| `OLLAMA_HOST` | Ollama | Local LLM server (default: localhost:11434) |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI | Azure OpenAI service |
| `GOOGLE_API_KEY` | Google AI | Gemini models (future) |

### Budget Management (`core/budget_manager.py`)

Tracks API usage costs and enforces budget limits across all services.

#### Key Features:
- **Multi-service tracking**: OpenAI, Claude, ElevenLabs, etc.
- **Time-based limits**: Daily, weekly, monthly budgets
- **Automatic resets**: Time-based budget renewals
- **Cost estimation**: Pre-request cost calculation
- **Usage analytics**: Detailed spending reports

#### Usage:

```python
from core.budget_manager import budget_manager

# Check if request is affordable
can_afford, reason = budget_manager.can_afford("openai", 0.05)

# Record actual usage
budget_manager.record_usage("openai", 0.023, "gpt-3.5-turbo")

# Get budget status
status = budget_manager.get_budget_status()

# Set custom limits
budget_manager.set_budget_limit("elevenlabs", "daily", 5.00)
```

## LLM Provider System

### Base Provider Interface (`llm_providers/base_provider.py`)

All LLM providers inherit from `BaseLLMProvider` and implement the standard interface.

#### Abstract Methods:
- `_initialize()`: Setup provider (API keys, connections)
- `_get_response()`: Generate response from LLM
- `get_available_models()`: List supported models
- `estimate_cost()`: Calculate request cost

#### Standard Response Format:

```python
@dataclass
class LLMResponse:
    success: bool              # Whether request succeeded
    content: str              # Generated text response
    model_used: str           # Model that generated response
    provider_name: str        # Provider name
    input_tokens: int         # Input token count
    output_tokens: int        # Output token count
    cost: float              # Actual cost in USD
    response_time: float     # Generation time in seconds
    error_message: str       # Error details if failed
    metadata: Dict[str, Any] # Provider-specific data
```

### OpenAI Provider (`llm_providers/openai_provider.py`)

Supports GPT-3.5-turbo, GPT-4, and GPT-4-turbo models.

#### Features:
- **Model support**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **Streaming support**: Real-time response generation
- **Function calling**: Tool/function integration
- **Organization support**: Multi-org API key handling

#### Usage:

```python
from llm_providers import OpenAIProvider

provider = OpenAIProvider()

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]

response = provider.generate_response(messages, model="gpt-3.5-turbo")
print(response.content)
```

### Claude Provider (`llm_providers/claude_provider.py`)

Supports Claude-3 model family from Anthropic.

#### Features:
- **Model support**: Claude-3-haiku, Claude-3-sonnet, Claude-3-opus
- **Large context**: 200K token context window
- **Model aliases**: Simplified names (claude-3-sonnet vs claude-3-sonnet-20240229)
- **Streaming support**: Real-time generation

#### Usage:

```python
from llm_providers import ClaudeProvider

provider = ClaudeProvider()

response = provider.generate_response(
    messages,
    model="claude-3-haiku",  # or full name: claude-3-haiku-20240307
    max_tokens=1000
)
```

### Ollama Provider (`llm_providers/ollama_provider.py`)

Supports local Llama and other models running on Ollama.

#### Features:
- **Local execution**: No API costs, complete privacy
- **Model management**: Pull, delete, list models
- **Multiple models**: Llama2, CodeLlama, Mistral, Phi, Gemma
- **Auto-discovery**: Dynamic model detection

#### Usage:

```python
from llm_providers import OllamaProvider

provider = OllamaProvider()

# Check available models
models = provider.get_available_models()

# Pull a new model
success, message = provider.pull_model("llama2:13b")

# Generate response
response = provider.generate_response(messages, model="llama2")
```

### Emergency Provider (`llm_providers/emergency_provider.py`)

Provides hardcoded responses when all other providers fail.

#### Features:
- **Always available**: Never fails
- **Intent detection**: Basic pattern matching
- **Template responses**: Customizable response templates
- **Zero cost**: Completely free fallback

#### Usage:

```python
from llm_providers import EmergencyProvider

provider = EmergencyProvider()

# Add custom response template
provider.add_response_template("weather", "I cannot check weather in emergency mode, Sir.")

# Add intent keywords
provider.add_intent_keywords("custom_intent", ["keyword1", "keyword2"])
```

## Voice Provider System

### Base Voice Provider Interface (`voice_providers/base_voice_provider.py`)

All voice providers inherit from `BaseVoiceProvider` and implement speech synthesis.

#### Abstract Methods:
- `_initialize()`: Setup provider (dependencies, API keys)
- `_synthesize_speech()`: Convert text to speech
- `get_available_voices()`: List supported voices
- `estimate_cost()`: Calculate synthesis cost

#### Standard Response Format:

```python
@dataclass
class VoiceResponse:
    success: bool              # Whether synthesis succeeded
    provider_name: str         # Provider name
    voice_used: str           # Voice that was used
    text_length: int          # Length of input text
    cost: float              # Synthesis cost in USD
    synthesis_time: float    # Time to generate audio
    playback_time: float     # Time to play audio
    error_message: str       # Error details if failed
    metadata: Dict[str, Any] # Provider-specific data
```

### ElevenLabs Provider (`voice_providers/elevenlabs_provider.py`)

Premium voice synthesis with natural-sounding voices.

#### Features:
- **Premium quality**: Human-like voice synthesis
- **Multiple voices**: Rachel, Domi, Bella, Antoni, etc.
- **SSML support**: Advanced speech markup
- **Streaming**: Real-time audio generation
- **Voice cloning**: Custom voice creation (premium feature)

#### Usage:

```python
from voice_providers import ElevenLabsProvider

provider = ElevenLabsProvider()

# Speak with default voice
response = provider.speak("Hello, this is JARVIS speaking.")

# Use specific voice
response = provider.speak("How may I assist you?", voice="Rachel")

# Get voice information
voice_info = provider.get_voice_info("Rachel")
```

### Edge TTS Provider (`voice_providers/edge_tts_provider.py`)

High-quality free voice synthesis using Microsoft Edge TTS.

#### Features:
- **Free service**: No API costs
- **High quality**: Neural voice models
- **Multiple languages**: English variants and international
- **SSML support**: Speech markup language
- **No rate limits**: Unlimited usage

#### Usage:

```python
from voice_providers import EdgeTTSProvider

provider = EdgeTTSProvider()

# Speak with custom parameters
response = provider.speak(
    "Good morning, Sir",
    voice="Aria",
    rate="+20%",
    pitch="+0Hz"
)
```

### gTTS Provider (`voice_providers/gtts_provider.py`)

Basic free voice synthesis using Google Text-to-Speech.

#### Features:
- **Free service**: No API costs
- **Multi-language**: Extensive language support
- **Simple interface**: Easy to use
- **Reliable**: Google's proven TTS service

#### Usage:

```python
from voice_providers import GTTSProvider

provider = GTTSProvider()

# Speak in different languages
response = provider.speak("Hello", voice="English (US)")
response = provider.speak("Hola", voice="Spanish")

# Get supported languages
languages = provider.get_supported_languages()
```

### PyTTSx3 Provider (`voice_providers/pyttsx3_provider.py`)

Offline voice synthesis using system TTS engines.

#### Features:
- **Offline operation**: No internet required
- **System integration**: Uses OS-native TTS
- **Cross-platform**: Windows (SAPI), macOS (NSSpeechSynthesizer), Linux (espeak)
- **Zero cost**: Completely free
- **Customizable**: Rate, volume, voice selection

#### Usage:

```python
from voice_providers import PyTTSx3Provider

provider = PyTTSx3Provider()

# Speak with custom settings
response = provider.speak(
    "System status nominal",
    rate=180,
    volume=0.8
)

# Get system voices
voices = provider.get_available_voices()
```

### Text-Only Provider (`voice_providers/text_only_provider.py`)

Fallback provider that prints formatted text instead of speech.

#### Features:
- **Always available**: Never fails
- **Multiple styles**: Different text formatting options
- **Customizable**: Add custom output styles
- **Silent mode**: Process without output

#### Usage:

```python
from voice_providers import TextOnlyProvider

provider = TextOnlyProvider()

# Different output styles
provider.speak("Hello", voice="speech")     # 🗣️ JARVIS: Hello
provider.speak("Alert", voice="emphasis")   # ‼️ Alert
provider.speak("Info", voice="robot")       # 🤖 Info

# Add custom style
provider.add_style("custom", ">>> {}")
```

## Creating Custom Providers

### Custom LLM Provider

```python
from llm_providers.base_provider import BaseLLMProvider, LLMResponse

class CustomLLMProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__(name="custom_llm", cost_tier="medium")
    
    def _initialize(self) -> bool:
        # Setup your provider
        return True
    
    def _get_response(self, messages, model, **kwargs) -> LLMResponse:
        # Implement your LLM integration
        return LLMResponse(
            success=True,
            content="Generated response",
            model_used=model,
            provider_name=self.name
        )
    
    def get_available_models(self):
        return ["custom-model-1", "custom-model-2"]
    
    def estimate_cost(self, input_tokens, output_tokens, model):
        return 0.001 * (input_tokens + output_tokens)
```

### Custom Voice Provider

```python
from voice_providers.base_voice_provider import BaseVoiceProvider, VoiceResponse

class CustomVoiceProvider(BaseVoiceProvider):
    def __init__(self):
        super().__init__(name="custom_tts", quality_tier="high", cost_tier="low")
    
    def _initialize(self) -> bool:
        # Setup your voice provider
        return True
    
    def _synthesize_speech(self, text, voice=None, **kwargs) -> VoiceResponse:
        # Implement your TTS integration
        return VoiceResponse(
            success=True,
            provider_name=self.name,
            voice_used=voice,
            text_length=len(text)
        )
    
    def get_available_voices(self):
        return ["voice1", "voice2"]
    
    def estimate_cost(self, text, voice=None):
        return len(text) * 0.0001
```

## Integration Examples

### Using Multiple Providers

```python
from llm_providers import OpenAIProvider, ClaudeProvider, OllamaProvider
from voice_providers import ElevenLabsProvider, EdgeTTSProvider

# Initialize providers
llm_providers = [
    OpenAIProvider(),
    ClaudeProvider(), 
    OllamaProvider()
]

voice_providers = [
    ElevenLabsProvider(),
    EdgeTTSProvider()
]

# Use first available LLM
for provider in llm_providers:
    if provider.is_available:
        response = provider.generate_response(messages)
        break

# Use first available voice
for provider in voice_providers:
    if provider.is_available:
        provider.speak(response.content)
        break
```

### Budget-Aware Usage

```python
from core.budget_manager import budget_manager

def smart_llm_request(messages, providers):
    for provider in providers:
        if not provider.is_available:
            continue
        
        # Estimate cost
        estimated_cost = provider.estimate_cost(100, 50, provider.default_model)
        
        # Check budget
        can_afford, reason = budget_manager.can_afford(
            provider.name, 
            estimated_cost
        )
        
        if can_afford:
            response = provider.generate_response(messages)
            if response.success:
                budget_manager.record_usage(
                    provider.name, 
                    response.cost, 
                    response.model_used
                )
                return response
    
    return None  # No affordable providers
```

## Error Handling

### Provider Failures

```python
def robust_generation(text, providers):
    for provider in providers:
        try:
            response = provider.generate_response([{"role": "user", "content": text}])
            if response.success:
                return response
            else:
                print(f"{provider.name} failed: {response.error_message}")
        except Exception as e:
            print(f"{provider.name} error: {e}")
            continue
    
    return None  # All providers failed
```

### Voice Synthesis Fallbacks

```python
def speak_with_fallback(text, providers):
    for provider in providers:
        try:
            response = provider.speak(text)
            if response.success:
                return True
        except Exception as e:
            print(f"Voice provider {provider.name} failed: {e}")
            continue
    
    # Final fallback - print text
    print(f"📝 {text}")
    return False
```

## Best Practices

### 1. Provider Initialization
- Always check `provider.is_available` before use
- Handle initialization failures gracefully
- Use multiple providers for redundancy

### 2. Cost Management
- Estimate costs before making requests
- Set appropriate budget limits
- Monitor usage regularly

### 3. Error Handling
- Implement fallback chains
- Log errors for debugging
- Provide user feedback on failures

### 4. Performance
- Cache provider instances
- Use async operations where possible
- Monitor response times

### 5. Security
- Store API keys securely
- Use environment variables
- Never commit keys to version control

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Check environment variables
   - Verify key format
   - Test with provider's official tools

2. **Provider Not Available**
   - Check internet connectivity
   - Verify dependencies installed
   - Check provider service status

3. **Budget Exceeded**
   - Check budget limits
   - Review usage patterns
   - Adjust limits or switch providers

4. **Voice Synthesis Fails**
   - Check audio system
   - Verify text length limits
   - Test with simpler text

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed provider interactions and error details.