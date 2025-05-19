import requests

class DeepSeekChatbot:
    def __init__(self, ollama_url="http://localhost:11434", model_name="deepseek-r1:14b"):
        self.ollama_url = ollama_url
        self.model_name = model_name
        print(f"Using DeepSeek model '{self.model_name}' via Ollama at {self.ollama_url}")

    def generate_response(self, question):
        payload = {
            "model": self.model_name,
            "prompt": question,
            "stream": True  # Enable streaming
        }
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, stream=True)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = line.decode("utf-8")
                    import json
                    chunk = json.loads(data)
                    full_response += chunk.get("response", "")
            # Remove <think> and </think> tags if present
            full_response = full_response.replace("<think>", "").replace("</think>", "").strip()
            return full_response
        except Exception as e:
            return f"Error communicating with Ollama: {e}"

    def stream_response(self, question):
        payload = {
            "model": self.model_name,
            "prompt": question,
            "stream": True
        }
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = line.decode("utf-8")
                    import json
                    chunk = json.loads(data)
                    text = chunk.get("response", "")
                    text = text.replace("<think>", "").replace("</think>", "")
                    yield text
        except Exception as e:
            yield f"Error communicating with Ollama: {e}"