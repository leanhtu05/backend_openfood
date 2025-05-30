"""
A direct HTTP client for the Groq API without using the groq package
"""
import os
import json
import httpx

class DirectGroqClient:
    """
    A simple client for the Groq API using direct HTTP requests
    """
    def __init__(self, api_key=None):
        """
        Initialize the client with the given API key
        
        Args:
            api_key (str, optional): The API key to use. If None, uses GROQ_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and GROQ_API_KEY env var not set")
        
        self.base_url = "https://api.groq.com/openai/v1"
        self.client = httpx.Client(timeout=60.0)
        self.client.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def list_models(self):
        """
        List available models
        
        Returns:
            list: A list of available model IDs
        """
        response = self.client.get(f"{self.base_url}/models")
        response.raise_for_status()
        data = response.json()
        return [model["id"] for model in data["data"]]
    
    def generate_completion(self, model, prompt, temperature=0.7, max_tokens=1000):
        """
        Generate a completion using the Groq API
        
        Args:
            model (str): The model to use
            prompt (str): The prompt to use
            temperature (float, optional): The temperature. Defaults to 0.7.
            max_tokens (int, optional): The maximum tokens. Defaults to 1000.
            
        Returns:
            str: The generated text
        """
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = self.client.post(
            f"{self.base_url}/chat/completions",
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    
    def close(self):
        """Close the HTTP client"""
        if self.client:
            self.client.close()

# Example usage
if __name__ == "__main__":
    try:
        # Create client
        client = DirectGroqClient()
        print("Successfully created Groq client")
        
        # Get available models
        models = client.list_models()
        print(f"Available models: {', '.join(models)}")
        
        # Use a default model
        model = "llama3-8b-8192" if "llama3-8b-8192" in models else models[0]
        print(f"Using model: {model}")
        
        # Generate a simple completion
        prompt = "Say hello in 5 words or less"
        result = client.generate_completion(model, prompt)
        print(f"Response: {result}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Close the client
        if 'client' in locals():
            client.close() 