"""
Model Manager - Helper script for managing LLM models
"""

import json
from pathlib import Path
import sys

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def list_models():
    """List available models in the models directory"""
    models_dir = Path("models")
    
    if not models_dir.exists():
        print("\nNo models directory found. Creating it...")
        models_dir.mkdir()
        print("✓ Created models/ directory")
        return []
    
    model_files = list(models_dir.glob("*.gguf"))
    
    if not model_files:
        print("\nNo GGUF models found in models/ directory")
        return []
    
    print("\nAvailable models:")
    for i, model_path in enumerate(model_files, 1):
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"  {i}. {model_path.name}")
        print(f"     Size: {size_mb:.1f} MB")
    
    return model_files

def get_current_model():
    """Get currently configured model"""
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        current_path = config["llm"]["model_path"]
        return current_path
    except:
        return None

def set_model(model_path):
    """Update config.json with new model path"""
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        config["llm"]["model_path"] = str(model_path)
        
        with open("config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"\nError updating config: {e}")
        return False

def recommend_settings(model_size_mb):
    """Recommend settings based on model size"""
    print("\nRecommended settings for your model:")
    
    if model_size_mb < 2000:
        # Small model (< 2GB)
        print("  n_gpu_layers: 35+ (can fit entirely in GPU)")
        print("  n_ctx: 4096 (full context)")
    elif model_size_mb < 4000:
        # Medium model (2-4GB)
        print("  n_gpu_layers: 30-35 (mostly on GPU)")
        print("  n_ctx: 4096 (full context)")
    elif model_size_mb < 6000:
        # Large model (4-6GB)
        print("  n_gpu_layers: 20-30 (partial GPU)")
        print("  n_ctx: 2048-4096 (adjust based on GPU memory)")
    else:
        # Very large model (> 6GB)
        print("  n_gpu_layers: 10-20 (limited GPU)")
        print("  n_ctx: 2048 (reduced context)")
    
    print("\nNote: Adjust based on your GPU memory:")
    print("  • 4GB GPU: n_gpu_layers = 20-25")
    print("  • 6GB GPU: n_gpu_layers = 30-35")
    print("  • 8GB+ GPU: n_gpu_layers = 35+")

def main():
    print_header("Model Manager")
    
    # Show current model
    current = get_current_model()
    if current:
        current_path = Path(current)
        if current_path.exists():
            size_mb = current_path.stat().st_size / (1024 * 1024)
            print(f"\nCurrently configured model:")
            print(f"  {current_path.name} ({size_mb:.1f} MB)")
        else:
            print(f"\nCurrently configured model (NOT FOUND):")
            print(f"  {current}")
    else:
        print("\nNo model configured yet")
    
    # List available models
    print_header("Available Models")
    models = list_models()
    
    if not models:
        print("\nTo get started:")
        print("  1. Download a GGUF model from https://huggingface.co/TheBloke")
        print("  2. Place it in the models/ directory")
        print("  3. Run this script again to configure it")
        return
    
    # Prompt to select model
    print("\nOptions:")
    print("  1-N: Select a model to use")
    print("  Q: Quit without changes")
    
    choice = input("\nYour choice: ").strip().upper()
    
    if choice == 'Q':
        print("\nNo changes made.")
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(models):
            selected_model = models[index]
            
            print(f"\nSelected: {selected_model.name}")
            
            # Get relative path
            relative_path = selected_model.relative_to(Path.cwd())
            
            # Update config
            if set_model(str(relative_path)):
                print("✓ Configuration updated!")
                
                # Show recommendations
                size_mb = selected_model.stat().st_size / (1024 * 1024)
                recommend_settings(size_mb)
                
                print("\nYou can now run the assistant:")
                print("  python run_assistant.py")
            else:
                print("✗ Failed to update configuration")
        else:
            print("\nInvalid selection")
    except ValueError:
        print("\nInvalid input")

if __name__ == "__main__":
    main()
