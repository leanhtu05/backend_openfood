"""
A fresh implementation of a simple Groq client to work around proxy issues
"""
import os
import groq

def create_groq_client(api_key=None):
    """
    Create a Groq client with the given API key
    
    Args:
        api_key (str, optional): The API key to use. If None, uses GROQ_API_KEY env var.
        
    Returns:
        groq.Groq: A Groq client
    """
    if api_key is None:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        raise ValueError("No API key provided and GROQ_API_KEY env var not set")
    
    # Create client with minimal arguments to avoid proxy issues
    client = groq.Groq(api_key=api_key)
    return client

def get_available_models(client):
    """
    Get available models from the Groq API
    
    Args:
        client (groq.Groq): The Groq client
        
    Returns:
        list: A list of available model IDs
    """
    models = client.models.list()
    return [model.id for model in models.data]
    
def generate_completion(client, model, prompt, temperature=0.7, max_tokens=1000):
    """
    Generate a completion using the Groq API
    
    Args:
        client (groq.Groq): The Groq client
        model (str): The model to use
        prompt (str): The prompt to use
        temperature (float, optional): The temperature. Defaults to 0.7.
        max_tokens (int, optional): The maximum tokens. Defaults to 1000.
        
    Returns:
        str: The generated text
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content.strip()

# Example usage
if __name__ == "__main__":
    try:
        # Create client
        client = create_groq_client()
        print("Successfully created Groq client")
        
        # Get available models
        models = get_available_models(client)
        print(f"Available models: {', '.join(models)}")
        
        # Use a default model
        model = "llama3-8b-8192" if "llama3-8b-8192" in models else models[0]
        print(f"Using model: {model}")
        
        # Generate a simple completion
        prompt = "Say hello in 5 words or less"
        result = generate_completion(client, model, prompt)
        print(f"Response: {result}")
        
    except Exception as e:
        print(f"Error: {str(e)}") 