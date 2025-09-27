import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import warnings

# Extra imports for new features (Voice output only)
from gtts import gTTS
from io import BytesIO

warnings.filterwarnings("ignore")

load_dotenv()

# ---------------------- SCRAPER TOOL ----------------------
class EnchancedWebScrapperTool:
    def __init__(self):
        self.name = "Webscrapper"
        self.description = "Scrape content from a website with advanced options. Input should be URL"

    def run(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.9 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Like Gecko) Chrome/91.0.4472.124 safari/537.36"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style", "footer", "nav", "aside"]):
                script.extract()

            text = soup.get_text(separator="\n", strip=True)

            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            max_length = 4000
            if len(text) > max_length:
                text = text[:max_length] + "...\n[content truncated due to length]"

            return f"Content from {url}:\n\n{text}"
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"


# ---------------------- STREAMLIT UI ----------------------
st.set_page_config(
    page_title="Web Search AI Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("Web Search AI Agent")
    st.write("This Tool allows you to ask questions and get answers from the web.")

    st.subheader("How it Works")
    st.write("""
    1. Enter your question in the input field  
    2. The AI agent will:  
       - Search the web  
       - Scrape website content  
       - Generate a comprehensive answer  
    """)

    st.subheader("Settings")

    model_choice = st.selectbox(
        "Choose Language Model",
        options=["moonshotai/kimi-k2-instruct-0905", "llama-3.1-8b-instant", "openai/gpt-oss-120b"],
        index=0
    )

    temperature = st.slider(
        "Temperature (Creativity)", min_value=0.0, max_value=1.0, value=0.5, step=0.1
    )

    max_iterations = st.slider(
        "Max Search Iterations", min_value=1, max_value=10, value=5
    )

    mode = st.radio(
        "Select Mode",
        ["Normal 🤖", "Smart Summarizer 📝", "Fun 🎲"]
    )

st.title("🌐 Web Search AI Agent")
st.write("Ask me anything, and I'll search the web for you!")


# ---------------------- INITIALIZE AGENT ----------------------
@st.cache_resource
def initialize_web_agent(model_name, temp, max_iter):
    api_key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(
        temperature=temp,
        model=model_name,
        groq_api_key=api_key
    )

    agent_type = AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION
    search_tool = DuckDuckGoSearchRun()
    web_scrapper_tool = EnchancedWebScrapperTool()

    tools = [
        Tool(name="Search", func=search_tool.run, description="Useful for searching the web. Input should be a search query."),
        Tool(name="Webscraper", func=web_scrapper_tool.run, description="Scrapes content from a specific website. Input should be a URL.")
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=agent_type,
        verbose=True,
        max_iterations=max_iter,
        handle_parsing_errors=True,
        early_stopping_method="generate"
    )
    return agent


# ---------------------- SESSION STATE ----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "session_title" not in st.session_state:
    st.session_state.session_title = "Untitled Session"


# ---------------------- CHAT HISTORY ----------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------- USER INPUT ----------------------
user_question = st.chat_input("What would you like to know?")


# ---------------------- RUN AGENT ----------------------
try:
    agent = initialize_web_agent(model_choice, temperature, max_iterations)
except Exception as e:
    st.error(f"Error initializing agent: {e}")
    agent = None

if user_question and agent:
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.status("Working on it...", expanded=True) as status:
            st.write("Searching the web...")

            try:
                # Handle modes
                if mode == "Smart Summarizer 📝":
                    raw_response = agent.run(user_question)
                    response = "📑 Summary:\n\n" + " ".join(raw_response.split()[:60]) + "..."
                elif mode == "Fun 🎲":
                    raw_response = agent.run(user_question)
                    response = f"🎉 Fun Mode:\n\n{raw_response}\n😂"
                else:
                    response = agent.run(user_question)

                status.update(label="Search complete", state="complete")
                message_placeholder.markdown(response)

                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.history.append({"q": user_question, "a": response})

                # 🔊 Voice Output
                if st.button("🔊 Read Aloud"):
                    tts = gTTS(text=response, lang="en")
                    audio_fp = BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp.getvalue(), format="audio/mp3")

            except Exception as e:
                status.update(label="Error", state="error")
                error_message = f"An error occurred: {str(e)}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})


# ---------------------- DISPLAY CHAT HISTORY ----------------------
st.write("## 📜 Chat History")
st.text_input("Session Title", st.session_state.session_title, key="session_title")

for h in st.session_state.history:
    st.write(f"**You:** {h['q']}")
    st.write(f"**Agent:** {h['a']}")
