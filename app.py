import streamlit as st
from emotion_recognition import EmotionRecognizer
import tempfile
import os
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch

# Set up Streamlit UI
st.set_page_config(page_title="Audio Emotion + Chatbot", layout="centered")
st.title("🎙️ Emotion Recognition from Audio + Chat Support")
st.write("Upload a WAV file to detect emotion, then chat with an AI for help or support.")

# Load Chat Model
@st.cache_resource
def load_llm():
    model_name = "facebook/blenderbot-400M-distill"
    tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
    model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_llm()

def generate_response(user_input):
    inputs = tokenizer([user_input], return_tensors="pt")
    reply_ids = model.generate(**inputs, max_length=100)
    response = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
    return response

# Initialize EmotionRecognizer
rec = EmotionRecognizer(
    emotions=["neutral", "happy", "sad", "angry"],
    balance=False,
    verbose=0,
    custom_db=False
)

# Initialize session state
if "emotion" not in st.session_state:
    st.session_state.emotion = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Upload and predict
uploaded_file = st.file_uploader("🔊 Choose a WAV file", type=["wav"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    if st.button("🎯 Predict Emotion"):
        with st.spinner("Analyzing audio..."):
            try:
                prediction = rec.predict(temp_path)
                accuracy = rec.test_score() * 100
                st.session_state.emotion = prediction
                st.success(f"🎯 Detected Emotion: **{prediction}**")
                st.info(f"📈 Model Accuracy: {accuracy:.2f}%")
                st.session_state.chat_history.append(f"🔍 Detected emotion from audio: {prediction}")
            except Exception as e:
                st.error(f"Error: {e}")
        os.remove(temp_path)

# After emotion is detected, show chat
if st.session_state.emotion:
    st.subheader("💬 Would you like to share your emotion?")
    with st.form(key="chat_form"):
        user_input = st.text_input("You:", placeholder="Type your feelings or ask for help...")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_input:
        st.session_state.chat_history.append(f"You: {user_input}")
        with st.spinner("AI typing..."):
            reply = generate_response(user_input)
            st.session_state.chat_history.append(f"AI: {reply}")

    # Display chat history
    for msg in st.session_state.chat_history:
        st.write(msg)