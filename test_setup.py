"""
Test Suite - Verify installation and configuration
Run this to check if all components are properly set up
"""

import sys
import json
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_status(status, message):
    """Print status message"""
    symbols = {"pass": "✓", "fail": "✗", "warn": "⚠"}
    colors = {"pass": "\033[92m", "fail": "\033[91m", "warn": "\033[93m"}
    reset = "\033[0m"
    
    symbol = symbols.get(status, "?")
    color = colors.get(status, "")
    print(f"{color}{symbol}{reset} {message}")

def test_python_version():
    """Test Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_status("pass", f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_status("fail", f"Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)")
        return False

def test_dependencies():
    """Test required packages"""
    packages = {
        "llama_cpp": "llama-cpp-python",
        "requests": "requests",
        "bs4": "beautifulsoup4",
        "psutil": "psutil",
        "pyttsx3": "pyttsx3",
        "speech_recognition": "SpeechRecognition"
    }
    
    results = []
    for module, package in packages.items():
        try:
            __import__(module)
            print_status("pass", f"{package} installed")
            results.append(True)
        except ImportError:
            print_status("fail", f"{package} not installed")
            results.append(False)
    
    # Optional packages
    optional = {
        "whisper": "openai-whisper",
        "pyaudio": "pyaudio"
    }
    
    for module, package in optional.items():
        try:
            __import__(module)
            print_status("pass", f"{package} installed (optional)")
        except ImportError:
            print_status("warn", f"{package} not installed (optional)")
    
    return all(results)

def test_configuration():
    """Test config.json"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print_status("fail", "config.json not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_sections = ["llm", "tts", "stt", "web", "system", "assistant"]
        missing = [s for s in required_sections if s not in config]
        
        if missing:
            print_status("fail", f"config.json missing sections: {missing}")
            return False
        
        print_status("pass", "config.json valid")
        return True
        
    except json.JSONDecodeError:
        print_status("fail", "config.json is invalid JSON")
        return False
    except Exception as e:
        print_status("fail", f"config.json error: {e}")
        return False

def test_model_file():
    """Test if model file exists"""
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        model_path = Path(config["llm"]["model_path"])
        
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print_status("pass", f"Model found: {model_path.name} ({size_mb:.1f} MB)")
            return True
        else:
            print_status("warn", f"Model not found: {model_path}")
            print_status("warn", "Download a GGUF model and update config.json")
            return False
            
    except Exception as e:
        print_status("warn", f"Could not check model file: {e}")
        return False

def test_directories():
    """Test directory structure"""
    required_dirs = ["models"]
    results = []
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_status("pass", f"{dir_name}/ directory exists")
            results.append(True)
        else:
            print_status("warn", f"{dir_name}/ directory not found")
            results.append(False)
    
    return all(results)

def test_modules():
    """Test if core modules are importable"""
    modules = [
        "llama_model",
        "tts_engine",
        "stt_engine",
        "web_tools",
        "system_control",
        "chat_interface",
        "assistant_core"
    ]
    
    results = []
    for module in modules:
        try:
            __import__(module)
            print_status("pass", f"{module}.py importable")
            results.append(True)
        except Exception as e:
            print_status("fail", f"{module}.py error: {e}")
            results.append(False)
    
    return all(results)

def test_gpu_support():
    """Test GPU availability"""
    try:
        from llama_cpp import Llama
        # Try to check CUDA support
        print_status("pass", "llama-cpp-python installed")
        
        # Try to detect GPU
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print_status("pass", "NVIDIA GPU detected")
                return True
            else:
                print_status("warn", "No NVIDIA GPU detected (CPU mode)")
                return True
        except:
            print_status("warn", "Could not check GPU status (CPU mode)")
            return True
            
    except ImportError:
        print_status("fail", "llama-cpp-python not installed")
        return False

def main():
    """Run all tests"""
    print_header("AI Assistant - Installation Test")
    
    print("\n[1/7] Testing Python Version...")
    test1 = test_python_version()
    
    print("\n[2/7] Testing Dependencies...")
    test2 = test_dependencies()
    
    print("\n[3/7] Testing Configuration...")
    test3 = test_configuration()
    
    print("\n[4/7] Testing Model File...")
    test4 = test_model_file()
    
    print("\n[5/7] Testing Directories...")
    test5 = test_directories()
    
    print("\n[6/7] Testing Core Modules...")
    test6 = test_modules()
    
    print("\n[7/7] Testing GPU Support...")
    test7 = test_gpu_support()
    
    # Summary
    print_header("Test Summary")
    
    critical_tests = [test1, test2, test3, test6]
    optional_tests = [test4, test5, test7]
    
    if all(critical_tests):
        print("\n✓ All critical tests passed!")
        
        if all(optional_tests):
            print("✓ All optional tests passed!")
            print("\n🎉 Your assistant is ready to use!")
            print("\nRun: python run_assistant.py")
        else:
            print("\n⚠ Some optional tests failed:")
            if not test4:
                print("  • Download a GGUF model file")
            if not test5:
                print("  • Create missing directories")
            if not test7:
                print("  • GPU support not available (CPU mode will work)")
            print("\nYour assistant will work, but consider addressing these issues.")
    else:
        print("\n✗ Some critical tests failed. Please fix the issues above.")
        print("\nRefer to SETUP.md for installation instructions.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
