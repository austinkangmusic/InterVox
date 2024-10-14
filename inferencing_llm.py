import chat_utils

# Initialize LLM models
chat_utils.initialize()

chat_llm = chat_utils.use_chat_llm()



def stream_response(model, system_prompt, conversation_history):
    # Combine system prompt, conversation history, and user input
    full_conversation = [{"role": "system", "content": system_prompt}] + conversation_history
    
    chunks = []
    
    # Stream response from the model
    response_generator = model.stream(full_conversation)  # Adjust based on the streaming mechanism
    
    # Iterate through the streamed response
    for chunk in response_generator:
        if isinstance(chunk, str):
            # If chunk is a string, append directly
            chunks.append(chunk)
            print(chunk, end="", flush=True)
        else:
            # If chunk is an object, handle accordingly
            delta_content = chunk.content  # Update this based on actual response structure
            if delta_content is not None:
                chunks.append(delta_content)
                print(delta_content, end="", flush=True)

    print('\n')
    return ''.join(chunks)

conversation_history = []

system_prompt = ''

while True:
        user_input = input('User:\n')

        conversation_history.append({"role": "user", "content": user_input})
    
        # Stream the response with the system prompt, user input, and conversation history
        chatbot_response = stream_response(chat_llm, system_prompt, conversation_history)