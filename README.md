# Library ChatBot

An intelligent library management chatbot that converts natural language queries into SQL queries for Supabase database operations. Built with Google Gemini AI and featuring a modular, scalable architecture.

## 🚀 Features

- 🧠 **Natural Language Processing** - Understands conversational queries like "I want Harry Potter book"
- 🔄 **Automatic SQL Generation** - Converts text queries to optimized Supabase database queries
- 📚 **Comprehensive Library Operations** - Books, members, transactions, reservations, fines management
- 🤖 **AI-Powered Responses** - Context-aware responses using Google Gemini 2.0 Flash
- 🏗️ **Modular Architecture** - Easily extensible and maintainable codebase
- 💾 **Real-time Database Integration** - Live data from your Supabase library management system
- 🎯 **Smart Query Classification** - Automatically identifies query types and search patterns

## 🏗️ Architecture

The chatbot follows a modular design with four main components:

```
User Query → QueryProcessor → DatabaseManager → ResponseGenerator → Response
     ↓              ↓              ↓              ↓
"Find books    → book_search   → SQL Query    → AI Context    → Clean formatted
by Rowling"      + author      → books table  → + Results     → response
```

### Components:

1. **QueryProcessor** - Natural language understanding and SQL generation
2. **DatabaseManager** - Supabase database operations and data fetching
3. **ResponseGenerator** - AI-powered response generation with Google Gemini
4. **LibraryChatBot** - Main orchestrator coordinating all components

## 📖 Supported Query Types

### Book Searches
- "Find books by J.K. Rowling"
- "I want Harry Potter and the Goblet of Fire"
- "Show me programming books"
- "Books about Python"

### Availability Checks
- "Is The C Programming Language available?"
- "How many copies of Harry Potter are in stock?"
- "Do you have Introduction to Algorithms?"

### Member Information
- "Show member details for john@email.com"
- "Member info for ID 9b84bfa3-df67..."
- "Find member named John Smith"

### Transaction History
- "Who borrowed Harry Potter?"
- "Show transaction history for member1@example.com"
- "Which books are currently issued?"

### Fines & Overdue Books
- "Show overdue books"
- "Members with outstanding fines"
- "Books returned late with fines"

### Reservations
- "Show pending reservations"
- "Who reserved The C Programming Language?"
- "Reservation status for book ID 123"

## 🛠️ Setup

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
2. Set up your library management tables (books, members, staff, reservations, transactions)
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
python app.py
```

## 🗄️ Database Schema

The chatbot works with the following database structure:

### Books Table
- `book_id` (UUID) - Primary key
- `isbn`, `title`, `author`, `publisher`
- `genre`, `year_of_publication`, `pages`, `language`
- `shelf_location`, `total_copies`, `available_copies`, `status`

### Members Table
- `member_id` (UUID) - Primary key
- `full_name`, `email`, `phone`, `address`
- `membership_type`, `membership_start`, `membership_expiry`
- `max_borrow_limit`, `fine_balance`

### Transactions Table
- `transaction_id` (UUID) - Primary key
- `book_id`, `member_id` (Foreign keys)
- `issue_date`, `due_date`, `return_date`, `fine`

### Reservations Table
- `reservation_id` (UUID) - Primary key
- `book_id`, `member_id` (Foreign keys)
- `reservation_date`, `status`

### Staff Table
- `staff_id` (UUID) - Primary key
- `full_name`, `role`, `email`, `password_hash`

## 🔧 How It Works

1. **Query Processing**: Natural language is analyzed to identify intent and extract search terms
2. **SQL Generation**: Queries are converted to appropriate Supabase filter conditions
3. **Database Operations**: Data is fetched from relevant tables with proper joins
4. **AI Response**: Google Gemini generates contextual responses based on retrieved data
5. **Clean Formatting**: Responses are formatted without markdown for better readability

## 💡 Example Interactions

```
User: "I want Harry Potter and the Goblet of Fire"
🔍 Query type: book_search
🎯 Search terms: {'title': 'Harry Potter and the Goblet of Fire'}
📋 SQL Query: SELECT * FROM books WHERE title.ilike.%Harry Potter and the Goblet of Fire%

Response: Found "Harry Potter and the Goblet of Fire" by J.K. Rowling. 
Available: 2 out of 4 copies. Location: Shelf F1. 
You can borrow this book right now!
```

## 🚀 Advanced Features

- **Multi-table Queries** - Automatically fetches related data from multiple tables
- **Smart Search Term Extraction** - Recognizes book titles, author names, ISBNs, emails
- **Error Handling** - Graceful degradation with helpful error messages
- **Query Debugging** - Shows processing steps for transparency
- **Extensible Patterns** - Easy to add new query types and search patterns

## 📁 Project Structure

```
Library_ChatBot/
├── app.py                          # Main modular chatbot application
├── test_connection.py              # Database connection testing
├── database_analyzer.py            # Database schema analysis tool
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (not tracked)
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 👥 Contributors

This project was developed by:

- **Arjun** ([GitHub](https://github.com/arjunheregeek), [Portfolio](https://arjunai.engineer))
  - Contributed Supabase functionality and project logic.

- **Shivang** ([GitHub](https://github.com/ShivangSharma3))
  - Built the chatbot and integrated it with the database.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues:

1. **Database Connection Errors**: Check your `.env` file and Supabase credentials
2. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **API Rate Limits**: Google Gemini API has usage limits; check your quota
4. **Query Not Understood**: Try rephrasing with more specific terms

### Debug Mode:
The chatbot shows processing steps including query classification and SQL generation for debugging.

## 🎯 Roadmap

- [ ] Web interface with Flask/FastAPI
- [ ] Voice input support
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Real-time notifications
- [ ] Integration with library card systems

---

**Built with ❤️ using Google Gemini AI and Supabase**
