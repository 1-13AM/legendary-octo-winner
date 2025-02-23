import streamlit as st
from base.prompt_enhancer.enhancer import ConversationManager
from base.memory.memory_store import WeaviateMemoryStore

# Initialize the ConversationManager and memory store once
manager = ConversationManager()
memory_store = WeaviateMemoryStore()

# Configure the page for a centered, chat-like layout
st.set_page_config(page_title="Lumina Chat", layout="centered")
st.title("Lumina Chat")
st.write("A simple chatbot interface resembling ChatGPT/Claude.")

# Initialize chat history in session state (each message has a role and content)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Use st.chat_input if available; otherwise, fall back to a text_input
if hasattr(st, "chat_input"):
    user_input = st.chat_input("Type your message here...")
else:
    user_input = st.text_input("Type your message here...")

# When the user sends a message, process it
if user_input:
    with st.spinner("Thinking..."):
        bot_response = manager.respond(user_input)
    
    # Append both user and bot messages to the chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "bot", "content": bot_response})
    
    print({"role": "user", "content": user_input})
    print({"role": "bot", "content": bot_response})
    # Log the interaction in the memory store
    memory_store.add_interaction({
        "conversation": {
            "Human": user_input,
            "AI": bot_response
        },
        "user_id": "12345678"
    })

# Display the chat history with code highlighting
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        # Check if the message contains code (using <code> tags)
        if "<code>" in msg["content"]:
            # Extract and display code blocks
            parts = msg["content"].split("<code>")
            for i, part in enumerate(parts):
                if "</code>" in part:  # This part contains code
                    code_content = part.split("</code>")[0]
                    st.code(code_content, language="python")
                    # Add any text after the closing tag
                    if part.split("</code>")[1]:
                        st.write(part.split("</code>")[1])
                else:
                    st.write(part)
        else:
            st.write(msg["content"])      