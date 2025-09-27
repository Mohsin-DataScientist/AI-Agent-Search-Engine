🔎 AI Agent Search Engine

An AI-powered search engine built with ChatGroq and Streamlit, designed to provide intelligent, interactive, and fun search experiences.
This project combines smart summarization, voice features, and customizable settings to make search more human-like and engaging.

✨ Features

📝 Smart Summarizer Mode – Get concise, meaningful summaries of search results.

🎤 Voice Input & Output – Search using your voice and listen to AI responses.

🧠 Session Titles with History – Automatically saves your search sessions with titles for easy recall.

🎲 Fun Mode – Adds a touch of humor and creativity to responses.

⚙️ Customizable Settings – Adjust temperature (creativity) and iterations (depth of search).

🚀 Tech Stack

ChatGroq
 – AI model backend

Streamlit
 – Frontend framework

SpeechRecognition – For voice input

gTTS – For text-to-speech output

PyAudio – Audio handling

🛠️ Installation

Clone this repository:

git clone https://github.com/your-username/ai-agent-search-engine.git
cd ai-agent-search-engine


Create and activate a virtual environment:

python -m venv agent
agent\Scripts\activate   # On Windows
source agent/bin/activate # On Mac/Linux


Install dependencies:

pip install -r requirements.txt


Run the app:

streamlit run app.py

⚙️ Configuration

You’ll need a valid ChatGroq API key.

Set it in your environment before running:

set GROQ_API_KEY=your_api_key   # Windows
export GROQ_API_KEY=your_api_key # Mac/Linux

📸 Screenshots (Optional)

(Add here later once you have UI screenshots)

📌 Roadmap

 Add dark mode 🌙

 Multi-language support 🌍

 Advanced filtering options 🔍

🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss what you’d like to change.

📜 License

MIT License – feel free to use and modify.
