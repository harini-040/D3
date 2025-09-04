import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# HUGGINGFACE API KEY AND MODEL
API_URL = "https://api-inference.huggingface.co/models/ibm-granite/granite-3.3-2b-instruct"
API_KEY = "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"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def query_hf(messages, user_type="student"):
    # Adapt prompt based on user type
    prefix = "Explain for a student: " if user_type == "student" else "Explain in detail for a professional: "
    conversation = [
        {"role": "system", "content": f"You are a personal finance assistant. Please be clear and helpful."},
        *messages
    ]
    # Add adaptation
    if conversation[-1]["role"] == "user":
        conversation[-1]["content"] = prefix + conversation[-1]["content"]
    payload = {"inputs": conversation}
    res = requests.post(API_URL, headers=headers, json=payload)
    try:
        return res.json()[0]['generated_text']

    except Exception:
        return "Sorry, I'm unable to respond at the moment."

# STREAMLIT UI
st.set_page_config(page_title="Personal Finance Chatbot")
st.title("Personal Finance Chatbot")
st.markdown("Powered by HuggingFace Granite\n\n_Ask about savings, taxes, investments. Upload your expenses for budget summaries & insights._")

# User Type Selection
user_type = st.radio("Are you a student or professional?", ["student", "professional"])

# Chat History
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Chat Input
user_input = st.text_input("Type your finance question here:", key="chat_input")
if st.button("Ask"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply = query_hf([st.session_state.messages[-1]], user_type)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Show Chat Conversation
if st.session_state.messages:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Chatbot:** {msg['content']}")

st.markdown("---")
st.subheader("Budget Summary & Spending Insights")

# Expense CSV Upload
file = st.file_uploader("Upload your monthly expense CSV", type=["csv"])
if file:
    df = pd.read_csv(file)
    st.markdown("### Your Expense Data")
    st.dataframe(df)

    # Summary statistics
    st.write("#### Budget Summary")
    st.write(df.describe())

    # Category spending (Assume df columns: ['Category', 'Amount'])
    if "Category" in df.columns and "Amount" in df.columns:
        cat_sum = df.groupby("Category")['Amount'].sum().reset_index()
        fig = px.pie(cat_sum, names="Category", values="Amount", title="Spending by Category")
        st.plotly_chart(fig)

        overspend = cat_sum[cat_sum["Amount"] > cat_sum["Amount"].mean()]
        tips = []
        for _, row in overspend.iterrows():
            tips.append(f"Consider reducing spending on {row['Category']} ({row['Amount']:.2f}).")
        st.markdown("#### Spending Insights")
        st.write("\n".join(tips))
    else:
        st.info("Please make sure your CSV has 'Category' and 'Amount' columns for insights.")

st.markdown("---")
st.info("Demo only: This chatbot uses HuggingFace Granite, free open-source models, and Streamlit. No IBM Watson required.")
