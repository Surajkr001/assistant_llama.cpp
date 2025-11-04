# AI Assistant - Quick Reference Card

## 🚀 Quick Start

```powershell
# Setup (first time only)
.\setup.ps1

# Download a model and place in models/ folder
# Update config.json with model path

# Run assistant
python run_assistant.py
```

## 📝 Available Commands

### Chat Commands (in text mode)
| Command    | Description                     |
|------------|---------------------------------|
| `/help`    | Show available commands         |
| `/clear`   | Clear conversation history      |
| `/history` | Show conversation log           |
| `/quit`    | Exit the assistant              |

### System Operations
| Task                    | Example                                      |
|-------------------------|----------------------------------------------|
| Open application        | "Open notepad"                               |
| Search the web          | "Search for Python tutorials"                |
| Get system info         | "What is my CPU usage?"                      |
| Read a file             | "Read the file at C:\Users\...\file.txt"    |
| List directory          | "List files in my Documents folder"          |
| General conversation    | "Tell me a joke"                             |

## ⚙️ Configuration Quick Reference

### config.json Key Settings

```json
{
  "llm": {
    "model_path": "models/your-model.gguf",  // ⚠️ Update this!
    "n_gpu_layers": 35,                       // GPU layers (0 = CPU only)
    "temperature": 0.7                        // 0.0-1.0 (lower = factual)
  },
  "system": {
    "allowed_commands": ["notepad", "..."],   // Apps to allow
    "require_confirmation": true              // Ask before actions
  }
}
```

## 🎯 Common Tasks

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Install with GPU Support
```powershell
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

### Test Setup
```powershell
python test_setup.py
```

### Run Different Modes
```powershell
python run_assistant.py     # Interactive mode selector
python text_assistant.py    # Direct text chat
python voice_assistant.py   # Direct voice mode
```

### Test Individual Components
```powershell
python llama_model.py       # Test LLM
python tts_engine.py        # Test text-to-speech
python stt_engine.py        # Test speech-to-text
python web_tools.py         # Test web search
```

## 🐛 Troubleshooting Quick Fixes

### Model Won't Load
```json
// In config.json, reduce GPU layers:
"n_gpu_layers": 0  // Try CPU mode first
```

### Out of Memory
```json
// In config.json:
"n_ctx": 2048,           // Reduce context window
"n_gpu_layers": 20       // Reduce GPU layers
```

### Import Errors
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Microphone Not Working
```powershell
# Test microphone
python -m speech_recognition

# Grant permissions in Windows Settings > Privacy > Microphone
```

## 📊 Performance Tips

| Setting           | Value     | Effect                    |
|-------------------|-----------|---------------------------|
| `n_gpu_layers`    | 0         | CPU only (slowest)        |
| `n_gpu_layers`    | 20-30     | Partial GPU (balanced)    |
| `n_gpu_layers`    | 35+       | Full GPU (fastest)        |
| `temperature`     | 0.1-0.3   | Factual responses         |
| `temperature`     | 0.7-0.9   | Creative responses        |
| `n_ctx`           | 2048      | Less memory, faster       |
| `n_ctx`           | 4096      | More context, slower      |

## 🔍 Log Files

- **assistant.log**: Main application log with debug info
- Check logs when troubleshooting issues

## 🔗 Useful Links

- **Models**: https://huggingface.co/TheBloke
- **llama.cpp**: https://github.com/ggerganov/llama.cpp
- **Documentation**: See README.md for full details

## 💡 Example Interactions

**Web Search:**
```
You: Search for the latest AI news
Assistant: [Searches web and summarizes results]
```

**System Control:**
```
You: Open calculator and tell me my system specs
Assistant: [Opens calculator and displays system info]
```

**File Operations:**
```
You: List the files in my Desktop folder
Assistant: [Shows directory contents]
```

**Conversation:**
```
You: Explain quantum computing in simple terms
Assistant: [Generates detailed explanation]
```

## 📞 Getting Help

1. Run `python test_setup.py` to diagnose issues
2. Check `assistant.log` for error details
3. Review SETUP.md for installation steps
4. See README.md for comprehensive documentation

---

**Remember:** 
- Download a GGUF model first!
- Update `model_path` in config.json
- Adjust settings based on your hardware

**Enjoy your AI assistant! 🎉**
