import streamlit as st

st.set_page_config(
    page_title="Hello, Computer",
    page_icon="\U0001f3a4",
    layout="wide",
)

st.title("Hello, Computer")
st.subheader("Azure AI Speech Service Demos")

st.markdown(
    """
    Select a demo from the sidebar:

    - **Speech to Text** -- transcribe audio from your microphone or a WAV file
    - **Text to Speech** -- type text and hear it spoken in a neural voice
    - **Chat with AI** -- speak to a language model and hear its response
    """
)
