# Library ChatBot

A simple chatbot using Google Gemini API, built in Python. cool

## Features
- Uses Google Gemini (genai) for content generation
- Loads API key from `.env` file
- Simple command-line interface

## Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/ShivangSharma3/Library_ChatBot.git
   cd Library_ChatBot
   ```
2. Create and activate a virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Add your Gemini API key to a `.env` file:
   ```sh
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```
5. Run the chatbot:
   ```sh
   python app.py
   ```

## License
MIT
