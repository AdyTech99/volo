import uuid
import os
import atexit
import signal
import subprocess
import time
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import json
import configparser
app = Flask(__name__)
CORS(app)
# Define the path to the config file
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
# Default configuration values
# download location: https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_nopic_2024-06.zim
DEFAULT_CONFIG = {
    'PATHS': {
        'KIWIX_SEARCH_PATH': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kiwix_tools', 'kiwix-tools-macos-arm64-3.7.0-2', 'kiwix-search'),
        'KIWIX_SERVE_PATH': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kiwix_tools', 'kiwix-tools-macos-arm64-3.7.0-2', 'kiwix-serve'),
        'ZIM_FILE_PATH': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Database', 'Wikipedia', 'wikipedia_en_all_nopic_2024-06.zim')
    },
    'SERVER': {
        'PORT': '1255',
        'KIWIX_SERVE_URL': 'http://localhost:821',
        'HEADING_COUNT': '64',
        'AI_MODEL': 'qwen2.5:3b',
        'OLLAMA_API_URL': 'http://localhost:11434/api/chat'
        #'API_KEY': 'support-for-custom-api-providers-is-currently-unavailable'
    }
}
def load_config():
    """Load configuration from file or create it with default values if missing or damaged."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE_PATH):
        print("Config file not found, creating with default values...")
        config.read_dict(DEFAULT_CONFIG)
        with open(CONFIG_FILE_PATH, 'w') as configfile:
            config.write(configfile)
    else:
        try:
            config.read(CONFIG_FILE_PATH)
            # Validate the config file by checking if all required sections and options are present
            for section, options in DEFAULT_CONFIG.items():
                if not config.has_section(section):
                    raise configparser.Error(f"Missing section: {section}")
                for option in options:
                    if not config.has_option(section, option):
                        raise configparser.Error(f"Missing option: {section}.{option}")
        except (configparser.Error, ValueError) as e:
            print(f"Config file is damaged: {e}, regenerating with default values...")
            config.read_dict(DEFAULT_CONFIG)
            with open(CONFIG_FILE_PATH, 'w') as configfile:
                config.write(configfile)
    return config
# Load configuration
config = load_config()
# Assign configuration values to variables
KIWIX_SEARCH_PATH = config['PATHS']['KIWIX_SEARCH_PATH']
KIWIX_SERVE_PATH = config['PATHS']['KIWIX_SERVE_PATH']
ZIM_FILE_PATH = config['PATHS']['ZIM_FILE_PATH']
PORT = int(config['SERVER']['PORT'])
KIWIX_SERVE_URL = config['SERVER']['KIWIX_SERVE_URL']
HEADING_COUNT = int(config['SERVER']['HEADING_COUNT'])
AI_MODEL = config['SERVER']['AI_MODEL']
OLLAMA_API_URL = config['SERVER']['OLLAMA_API_URL']
#API_KEY = config['SERVER']['API_KEY']
API_KEY = 'support-for-custom-api-providers-is-currently-unavailable'
# Global variable to store the kiwix-serve process
kiwix_serve_process = None
# Define headers to be used in API calls
API_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {API_KEY}'  # Ensure API_KEY is defined in your environment or code
}
def start_kiwix_serve():
    """Start the kiwix-serve process."""
    global kiwix_serve_process
    try:
        # Start the kiwix-serve process
        kiwix_serve_process = subprocess.Popen(
            [KIWIX_SERVE_PATH, ZIM_FILE_PATH, "-p", "821"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("kiwix-serve process started successfully.")
    except Exception as e:
        print(f"Failed to start kiwix-serve: {e}")
        raise
def stop_kiwix_serve():
    """Stop the kiwix-serve process."""
    global kiwix_serve_process
    if kiwix_serve_process:
        print("Stopping kiwix-serve process...")
        kiwix_serve_process.terminate()  # Send SIGTERM
        try:
            kiwix_serve_process.wait(timeout=5)  # Wait for the process to terminate
        except subprocess.TimeoutExpired:
            print("kiwix-serve process did not terminate gracefully, killing it...")
            kiwix_serve_process.kill()  # Force kill if it doesn't terminate
        print("kiwix-serve process stopped.")
# Register the stop_kiwix_serve function to run on app exit
atexit.register(stop_kiwix_serve)
# Handle termination signals (e.g., Ctrl+C)
def handle_signal(signum, frame):
    """Handle termination signals."""
    print(f"Received signal {signum}, stopping kiwix-serve...")
    stop_kiwix_serve()
    exit(0)
# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, handle_signal)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_signal)  # Termination signal
# Start kiwix-serve when the app starts
start_kiwix_serve()
# Function to perform a search using kiwix-search
def perform_search(query):
    print(f"Searching for: {query}")
    
    # Execute the kiwix-search command
    try:
        result = subprocess.run(
            [KIWIX_SEARCH_PATH, ZIM_FILE_PATH, query],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error executing kiwix-search: {result.stderr}")
            return None
        # Extract the first n article headings from the output
        output_lines = result.stdout.splitlines()
        if not output_lines:
            print("No search results found.")
            return None
        # Filter out headings that contain the word "disambiguation"
        filtered_headings = [line.strip() for line in output_lines if "disambiguation" not in line.lower()]
        # Get the first 64 headings after filtering
        first_n_headings = filtered_headings[:HEADING_COUNT]
        print(f"First {HEADING_COUNT} headings after filtering: {first_n_headings}")
        return first_n_headings
    except Exception as e:
        print(f"Error during search: {e}")
        return None
# Function to select the best heading using the LLM
def select_best_heading(query, headings):
    print("Selecting the best heading...")
    
    # Construct the headings string with newlines
    headings_str = '\n'.join(headings)
    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            headers=API_HEADERS,
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a research assistant. Your task is to select the most relevant heading from the list provided based on the user's query. Ensure the heading is in the list; avoid outputting headings that are not in the list."},
                    {"role": "user", "content": f"The user's query is: {query}. Here are the headings:\n{headings_str}\n\nPlease select the most relevant heading. Output the heading **only** and nothing else."},
                ],
                "stream": False,
                "options": {
                    "temperature": 0.48,
                    "num_ctx": 2048,
                }
            }
        )
        response.raise_for_status()
        selected_heading = response.json()["message"]["content"].strip()
        print(f"Selected heading: {selected_heading}")
        if selected_heading in headings:
            return selected_heading
        else:
            return None
    except Exception as e:
        print(f"Error selecting best heading: {e}")
        return None
# Function to fetch article content from Kiwix server
def fetch_article_content(heading):
    # Replace spaces with underscores
    formatted_heading = heading.replace(" ", "_")
    
    # Construct the URL
    article_url = f"{KIWIX_SERVE_URL}/wikipedia_en_all_nopic_2024-06/A/{formatted_heading}"
    print(f"Fetching article from: {article_url}")
    try:
        # Fetch the HTML content
        response = requests.get(article_url, headers=API_HEADERS)
        response.raise_for_status()  # Raise an error for bad status codes
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract readable text from the article
        article_text = soup.get_text(separator="\n", strip=True)
        return article_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article content: {e}")
        return None
# Search endpoint
@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query")
    context = data.get("context", [])
    try:
        # Step 1: Use Ollama with tool calling to generate four distinct search queries
        response = requests.post(
            OLLAMA_API_URL,
            headers=API_HEADERS,
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a research assistant. Use the search_engine tool to generate four distinct search queries that will help gather a broad range of information related to the user's query. Each query should focus on a different aspect or angle of the topic."},
                    *context,
                    {"role": "user", "content": query},
                ],
                "tools": [
                    {
                        'type': 'function',
                        'function': {
                            'name': 'search_engine',
                            'description': 'A Wikipedia search engine. Generate four distinct search queries to maximize the spread of search results.',
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'queries': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'string',
                                            'description': 'A distinct search query focusing on a specific aspect of the topic.'
                                        },
                                        'minItems': 4,
                                        'maxItems': 4,
                                        'description': 'Four distinct search queries to maximize the spread of search results.'
                                    },
                                },
                                'required': ['queries']
                            },
                        },
                    },
                ],
                "stream": False,
                "options": {
                    "temperature": 0.48,
                    "num_ctx": 32768,
                }
            }
        )
        response.raise_for_status()
        tool_calls = response.json().get("message", {}).get("tool_calls", [])
        if tool_calls:
            tool_call = tool_calls[0]
            if tool_call["function"]["name"] == "search_engine":
                # Access the arguments directly (it's already a dictionary)
                arguments = tool_call["function"]["arguments"]
                search_queries = arguments.get("queries", [])
                print(f"Generated search queries: {search_queries}")
                # Step 2: Perform searches for each query and aggregate the results
                all_headings = []
                for search_query in search_queries:
                    first_n_headings = perform_search(search_query)
                    if first_n_headings:
                        all_headings.extend(first_n_headings)
                if not all_headings:
                    return jsonify({"message": "No search results found."})
                # Step 3: Select the best heading using the LLM
                best_heading = select_best_heading(query, all_headings)
                if best_heading is None:
                    return "No search results found."
                # Step 4: Fetch the article content for the best heading
                article_content = fetch_article_content(best_heading)
                if article_content is None:
                    return jsonify({"message": "Failed to fetch article content for the selected heading."})
                updated_context = context + [
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": f"Search results: {article_content}"}
                ]
                # Step 5: Generate a detailed response based on the aggregated search results
                def generate_final_response():
                    final_response = requests.post(
                        OLLAMA_API_URL,
                        json={
                            "model": AI_MODEL,
                            "messages": [
                                {"role": "system", "content": '''You are an expert research assistant. Present the search results provided in a natural language response. In addition to summarizing the key points, give an extremely detailed and long analysis that includes extensive detail, nuanced insights, and any potential implications or future outlooks related to each piece of information. As a researcher, ensure that you cite your sources and provide references.
                                \n
                                Additional Instructions: Enclose LaTeX math equations (if any) in $$. Example: $x^2 + y^2 = z^2$ and $( E = mc^2 $)'''},
                                *updated_context,
                                {"role": "user", "content": f"The users query is: {query}"},
                                {"role": "user", "content": f"The search results are: {article_content}"}
                            ],
                            "stream": True,
                            "options": {
                                "temperature": 0.48,
                                "num_ctx": 32768,
                            }
                        },
                        stream=True
                    )
                    for chunk in final_response.iter_lines():
                        if chunk:
                            try:
                                # Parse the chunk as JSON
                                chunk_json = json.loads(chunk)
                                # Extract the content field
                                content = chunk_json.get("message", {}).get("content", "")
                                # Yield the content
                                yield content
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON: {e}")
                                continue
                return Response(stream_with_context(generate_final_response()), content_type='text/plain')
        # If no tool calls, return the response as a string
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred! This is most likely due to a connection issue with Ollama. Ensure that Ollama is running and that the model (default qwen2.5:3b) is available.", 500
# OpenAI-compatible /models endpoint
@app.route("/v1/models", methods=["GET"])
def list_models():
    """Mimic the OpenAI /models endpoint."""
    return jsonify({
        "data": [
            {
                "id": "volo-workflow",
                "object": "model",
                "owned_by": "your-organization",
                "permission": []
            }
        ],
        "object": "list"
    })
# OpenAI-compatible /chat/completions endpoint
@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json
    # Extract the user's messages from the OpenAI-style request
    messages = data.get("messages", [])
    
    # Get the latest user message
    user_messages = [msg for msg in messages if msg["role"] == "user"]
    if not user_messages:
        return jsonify({
            "error": {
                "message": "No user message found in the request.",
                "type": "invalid_request_error",
                "code": 400
            }
        }), 400
    
    latest_user_message = user_messages[-1]["content"]  # Get the latest user message
    context = [msg for msg in messages if msg["role"] != "user"]  # All other messages as context

    # Prepare the request for the existing /search endpoint
    search_request = {
        "query": latest_user_message,
        "context": context  # Pass the context as expected by /search
    }
    # Forward the request to the /search logic
    try:
        # Make an HTTP request to the /search endpoint
        search_response = requests.post(f"http://localhost:{PORT}/search", json=search_request)
        # Check if the search response is valid
        if search_response.status_code != 200:
            return jsonify({
                "error": {
                    "message": "Search request failed.",
                    "type": "api_error",
                    "code": search_response.status_code
                }
            }), search_response.status_code
        # Extract the content from the search response
        content = search_response.text
        response = jsonify({
            "id": f"chatcmpl-{uuid.uuid4()}",  # Generate a unique ID
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "volo-workflow",  # Use the correct model name
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": len(latest_user_message.split()),  # Approximate token count
                "completion_tokens": len(content.split()),  # Approximate token count
                "total_tokens": len(latest_user_message.split()) + len(content.split())
            }
        })
        # Format the response according to OpenAI's API
        return response.get_json()
    except Exception as e:
        # Log the exception for debugging
        print(f"Error in /v1/chat/completions: {e}")
        return jsonify({
            "error": {
                "message": str(e),
                "type": "internal_server_error",
                "code": 500
            }
        }), 500
# Start the server
if __name__ == "__main__":
    try:
        app.run(port=PORT, debug=True)
    finally:
        # Ensure kiwix-serve is stopped when the app exits
        stop_kiwix_serve()