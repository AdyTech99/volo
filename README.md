# Volo: Empower Your AI with Wikipedia Knowledge 🚀

Volo is an innovative solution designed to enhance AI capabilities with Wikipedia knowledge through an efficient **RAG (Retrieval Augmented Generation)** pipeline. It utilizes an offline database of Wikipedia powered by **Kiwix**, ensuring fast and reliable access to information without requiring constant internet connectivity.

Volo uses a tiny model (Qwen2.5:3b) and gives it the knowledge of nearly 7 million Wikipedia articles, making it a _more_ reliable source of information than giant closed-source models like OpenAI's GPT4o and Anthropic's Claude 3.5 Sonnet

By integrating with **Ollama** and supporting **OpenAI-compatible REST APIs**, Volo provides a flexible and user-friendly interface for knowledge-driven AI interactions. Whether you're building intelligent chatbots, conducting research, or just exploring Wikipedia in new ways, Volo makes it seamless and efficient.

---

## ✨ Features
- **Offline Wikipedia Database**: Leverages a `.zim` file from Kiwix, offering a snapshot of Wikipedia for offline access.
- **RAG Workflow**: Combines retrieval of factual data from Wikipedia with advanced AI generative capabilities.
- **Integration with Ollama**: Supports Ollama models like `qwen2.5:3b` for superior natural language processing.
- **Configurable Settings**: Fully customizable via `config.ini`.
- **OpenAI-Compatible REST APIs**: Use Volo with interfaces like Open WebUI or your own API client.
- **Cross-Platform Support**: Compatible with Windows, macOS, and Linux.

---

## Minimum System Requirements
- 3 GB VRAM (most discrete GPUs should be enough)
- 60 GB of disk space
- A fast GPU

## 📦 Prerequisites
Before installing Volo, ensure you have the following installed:
1. **Python 3.10 or later**  
   - Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - Make sure `pip` is installed and available in your PATH.
2. **Kiwix Offline Database**  
   - Download the `.zim` file for Wikipedia (~55 GB):  
     [wikipedia_en_all_nopic_2024-06.zim](https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_nopic_2024-06.zim)
3. **Ollama**  
   - Follow the [Ollama installation guide](https://github.com/ollama/ollama#ollama) to set up the environment.
   - Pull the required model:  
     ```bash
     ollama pull qwen2.5:3b
     ```
   - Start the Ollama server:  
     ```bash
     ollama serve
     ```

---

## 🔧 Installation
Follow these steps to set up and run Volo:

### Step 1: Clone the Repository
Clone the Volo repository from GitHub:
```bash
git clone https://github.com/AdyTech99/volo.git
cd volo
```

### Step 2: Install Python Dependencies
Install the required Python packages using pip:
```pip install -r requirements.txt```

### Step 3: Start the server:
On macOS/Linux, run the commands:
```
cd Volo
./start.sh
```
On Windows, navigate to the cloned repository and double click start.bat

### Step 4: Configure Volo
**Set Up config.ini:** Open the newly-generated config.ini file and specify the path to the .zim file downloaded from Kiwix:

```
[Volo]
zim_file_path = /path/to/wikipedia_en_all_nopic_2024-06.zim
```

**[Optional]: Modify other settings such as RAG options or model name.**

### Step 5: Start Volo (again)

On macOS/Linux, run the commands:
```
cd Volo
./start.sh
```
On Windows, navigate to the cloned repository and double click start.bat

---

## 🚀 Usage

### OpenAI-Compatible API Endpoints

> [!WARNING]
Streaming must be set to __false__ in any custom interface used (like Open WebUI)

Volo provides REST API endpoints compatible with OpenAI:

1.	**/v1/models**: List available models.
2.	**/v1/chat/completions**: Generate AI chat completions.

You can use these endpoints with any OpenAI-compatible client, such as Open WebUI, or your own custom integrations. 
Volo provides a "volo-workflow" model that requests can be made to. When using an interface such as Open WebUI, select the "volo-workflow" model from the dropdown.
The request will be sent through Volo's pipeline, and a result will be produced in the OpenAI format.

### Example API Call

Using curl to make a chat completion request:
```
curl -X POST http://localhost:1255/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "volo-workflow",
  "messages": [{"role": "user", "content": "What is the capital of France?"}]
}'
```


## 🛠️ Configuration Options

Customize Volo by editing the config.ini file:

```
[PATHS]
kiwix_search_path = path/to/volo/kiwix_tools/kiwix-tools-macos-arm64-3.7.0-2/kiwix-search
kiwix_serve_path = path/to/volo/kiwix_tools/kiwix-tools-macos-arm64-3.7.0-2/kiwix-serve
zim_file_path = /Volumes/T7/Documents/wikipedia_en_all_nopic_2024-06.zim

[SERVER]
port = 1255
kiwix_serve_url = http://localhost:821
heading_count = 64
ai_model = qwen2.5:3b
ollama_api_url = http://localhost:11434/api/chat
```



## 🤝 Contributing

Contributions are welcome! If you’d like to improve Volo, please:
	1.	Fork the repository.
	2.	Create a feature branch.
	3.	Submit a pull request with a detailed description.

## 📄 License

This project is licensed under the GPLv3 License. See the LICENSE file for details.

## 💡 Acknowledgments

Volo is powered by:
	•	Kiwix for offline Wikipedia access.
	•	Ollama for cutting-edge AI models.

## 🌟 Get Started Today!

Unleash the power of Wikipedia knowledge in your AI projects with Volo. Clone the repository, set it up, and begin exploring the endless possibilities!
