import streamlit as st
import requests

def check_perplexity_api_connection(api_key):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Check connection."},
            {"role": "user", "content": "Hello!"}
        ],
        "max_tokens": 5,
        "temperature": 0.2,
        "top_p": 0.9
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def query_perplexity(prompt, api_key, model="sonar-pro", system_message="You are a helpful assistant."):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 10000,
        "temperature": 0.7,
        "top_p": 0.9
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Exception: {e}"

st.title("DARS-Agent")

api_key = st.text_input("Model API Key", type="password")
if api_key:
    if st.button("Check API Connection"):
        if check_perplexity_api_connection(api_key):
            st.success("Connection successful!")
        else:
            st.error("API connection failed. Check your API key and network.")

    st.write("## Query the LLM")
    prompt = st.text_area("Prompt:", height=100)
    model_name = st.selectbox("Model", options=["sonar", "sonar-pro", "gpt-4o", "sonar-deep-research","sonar-reasoning"], index=1)

    # ADD FILE UPLOADER
    uploaded_file = st.file_uploader("Upload a file for chatperplexity context (optional):", type=None)

    if uploaded_file is not None:
        # Display file information and allow for basic file analysis
        st.write(f"**Uploaded file:** {uploaded_file.name}")
        content = uploaded_file.read()
        try:
            # Try decoding as text (may fail for binary)
            decoded_content = content.decode("utf-8")
            st.text_area("File Content Preview:", decoded_content, height=150, disabled=True)
        except Exception:
            st.info("Uploaded file is not plain text. It will be processed as binary.")
    
    # ANALYSE BUTTON TO QUERY THE API
    if st.button("Analyse (Send Prompt + File)"):
        final_prompt = prompt
        if uploaded_file is not None:
            # Add a file indicator or content into prompt; adapt logic as needed for your LLM API
            try:
                file_content = content.decode("utf-8")
            except Exception:
                file_content = str(content)
            final_prompt += "\n\n[File Content Starts]\n" + file_content[:8000] + "\n[File Content Ends]"  # Limit size for token efficiency

        with st.spinner("Querying the model..."):
            response = query_perplexity(final_prompt, api_key, model=model_name)
        st.write("**Response:**")
        st.code(response)
else:
    st.info("Enter your API key to begin.")