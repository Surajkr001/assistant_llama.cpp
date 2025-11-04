# Quick Setup Guide

Follow these steps to get your AI assistant up and running quickly.

## Step 1: Install Python Dependencies

```powershell
# Navigate to project directory
cd C:\Users\suraj\OneDrive\Desktop\model

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Install llama-cpp-python with GPU Support (Optional but Recommended)

If you have an NVIDIA GPU:

```powershell
# Set environment variable for CUDA support
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"

# Install llama-cpp-python with CUDA
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

## Step 3: Download a Language Model

1. Visit [TheBloke's HuggingFace](https://huggingface.co/TheBloke)
2. Search for a model (recommended: Llama-2-7B-Chat or Mistral-7B-Instruct)
3. Download the GGUF file (Q4_K_M quantization recommended)
4. Create a `models` folder and place the model there:

```powershell
mkdir models
# Move downloaded .gguf file to: .\models\
```

## Step 4: Configure the Assistant

Edit `config.json` and update the model path:

```json
{
  "llm": {
    "model_path": "models/llama-2-7b-chat.Q4_K_M.gguf",
    ...
  }
}
```

## Step 5: Run the Assistant

### Option A: Interactive Mode (Recommended)
```powershell
python run_assistant.py
```

### Option B: Text Chat Only
```powershell
python text_assistant.py
```

### Option C: Voice Mode
```powershell
python voice_assistant.py
```

## Common Issues

### Issue: "Import llama_cpp could not be resolved"

**Solution:** This is just a linting warning. Install the package:
```powershell
pip install llama-cpp-python
```

### Issue: "Model file not found"

**Solution:** Verify the path in `config.json` matches your model location:
```powershell
# Check if model exists
Test-Path .\models\your-model-name.gguf
```

### Issue: "Microphone not working"

**Solution:** 
1. Install pyaudio: `pip install pyaudio`
2. Grant microphone permissions in Windows Settings
3. Test with: `python -m speech_recognition`

### Issue: "Out of memory"

**Solution:** Reduce GPU layers in `config.json`:
```json
"n_gpu_layers": 20  // Lower value = less GPU memory used
```

## Testing Individual Modules

Each module can be tested independently:

```powershell
# Test LLM
python llama_model.py

# Test TTS
python tts_engine.py

# Test STT
python stt_engine.py

# Test Web Search
python web_tools.py

# Test System Control
python system_control.py

# Test Chat Interface
python chat_interface.py
```

## Next Steps

Once everything is working:

1. Customize `config.json` to your preferences
2. Add your favorite applications to `allowed_commands`
3. Configure allowed directories for file operations
4. Try different models to find your favorite
5. Adjust temperature and other LLM parameters for better responses

## Getting Help

- Check `assistant.log` for detailed error messages
- Review the main README.md for comprehensive documentation
- Test components individually to isolate issues

Happy assisting! 🎉
