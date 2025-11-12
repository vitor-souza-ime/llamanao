````markdown
# NAO + Ollama Llama Chat

This project integrates the **NAO humanoid robot** with a **local LLaMA-based AI model** (via Ollama CLI), enabling conversational interaction. The robot can listen, process speech, and respond using a local AI model, all in English.

---

## Features

- Connects to NAO robot via its IP address.
- Uses `ALSpeechRecognition` for speech recognition.
- Uses `ALTextToSpeech` for voice output with adjustable volume.
- Integrates with local LLaMA models via **Ollama CLI**.
- Handles basic conversational commands, including greetings, questions, and exit commands.
- Configurable vocabulary for better recognition.
- Timeout handling and basic error recovery.

---

## Requirements

- NAOqi SDK installed.
- Python 3.x.
- `qi` Python library:  
  ```bash
  pip install qi
````

* **Ollama CLI** installed and a LLaMA-based model downloaded:

  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ollama list
  ollama pull llama3
  ```
* NAO robot powered on and connected to the same network.

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/nao-ollama-chat.git
cd nao-ollama-chat
```

2. Install Python dependencies:

```bash
pip install qi
```

3. Make sure Ollama CLI is installed and your preferred model is available:

```bash
ollama list
ollama pull llama3  # or another model
```

---

## Configuration

Edit `main()` in `nao_ollama_chat.py` to set your NAO IP and model name:

```python
NAO_IP = "172.15.3.253"  # Change to your NAO's IP
MODEL_NAME = "llama3"     # Or another Ollama model
```

Optionally, you can adjust the initial TTS volume (range 0.0 - 1.0):

```python
chat = NAOOllamaChat(NAO_IP, model_name=MODEL_NAME, tts_volume=0.5)
```

---

## Usage

Run the chat script:

```bash
python3 nao_ollama_chat.py
```

* The robot will greet you and wait for your input.
* Speak clearly, using common English words or the configured vocabulary.
* To exit, say any of the following: `bye`, `goodbye`, `stop`, `quit`, `exit`, `end`.

---

## Example Interaction

```
NAO: Hello! I'm NAO with Llama AI running locally. I'm ready to chat with you in English. Please speak clearly.
User: Hello robot!
NAO: Hi! How are you today?
User: Tell me a fun fact.
NAO: Did you know that honey never spoils? Archaeologists have found edible honey in ancient Egyptian tombs.
User: Goodbye
NAO: Goodbye! It was wonderful chatting with you. Have a great day!
```

---

## Troubleshooting

* Ensure NAO is powered on and connected to the network.
* Verify IP address is correct.
* Confirm Ollama is installed and the model is available.
* Make sure Python dependencies are installed (`qi`).
* If speech recognition fails, speak louder and clearly.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
