def write_file_ai(command_text: str) -> str:
    """
    Use local LLM (Ollama) to write content to a file.
    Example: 'write a README for my movie recommendation project'
    
    Note: Requires Ollama to be running locally with a model (e.g., llama2 or mistral).
    """
    try:
        import ollama
    except ImportError:
        return "Ollama library is not installed. Run 'pip install ollama'."

    # Expected command: write a <filename> for <prompt> or similar
    # For simplicity, we just pass the whole command to the AI and ask it to output file content
    prompt = command_text.replace("write ", "").strip()
    if not prompt:
        return "Please specify what to write."

    try:
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'system',
                'content': 'You are a helpful assistant. Provide only the file content based on the user request, without markdown formatting or extra talk.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        content = response['message']['content']
        
        # Save to a generic output file for now
        output_file = "ai_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Successfully generated and saved to {output_file}"
        
    except Exception as e:
        return f"Failed to generate text using Ollama: {str(e)}"
