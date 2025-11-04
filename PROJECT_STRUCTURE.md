# Project Structure

```
model/
│
├── config.json                 # Main configuration file
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
├── SETUP.md                    # Quick setup guide
├── .gitignore                  # Git ignore rules
│
├── Core Modules:
├── llama_model.py             # LLM inference engine
├── tts_engine.py              # Text-to-Speech
├── stt_engine.py              # Speech-to-Text
├── web_tools.py               # Web search & scraping
├── system_control.py          # System operations
├── chat_interface.py          # Terminal chat UI
├── assistant_core.py          # Central orchestrator
│
├── Entry Points:
├── run_assistant.py           # Interactive launcher (recommended)
├── text_assistant.py          # Text chat mode
├── voice_assistant.py         # Voice interaction mode
│
└── models/                    # Place your GGUF models here
    └── (download model files here)
```

## File Descriptions

### Configuration
- **config.json**: All settings for LLM, TTS, STT, web, and system control

### Core Modules
- **llama_model.py**: Handles LLM loading, inference, and conversation history
- **tts_engine.py**: Converts text responses to speech output
- **stt_engine.py**: Converts speech input to text
- **web_tools.py**: Web search and content extraction
- **system_control.py**: Safe system command execution with permissions
- **chat_interface.py**: Terminal-based chat interface
- **assistant_core.py**: Orchestrates all modules and routes requests

### Entry Points
- **run_assistant.py**: Main launcher with mode selection
- **text_assistant.py**: Direct text chat mode
- **voice_assistant.py**: Direct voice mode

### Documentation
- **README.md**: Comprehensive project documentation
- **SETUP.md**: Quick start installation guide
- **requirements.txt**: Python package dependencies
- **.gitignore**: Files to exclude from version control

## Module Dependencies

```
assistant_core.py
    ├── llama_model.py (LLM)
    ├── tts_engine.py (TTS)
    ├── stt_engine.py (STT)
    ├── web_tools.py (Web)
    ├── system_control.py (System)
    └── chat_interface.py (UI)

run_assistant.py → assistant_core.py
text_assistant.py → assistant_core.py
voice_assistant.py → assistant_core.py
```

## Key Features by Module

### LlamaModel (llama_model.py)
- GPU-accelerated inference
- Conversation history management
- Configurable parameters (temperature, tokens, etc.)
- Context window management

### TextToSpeech (tts_engine.py)
- Multiple TTS engines (pyttsx3, Coqui)
- Non-blocking speech with queue
- Voice selection and configuration
- Rate and volume control

### SpeechToText (stt_engine.py)
- Multiple STT engines (Whisper, Google, Sphinx)
- Ambient noise calibration
- Background listening support
- Microphone selection

### WebTools (web_tools.py)
- DuckDuckGo search integration
- Web page content extraction
- Search result summarization
- URL accessibility checks

### SystemControl (system_control.py)
- Safe application launching
- File read/write operations
- Directory listing
- System information retrieval
- Process management
- Permission-based access control

### ChatInterface (chat_interface.py)
- Interactive terminal UI
- Command system (/help, /clear, etc.)
- Conversation logging
- History management

### AssistantCore (assistant_core.py)
- Intent detection and routing
- Module orchestration
- Request processing
- Mode switching (text/voice)
- Unified interface

## Data Flow

### Text Mode
```
User Input → ChatInterface → AssistantCore → Intent Detection
    ↓
[Web Search | System Control | File Ops | Conversation]
    ↓
LlamaModel → Generate Response → ChatInterface → Display
```

### Voice Mode
```
Microphone → STT → Text → AssistantCore → Intent Detection
    ↓
[Web Search | System Control | File Ops | Conversation]
    ↓
LlamaModel → Generate Response → TTS → Speaker
```

## Configuration Overview

### config.json Structure
```json
{
  "llm": { ... },          // Model path, GPU settings, inference params
  "tts": { ... },          // TTS engine, voice, rate, volume
  "stt": { ... },          // STT engine, model, thresholds
  "web": { ... },          // Search settings, timeout
  "system": { ... },       // Allowed dirs, commands, permissions
  "assistant": { ... }     // Name, mode, logging
}
```

## Usage Patterns

### Basic Usage
1. Run `python run_assistant.py`
2. Select mode (text or voice)
3. Interact naturally
4. Use commands like /help, /quit

### Advanced Usage
- Customize intents in `assistant_core.py`
- Add custom system commands in `config.json`
- Extend modules with new capabilities
- Integrate with external APIs

## Extension Points

### Adding New Intents
Edit `assistant_core.py::_detect_intent()` and add handler method

### Adding New System Commands
Update `config.json` allowed_commands list

### Custom TTS Engine
Implement in `tts_engine.py` following existing pattern

### Custom STT Engine
Implement in `stt_engine.py` following existing pattern

### Additional Web Sources
Extend `web_tools.py` with new search methods

## Testing

Each module includes a `__main__` section for standalone testing:

```powershell
python llama_model.py    # Test LLM loading and inference
python tts_engine.py     # Test text-to-speech
python stt_engine.py     # Test speech-to-text
python web_tools.py      # Test web search
python system_control.py # Test system operations
python chat_interface.py # Test chat UI
```

## Logs

- `assistant.log`: Main application log
- Console output: Real-time interaction

## Security Considerations

- File operations limited to `allowed_directories`
- System commands limited to `allowed_commands`
- User confirmation for sensitive operations
- No external data transmission (fully local)
- Audit trail in logs

---

**Next Steps:** See SETUP.md for installation instructions!
