# AI Assistant - Local LLM with Voice, Web & System Control

A fully local AI assistant powered by llama.cpp, featuring text-to-speech, speech-to-text, web search capabilities, and safe system control—all running on your own hardware with just one LLM model.

## 🌟 Features

- **🤖 Local LLM**: Uses llama.cpp for fast, GPU-accelerated inference with 7B/8B models
- **🎤 Voice Input**: Speech-to-Text using Whisper or Google Speech Recognition
- **🔊 Voice Output**: Text-to-Speech with configurable voices (pyttsx3 or Coqui TTS)
- **💬 Text Chat**: Interactive terminal-based chat interface
- **🌐 Web Search**: DuckDuckGo search integration for real-time information
- **⚙️ System Control**: Safe execution of system commands and file operations
- **🔄 Modular Design**: Clean separation of concerns with easy configuration
- **🔒 Safety First**: Permission-based system access with user confirmation

## 📋 Requirements

- Python 3.9 or higher
- Windows 10/11 (adaptable to Linux/macOS)
- GPU with CUDA support (recommended for best performance)
- 8GB+ RAM (16GB recommended)
- A downloaded llama.cpp compatible model (GGUF format)

## 🚀 Installation

### 1. Clone or Download the Project

```powershell
https://github.com/Surajkr001/assistant_llama.cpp.git
```

### 2. Create a Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

#### Basic Installation (CPU only):
```powershell
pip install -r requirements.txt
```

#### GPU Installation (NVIDIA CUDA):
```powershell
# First install CUDA toolkit from NVIDIA
# Then install llama-cpp-python with CUDA support
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir

# Install other dependencies
pip install requests beautifulsoup4 psutil pyttsx3 SpeechRecognition pyaudio openai-whisper
```

### 4. Download a Language Model

Download a GGUF format model (e.g., Llama 2, Mistral, or similar):

**Recommended models:**
- Llama-2-7B-Chat (Q4_K_M): ~4GB
- Mistral-7B-Instruct (Q4_K_M): ~4GB
- OpenHermes-2.5-Mistral-7B (Q4_K_M): ~4GB

Sources:
- [TheBloke on HuggingFace](https://huggingface.co/TheBloke)
- [llama.cpp models](https://huggingface.co/models?search=gguf)

Place your model in a `models` folder:
```powershell
mkdir models
# Download model to: C:\Users\suraj\OneDrive\Desktop\model\models\your-model.gguf
```

### 5. Configure the Assistant

Edit `config.json` to set your preferences:

```json
{
  "llm": {
    "model_path": "models/llama-2-7b-chat.Q4_K_M.gguf",
    "n_gpu_layers": 35,
    "n_ctx": 4096,
    ...
  },
  ...
}
```

Key settings:
- `model_path`: Path to your GGUF model file
- `n_gpu_layers`: Number of layers to offload to GPU (0 for CPU-only)
- `allowed_directories`: Directories the assistant can access
- `allowed_commands`: Applications the assistant can launch

## 📖 Usage

### Quick Start - Interactive Launcher

```powershell
python run_assistant.py
```

Choose between text chat or voice mode from the menu.

### Text Chat Mode

```powershell
python text_assistant.py
```

**Example interactions:**
```
You: Hello! What can you help me with?
Jarvis: Hello! I'm your AI assistant. I can help you with...

You: Search for Python tutorials
Jarvis: [Performs web search and provides results]

You: What is my CPU usage?
Jarvis: [Shows system information]

You: Open notepad
Jarvis: I've opened notepad for you.
```

**Commands:**
- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/history` - Show conversation log
- `/quit` - Exit the assistant

### Voice Mode

```powershell
python voice_assistant.py
```

Speak naturally to the assistant. It will:
1. Listen for your voice input
2. Transcribe your speech
3. Process your request
4. Speak the response back to you

**Note:** Requires microphone access and STT dependencies installed.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         AssistantCore                    │
│    (Central Orchestrator)                │
└───────────┬─────────────────────────────┘
            │
    ┌───────┴────────┬──────────┬──────────┬──────────┐
    │                │          │          │          │
┌───▼────┐  ┌───────▼───┐  ┌──▼─────┐  ┌─▼────┐  ┌─▼─────┐
│ LLM    │  │  TTS/STT  │  │  Web   │  │System│  │ Chat  │
│ Model  │  │  Engines  │  │ Tools  │  │ Ctrl │  │  UI   │
└────────┘  └───────────┘  └────────┘  └──────┘  └───────┘
```

### Core Modules

1. **llama_model.py**: LLM inference with conversation context
2. **tts_engine.py**: Text-to-speech with multiple voice options
3. **stt_engine.py**: Speech-to-text with noise calibration
4. **web_tools.py**: Web search and content extraction
5. **system_control.py**: Safe system operations with permissions
6. **chat_interface.py**: Terminal-based chat UI
7. **assistant_core.py**: Central orchestrator and intent routing

## ⚙️ Configuration

### LLM Settings

```json
"llm": {
  "model_path": "models/your-model.gguf",
  "n_gpu_layers": 35,        // Layers on GPU (0 for CPU)
  "n_ctx": 4096,             // Context window size
  "temperature": 0.7,        // Creativity (0.0-1.0)
  "max_tokens": 512,         // Max response length
  "top_p": 0.95,
  "repeat_penalty": 1.1
}
```

### TTS Settings

```json
"tts": {
  "engine": "pyttsx3",       // or "coqui"
  "rate": 175,               // Speech speed
  "volume": 0.9,             // Volume (0.0-1.0)
  "voice_id": 0              // Voice index
}
```

### STT Settings

```json
"stt": {
  "engine": "whisper",       // or "google", "sphinx"
  "model": "base",           // Whisper model size
  "language": "en",
  "energy_threshold": 4000,  // Noise threshold
  "pause_threshold": 1.0     // Pause detection
}
```

### System Control

```json
"system": {
  "allowed_directories": [
    "C:\\Users\\suraj\\Documents",
    "C:\\Users\\suraj\\Desktop"
  ],
  "allowed_commands": [
    "notepad",
    "calculator",
    "explorer"
  ],
  "require_confirmation": true  // Ask before system operations
}
```

## 🎯 Use Cases

### Information Retrieval
```
You: Search for the latest news on AI
Assistant: [Performs web search and summarizes results]
```

### System Automation
```
You: Open calculator and show my system specs
Assistant: [Opens calculator and displays system information]
```

### File Operations
```
You: List the files in my Documents folder
Assistant: [Shows directory contents]
```

### General Conversation
```
You: Write a poem about technology
Assistant: [Generates creative content using LLM]
```

## 🔧 Troubleshooting

### Model Loading Issues

**Problem:** Model fails to load
**Solution:** 
- Check model path in `config.json`
- Ensure model is in GGUF format
- Verify you have enough RAM
- Try reducing `n_gpu_layers` if GPU memory is insufficient

### GPU Not Being Used

**Problem:** Running on CPU when GPU is available
**Solution:**
```powershell
# Reinstall with CUDA support
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

### Microphone Not Working

**Problem:** STT not detecting voice
**Solution:**
- Check microphone permissions in Windows
- Run microphone test: `python -c "from stt_engine import *; stt = SpeechToText({'engine': 'google'}); stt.initialize(); stt.test_microphone()"`
- Adjust `energy_threshold` in config

### TTS Voice Issues

**Problem:** TTS voice sounds wrong
**Solution:**
- List available voices: Run individual module test in `tts_engine.py`
- Change `voice_id` in config
- Try different TTS engines (pyttsx3 vs Coqui)

### Web Search Not Working

**Problem:** Search returns no results
**Solution:**
- Check internet connection
- Verify `user_agent` in config
- Try increasing `timeout` value

## 🔐 Security & Privacy

- **Fully Local**: All processing happens on your machine
- **No Data Collection**: No telemetry or data sent to external services
- **Permission-Based**: System operations require explicit confirmation
- **Sandboxed**: File operations limited to configured directories
- **Audit Trail**: All operations logged to `assistant.log`

## 🎨 Customization

### Adding Custom Intents

Edit `assistant_core.py` → `_detect_intent()` method:

```python
def _detect_intent(self, text: str) -> str:
    # Add your custom intent patterns
    if 'your pattern' in text.lower():
        return 'custom_intent'
    ...
```

### Custom System Commands

Add to `config.json`:

```json
"allowed_commands": [
  "notepad",
  "your-custom-app"
]
```

### Changing the Assistant Name

Edit `config.json`:

```json
"assistant": {
  "name": "Your Name Here"
}
```

## 📊 Performance Tips

1. **GPU Acceleration**: Always use GPU if available (set `n_gpu_layers` > 0)
2. **Model Selection**: Q4_K_M quantization offers best speed/quality balance
3. **Context Window**: Larger `n_ctx` = better memory but slower
4. **Temperature**: Lower for factual responses, higher for creativity
5. **Batch Processing**: Process multiple requests in text mode for efficiency

## 🤝 Contributing

Feel free to extend this assistant! Some ideas:

- Add more TTS engines (Azure, Google Cloud)
- Implement RAG for document Q&A
- Add calendar/reminder functionality
- Create a GUI with tkinter or PyQt
- Add multi-language support
- Integrate with smart home devices

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Fast LLM inference
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - Python bindings
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) - Text-to-speech
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `assistant.log`
3. Verify configuration in `config.json`
4. Test individual modules using their `__main__` sections

---

**Enjoy your personal AI assistant! 🚀**

