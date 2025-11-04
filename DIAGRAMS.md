# Architecture & Flow Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐│
│  │  Text Chat UI   │  │  Voice Mode UI  │  │  Interactive ││
│  │ chat_interface  │  │  (STT + TTS)    │  │   Launcher   ││
│  └────────┬────────┘  └────────┬────────┘  └──────┬───────┘│
│           │                    │                   │         │
│           └────────────────────┴───────────────────┘         │
│                              ▼                               │
├─────────────────────────────────────────────────────────────┤
│                   ORCHESTRATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│                  ┌─────────────────────┐                     │
│                  │  AssistantCore      │                     │
│                  │  • Intent Detection │                     │
│                  │  • Request Routing  │                     │
│                  │  • Response Gen     │                     │
│                  └──────────┬──────────┘                     │
│                             │                                │
├─────────────────────────────┼────────────────────────────────┤
│                  SERVICE LAYER                               │
├─────────────────────────────┼────────────────────────────────┤
│                             │                                │
│     ┌───────────┬───────────┼──────────┬──────────┐         │
│     ▼           ▼           ▼          ▼          ▼         │
│ ┌────────┐ ┌────────┐ ┌─────────┐ ┌────────┐ ┌────────┐   │
│ │  LLM   │ │  TTS   │ │   STT   │ │  Web   │ │ System │   │
│ │ Model  │ │ Engine │ │ Engine  │ │ Tools  │ │ Control│   │
│ └────────┘ └────────┘ └─────────┘ └────────┘ └────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow - Text Mode

```
1. User Input
   │
   ├─> ChatInterface.get_user_input()
   │
2. Message Processing
   │
   ├─> AssistantCore.process_message()
   │   │
   │   ├─> _detect_intent()
   │   │   └─> [web_search, system_control, file_op, conversation]
   │   │
   │   ├─> Route to Handler
   │   │   │
   │   │   ├─> _handle_web_search()
   │   │   │   ├─> WebTools.search()
   │   │   │   └─> LlamaModel.generate_response()
   │   │   │
   │   │   ├─> _handle_system_control()
   │   │   │   └─> SystemControl.open_application()
   │   │   │
   │   │   ├─> _handle_file_operation()
   │   │   │   └─> SystemControl.read_file() / list_directory()
   │   │   │
   │   │   └─> _handle_conversation()
   │   │       └─> LlamaModel.generate_response()
   │   │
   │   └─> Return Response
   │
3. Display Output
   │
   └─> ChatInterface.display_message()
```

## Data Flow - Voice Mode

```
1. Voice Input
   │
   ├─> SpeechToText.listen()
   │   ├─> Microphone capture
   │   ├─> Noise calibration
   │   └─> Speech recognition
   │
2. Transcription
   │
   ├─> Text output from STT
   │
3. Processing (same as text mode)
   │
   ├─> AssistantCore.process_message()
   │   └─> [Intent detection & routing]
   │
4. Response Generation
   │
   ├─> LlamaModel.generate_response()
   │
5. Voice Output
   │
   └─> TextToSpeech.speak()
       ├─> Queue management
       ├─> Speech synthesis
       └─> Audio output
```

## Intent Detection Flow

```
User Input
   │
   ├─> Lowercase & Pattern Matching
   │
   ├─> Check Web Search Patterns
   │   ├─> "search for", "look up", "find information"
   │   ├─> "what is", "who is", "where is", "how to"
   │   └─> If match → web_search intent
   │
   ├─> Check System Control Patterns
   │   ├─> "open", "launch", "start", "run"
   │   ├─> "notepad", "calculator", "explorer", etc.
   │   └─> If match → system_control intent
   │
   ├─> Check File Operation Patterns
   │   ├─> "read file", "write file", "list directory"
   │   └─> If match → file_operation intent
   │
   ├─> Check System Info Patterns
   │   ├─> "cpu usage", "memory usage", "disk space"
   │   └─> If match → system_info intent
   │
   └─> Default → conversation intent
```

## Module Interaction Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        run_assistant.py                       │
│                    (Entry Point / Launcher)                   │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                      assistant_core.py                        │
│                                                                │
│  initialize_all() ──┐                                         │
│                     ├──> LlamaModel(config)                   │
│                     ├──> TextToSpeech(config)                 │
│                     ├──> SpeechToText(config)                 │
│                     ├──> WebTools(config)                     │
│                     ├──> SystemControl(config)                │
│                     └──> ChatInterface(config)                │
│                                                                │
│  process_message() ──┐                                        │
│                      ├──> detect_intent()                     │
│                      ├──> route_to_handler()                  │
│                      └──> generate_response()                 │
└──────────────────────────────────────────────────────────────┘
```

## Configuration Flow

```
config.json
   │
   ├─> llm settings ────────> LlamaModel
   │   • model_path
   │   • n_gpu_layers
   │   • temperature
   │   • max_tokens
   │
   ├─> tts settings ────────> TextToSpeech
   │   • engine
   │   • rate
   │   • volume
   │   • voice_id
   │
   ├─> stt settings ────────> SpeechToText
   │   • engine
   │   • model
   │   • thresholds
   │
   ├─> web settings ────────> WebTools
   │   • search_engine
   │   • max_results
   │   • timeout
   │
   ├─> system settings ─────> SystemControl
   │   • allowed_directories
   │   • allowed_commands
   │   • require_confirmation
   │
   └─> assistant settings ──> ChatInterface
       • name
       • mode
       • log_conversations
```

## Security & Safety Layers

```
User Request
   │
   ├─> Intent Detection
   │
   ├─> Is it a System Operation?
   │   │
   │   ├─> YES
   │   │   │
   │   │   ├─> Check Allowed Commands
   │   │   │   └─> Not in list? → REJECT
   │   │   │
   │   │   ├─> Check Allowed Directories
   │   │   │   └─> Outside scope? → REJECT
   │   │   │
   │   │   ├─> Require Confirmation?
   │   │   │   ├─> YES → Prompt User
   │   │   │   │   └─> User declines? → REJECT
   │   │   │   └─> NO → Continue
   │   │   │
   │   │   └─> Execute with Logging
   │   │
   │   └─> NO → Process Normally
   │
   └─> Log to assistant.log
```

## Threading Model

```
Main Thread
   │
   ├─> AssistantCore
   │   └─> Process messages
   │
   ├─> LlamaModel
   │   └─> Synchronous inference
   │
   ├─> ChatInterface
   │   └─> Input/Output
   │
Background Threads
   │
   ├─> TTS Speech Worker Thread
   │   ├─> Queue management
   │   ├─> Speech synthesis
   │   └─> Audio output
   │
   └─> STT Background Listening (optional)
       ├─> Continuous audio capture
       ├─> Speech detection
       └─> Callback execution
```

## File System Layout

```
model/
│
├─── Entry Points
│    ├── run_assistant.py      [Interactive launcher]
│    ├── text_assistant.py     [Text mode direct]
│    └── voice_assistant.py    [Voice mode direct]
│
├─── Core Logic
│    ├── assistant_core.py     [Orchestrator]
│    ├── llama_model.py        [LLM]
│    ├── chat_interface.py     [UI]
│    ├── tts_engine.py         [Text-to-Speech]
│    ├── stt_engine.py         [Speech-to-Text]
│    ├── web_tools.py          [Web scraping]
│    └── system_control.py     [System ops]
│
├─── Configuration
│    └── config.json           [Settings]
│
├─── Utilities
│    ├── model_manager.py      [Model selection]
│    ├── test_setup.py         [Verification]
│    └── setup.ps1             [Auto setup]
│
├─── Documentation
│    ├── README.md             [Main docs]
│    ├── SETUP.md              [Installation]
│    ├── QUICKREF.md           [Quick ref]
│    ├── PROJECT_STRUCTURE.md [Architecture]
│    ├── COMPLETION.md         [Summary]
│    └── DIAGRAMS.md           [This file]
│
├─── Dependencies
│    └── requirements.txt      [Pip packages]
│
├─── Runtime (created at runtime)
│    ├── models/               [GGUF models]
│    ├── venv/                 [Virtual env]
│    └── assistant.log         [Logs]
│
└─── Version Control
     └── .gitignore            [Git rules]
```

## Execution Flow - Complete Session

```
1. START
   │
2. Load Configuration
   ├─> Read config.json
   └─> Parse settings
   │
3. Initialize Modules
   ├─> Load LLM model (with GPU)
   ├─> Initialize TTS engine
   ├─> Initialize STT engine
   ├─> Setup web tools
   ├─> Setup system control
   └─> Create chat interface
   │
4. Choose Mode
   ├─> Text Mode
   │   └─> Start chat loop
   │       ├─> Get user input
   │       ├─> Process message
   │       ├─> Generate response
   │       ├─> Display response
   │       └─> Loop until /quit
   │
   └─> Voice Mode
       └─> Start voice loop
           ├─> Listen for speech
           ├─> Transcribe to text
           ├─> Process message
           ├─> Generate response
           ├─> Speak response
           └─> Loop until Ctrl+C
   │
5. Shutdown
   ├─> Unload LLM model
   ├─> Stop TTS engine
   ├─> Stop STT engine
   ├─> Close web session
   ├─> Save conversation log
   └─> Exit
   │
6. END
```

## Performance Optimization Points

```
┌─────────────────────────────────────────┐
│         Performance Bottlenecks         │
├─────────────────────────────────────────┤
│                                         │
│  1. LLM Inference (Slowest)             │
│     ├─> Use GPU acceleration            │
│     ├─> Optimize n_gpu_layers           │
│     ├─> Use quantized models (Q4_K_M)   │
│     └─> Reduce context window if needed │
│                                         │
│  2. Model Loading (One-time cost)       │
│     └─> Keep model loaded in memory     │
│                                         │
│  3. STT Processing                      │
│     ├─> Use Whisper base model          │
│     └─> Optimize energy thresholds      │
│                                         │
│  4. Web Search                          │
│     ├─> Cache results when possible     │
│     └─> Set reasonable timeouts         │
│                                         │
│  5. TTS Generation                      │
│     └─> Use background thread (done)    │
│                                         │
└─────────────────────────────────────────┘
```

## Extension Points

```
To Add New Features:

1. New Intent Type
   ├─> Edit assistant_core.py
   ├─> Add pattern in _detect_intent()
   ├─> Add handler method _handle_new_intent()
   └─> Integrate with existing modules

2. New TTS Engine
   ├─> Edit tts_engine.py
   ├─> Add initialization in _initialize_new_engine()
   └─> Update speak() method

3. New STT Engine
   ├─> Edit stt_engine.py
   ├─> Add recognition in _recognize_speech()
   └─> Update configuration

4. New Tool/Service
   ├─> Create new_tool.py
   ├─> Add initialization in AssistantCore
   └─> Add handler methods as needed

5. GUI Interface
   ├─> Create gui_interface.py
   ├─> Replace ChatInterface
   └─> Keep same message callback pattern
```

---

**These diagrams provide visual understanding of:**
- System architecture and layers
- Data flow through the application
- Module interactions and dependencies
- Security and safety mechanisms
- Threading model
- Performance considerations
- Extension opportunities

**Use these diagrams when:**
- Understanding the system design
- Planning modifications
- Debugging issues
- Extending functionality
- Onboarding new developers
