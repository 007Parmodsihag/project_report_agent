# agent/ollama_client.py
import requests
import json
import config # Import the configuration file
import os
# from os import path
# from sys import Path

class OllamaClient:
    """
    A client to interact with a local Ollama API endpoint for text generation.
    """
    def __init__(self, model_name: str = None, api_url: str = None):
        """
        Initializes the Ollama client.

        Args:
            model_name (str, optional): The specific Ollama model to use (e.g., 'mistral', 'llama3').
                                        Defaults to config.DEFAULT_OLLAMA_MODEL.
            api_url (str, optional): The URL for the Ollama generate API.
                                     Defaults to config.OLLAMA_API_URL.
        """
        self.model_name = model_name or config.DEFAULT_OLLAMA_MODEL
        self.api_url = api_url or config.OLLAMA_API_URL
        print(f"    OllamaClient initialized:")
        print(f"      API URL: {self.api_url}")
        print(f"      Model:   {self.model_name}")
        self._check_connection()

    def _check_connection(self):
        """Checks if the Ollama API endpoint is reachable."""
        print("      Checking Ollama connection...")
        try:
            # A simple GET request to the base Ollama URL often works for a basic health check
            # Adjust if your Ollama setup requires a different check
            base_url = self.api_url.replace("/api/generate", "")
            response = requests.get(base_url, timeout=5) # 5 second timeout
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            print(f"      Ollama connection successful ({base_url})!")
            # Optionally check if the specific model is available via /api/tags
            try:
                tags_url = base_url + "/api/tags"
                tags_response = requests.get(tags_url, timeout=5)
                tags_response.raise_for_status()
                models_data = tags_response.json()
                available_models = [m['name'] for m in models_data.get('models', [])]
                model_tag = self.model_name if ':' in self.model_name else f"{self.model_name}:latest"
                if model_tag not in available_models:
                     print(f"      Warning: Model '{self.model_name}' (checked as '{model_tag}') not found in available models: {available_models}")
                else:
                     print(f"      Model '{self.model_name}' found.")
            except Exception as e:
                print(f"      Warning: Could not verify model list from Ollama API: {e}")

        except requests.exceptions.ConnectionError:
            print(f"      ERROR: Could not connect to Ollama API at {self.api_url}.")
            print("             Ensure Ollama is running and the URL in config.py is correct.")
            # Consider raising an exception here to halt execution if connection is critical
            # raise ConnectionError(f"Failed to connect to Ollama at {self.api_url}")
        except requests.exceptions.Timeout:
            print(f"      ERROR: Connection to Ollama API timed out ({self.api_url}).")
            # raise TimeoutError(f"Connection timeout for Ollama at {self.api_url}")
        except requests.exceptions.RequestException as e:
            print(f"      ERROR: An error occurred during Ollama connection check: {e}")
            # raise e


    def generate(self, prompt: str, system_message: str = None, format_json: bool = False) -> str:
        """
        Sends a prompt to the Ollama API and returns the generated text.

        Args:
            prompt (str): The main user prompt for the LLM.
            system_message (str, optional): An optional system message to guide the LLM's behavior.
            format_json (bool): Whether to request JSON output format from Ollama (model must support it).

        Returns:
            str: The generated text content, or an empty string if an error occurs.
        """
        print(f"    Sending prompt to Ollama (model: {self.model_name})...")
        headers = {'Content-Type': 'application/json'}
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False, # Get the full response at once
            "options": { # Add options like temperature if needed
                 "temperature": 0.7,
                # "num_ctx": 4096 # Example context window size - adjust based on model/needs
            }
        }
        if system_message:
            payload["system"] = system_message
        if format_json:
            payload["format"] = "json"

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload), timeout=120) # Increased timeout for generation
            response.raise_for_status() # Check for HTTP errors

            response_data = response.json()
            generated_text = response_data.get('response', '').strip()

            # Basic logging of response length
            # print(f"      Ollama response received (length: {len(generated_text)} chars).")

            # Optional: Check for "done: false" or other indicators of incomplete generation if not streaming
            if not response_data.get('done', True):
                print("      Warning: Ollama response indicates generation might not be fully complete ('done': false).")

            return generated_text

        except requests.exceptions.Timeout:
            print(f"      ERROR: Request to Ollama timed out after 120 seconds.")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"      ERROR: Failed to get response from Ollama API: {e}")
            # Print response body if available for debugging
            if hasattr(e, 'response') and e.response is not None:
                 try:
                     print(f"      Ollama Response Status Code: {e.response.status_code}")
                     print(f"      Ollama Response Body: {e.response.text}")
                 except Exception:
                     print("      Could not retrieve detailed error response from Ollama.")
            return ""
        except json.JSONDecodeError:
            print(f"      ERROR: Could not decode JSON response from Ollama.")
            print(f"      Raw Response Text: {response.text}")
            return ""
        except Exception as e:
            print(f"      ERROR: An unexpected error occurred during Ollama generation: {e}")
            return ""


# --- Example Usage (if run directly) ---
if __name__ == '__main__':
    print("--- Testing OllamaClient ---")
    try:
        # Ensure config.py is accessible from this script's location if run directly
        # (e.g., run from the project root: python agent/ollama_client.py)
        import sys
        # Add project root to path to find config
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        import config

        client = OllamaClient() # Uses settings from config.py

        test_prompt = "Explain the concept of a Large Language Model in one sentence."
        print(f"\nSending test prompt: '{test_prompt}'")
        result = client.generate(test_prompt)

        if result:
            print("\n--- Ollama Response ---")
            print(result)
            print("-----------------------")
        else:
            print("\n--- Ollama generation failed ---")

    except ConnectionError:
        print("\nOllama connection failed. Ensure Ollama is running.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during testing: {e}")