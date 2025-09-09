# Library ChatBot

An intelligent library chatbot using Google Gemini AI with Supabase database integration for conversation history and library resource management.

## Features
- 🤖 AI-powered responses using Google Gemini 2.0 Flash
- 💾 Conversation history stored in Supabase database
- 📚 Library resource search and management
- 👤 User-specific conversation tracking
- 🔍 Context-aware responses using conversation history

## Setup

### 1. Clone the repository
```sh
git clone https://github.com/ShivangSharma3/Library_ChatBot.git
cd Library_ChatBot
```

### 2. Create and activate virtual environment
```sh
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Set up Supabase Database
1. Create a new project on [Supabase](https://supabase.com)
2. Go to SQL Editor and run the contents of `database_schema.sql`
3. Get your project URL and anon key from Settings > API

### 5. Configure environment variables
Create a `.env` file with:
```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 6. Run the chatbot
```sh
# Simple version (original)
python app.py

# Enhanced version with database
python chatbot.py
```

## Database Schema

The chatbot uses two main tables:

### conversations
- Stores chat history with user messages and bot responses
- Tracks user IDs and timestamps
- Enables context-aware conversations

### library_resources
- Stores library catalog (books, resources)
- Includes title, author, ISBN, description, category, location
- Enables intelligent resource recommendations

## Usage

1. Run `python chatbot.py`
2. Enter your user ID (or use 'anonymous')
3. Start chatting! The bot will:
   - Remember your conversation history
   - Search library resources based on your queries
   - Provide contextual responses using AI

## API Endpoints (Future Enhancement)

The project can be extended with Flask/FastAPI to create REST endpoints:
- `POST /chat` - Send message and get response
- `GET /history/{user_id}` - Get conversation history
- `GET /resources` - Search library resources

## License
MIT
