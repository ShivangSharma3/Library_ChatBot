"""
LIBRARY MANAGEMENT CHATBOT
==========================

A modular chatbot system that:
1. Takes natural language queries from users
2. Converts them to SQL queries for Supabase database
3. Fetches relevant data from the library management system
4. Generates appropriate responses using Google Gemini AI

Architecture:
- QueryProcessor: Converts natural language to SQL
- DatabaseManager: Handles Supabase operations  
- ResponseGenerator: Creates AI-powered responses
- LibraryChatBot: Main orchestrator class

Supported Queries:
- Book searches: "Find books by J.K. Rowling"
- Member info: "Show member details for john@email.com"
- Transaction history: "Who has borrowed Harry Potter?"
- Availability: "Is The C Programming Language available?"
- Fines and dues: "Show overdue books with fines"
"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from supabase import create_client, Client
from typing import Dict, List, Optional, Tuple

class QueryProcessor:
    """Converts natural language queries to SQL queries for Supabase"""
    
    def __init__(self):
        self.query_patterns = {
            'book_search': [
                r'(find|search|show|get).*books?.*(by|author).*',
                r'books?.*(title|called|named).*',
                r'(show|find).*book.*id.*',
                r'isbn.*\d+',
                r'(i want|need|looking for).*(book|title).*',
                r'(do you have|is there).*(book|title).*'
            ],
            'availability': [
                r'(is|are).*available\??',
                r'(how many|available).*copies.*',
                r'(in stock|available).*',
                r'(i want|need|can i get).*'
            ],
            'member_info': [
                r'(member|user).*info.*',
                r'show.*member.*',
                r'member.*id.*',
                r'.*@.*\.com.*'  # email pattern
            ],
            'transactions': [
                r'(who|which member).*(borrowed|has|issued).*',
                r'(borrowed|issued).*books?.*',
                r'transaction.*history.*'
            ],
            'fines_overdue': [
                r'(fine|fees?).*',
                r'overdue.*books?.*',
                r'late.*returns?.*',
                r'outstanding.*amount.*'
            ],
            'reservations': [
                r'reserv.*',
                r'(hold|book.*hold).*',
                r'waiting.*list.*'
            ]
        }
    
    def classify_query(self, query: str) -> str:
        """Classify the query type based on patterns"""
        query_lower = query.lower()
        
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return query_type
        
        return 'general'
    
    def extract_search_terms(self, query: str) -> Dict[str, str]:
        """Extract search terms from the query"""
        search_terms = {}
        query_lower = query.lower()
        
        # Extract potential book titles (quoted strings)
        title_match = re.search(r'["\']([^"\']+)["\']', query)
        if title_match:
            search_terms['title'] = title_match.group(1)
        
        # Extract author names (after "by" keyword)
        author_match = re.search(r'by\s+([a-zA-Z\s.]+?)(?:\s|$)', query_lower)
        if author_match:
            search_terms['author'] = author_match.group(1).strip()
        
        # Extract ISBN numbers
        isbn_match = re.search(r'isbn\s*:?\s*(\d+)', query_lower)
        if isbn_match:
            search_terms['isbn'] = isbn_match.group(1)
        
        # Extract email addresses
        email_match = re.search(r'(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)', query)
        if email_match:
            search_terms['email'] = email_match.group(1)
        
        # Extract UUIDs
        uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', query_lower)
        if uuid_match:
            search_terms['id'] = uuid_match.group(1)
        
        # Extract book titles from natural language queries
        # Look for common book title patterns
        book_title_patterns = [
            r'(?:want|need|looking for|find|get|show).*?((?:[A-Z][a-z]+\s*){2,})',
            r'(?:book|title)\s+(?:called|named)?\s*["\']?([^"\']+)["\']?',
            r'(Harry Potter[^,.\n]*)',
            r'(The [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+and\s+the\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in book_title_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                potential_title = match.group(1).strip()
                # Clean up the title
                potential_title = re.sub(r'^(want|need|this|book|title)\s+', '', potential_title, flags=re.IGNORECASE)
                if len(potential_title) > 3:
                    search_terms['title'] = potential_title
                    break
        
        # Extract general search terms (remove common words) only if no specific terms found
        if not search_terms:
            words = query.split()
            relevant_words = [word for word in words if len(word) > 2 and 
                             word.lower() not in ['the', 'and', 'or', 'but', 'show', 'find', 'get', 'book', 'books', 'want', 'need', 'this', 'that', 'have']]
            if relevant_words:
                search_terms['general'] = ' '.join(relevant_words[:3])  # Limit to 3 words
        
        return search_terms
    
    def generate_sql_query(self, query_type: str, search_terms: Dict[str, str]) -> Tuple[str, str]:
        """Generate SQL query based on query type and search terms"""
        
        if query_type == 'book_search':
            if 'title' in search_terms:
                return 'books', f"title.ilike.%{search_terms['title']}%"
            elif 'author' in search_terms:
                return 'books', f"author.ilike.%{search_terms['author']}%"
            elif 'isbn' in search_terms:
                return 'books', f"isbn.eq.{search_terms['isbn']}"
            elif 'id' in search_terms:
                return 'books', f"book_id.eq.{search_terms['id']}"
            elif 'general' in search_terms:
                term = search_terms['general']
                return 'books', f"title.ilike.%{term}%,author.ilike.%{term}%,genre.ilike.%{term}%"
        
        elif query_type == 'member_info':
            if 'email' in search_terms:
                return 'members', f"email.eq.{search_terms['email']}"
            elif 'id' in search_terms:
                return 'members', f"member_id.eq.{search_terms['id']}"
            elif 'general' in search_terms:
                term = search_terms['general']
                return 'members', f"full_name.ilike.%{term}%,email.ilike.%{term}%"
        
        elif query_type == 'transactions':
            if 'title' in search_terms or 'author' in search_terms or 'general' in search_terms:
                # Need to join with books table
                return 'transactions', '*'  # Will handle complex query in database manager
            elif 'email' in search_terms:
                return 'transactions', f"member_id.in.(select member_id from members where email.eq.{search_terms['email']})"
        
        elif query_type == 'fines_overdue':
            return 'transactions', f"return_date.is.null,fine.gt.0"
        
        elif query_type == 'reservations':
            if 'title' in search_terms or 'general' in search_terms:
                return 'reservations', '*'  # Will handle with joins
            return 'reservations', 'status.eq.Pending'
        
        elif query_type == 'availability':
            if 'title' in search_terms:
                return 'books', f"title.ilike.%{search_terms['title']}%"
            elif 'author' in search_terms:
                return 'books', f"author.ilike.%{search_terms['author']}%"
            elif 'general' in search_terms:
                term = search_terms['general']
                return 'books', f"title.ilike.%{term}%,author.ilike.%{term}%"
        
        # Default fallback
        return 'books', '*'

class DatabaseManager:
    """Handles all Supabase database operations"""
    
    def __init__(self):
        load_dotenv()
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    def execute_query(self, table: str, filter_condition: str) -> List[Dict]:
        """Execute the generated SQL query on Supabase"""
        try:
            if filter_condition == '*':
                # Get all records (limited)
                response = self.supabase.table(table).select('*').limit(10).execute()
            elif ',' in filter_condition:
                # Multiple OR conditions
                response = self.supabase.table(table).select('*').or_(filter_condition).execute()
            else:
                # Single condition - need to parse it
                if '.eq.' in filter_condition:
                    field, value = filter_condition.split('.eq.')
                    response = self.supabase.table(table).select('*').eq(field, value).execute()
                elif '.ilike.' in filter_condition:
                    field, value = filter_condition.split('.ilike.')
                    response = self.supabase.table(table).select('*').ilike(field, value).execute()
                elif '.gt.' in filter_condition:
                    field, value = filter_condition.split('.gt.')
                    response = self.supabase.table(table).select('*').gt(field, float(value)).execute()
                elif '.is.null' in filter_condition:
                    field = filter_condition.replace('.is.null', '')
                    response = self.supabase.table(table).select('*').is_(field, 'null').execute()
                else:
                    # Fallback to basic select
                    response = self.supabase.table(table).select('*').limit(5).execute()
            
            return response.data
            
        except Exception as e:
            print(f"Database query error: {e}")
            return []
    
    def get_related_data(self, query_type: str, primary_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Fetch related data based on primary query results"""
        related_data = {}
        
        if query_type == 'book_search' and primary_data:
            # Get reservations and transactions for these books
            book_ids = [book['book_id'] for book in primary_data]
            
            # Get current transactions
            for book_id in book_ids[:3]:  # Limit to first 3 books
                transactions = self.supabase.table('transactions').select('*').eq('book_id', book_id).execute()
                if transactions.data:
                    related_data[f'transactions_{book_id}'] = transactions.data
        
        elif query_type == 'member_info' and primary_data:
            # Get member's transactions and reservations
            member_ids = [member['member_id'] for member in primary_data]
            
            for member_id in member_ids[:2]:  # Limit to first 2 members
                transactions = self.supabase.table('transactions').select('*').eq('member_id', member_id).execute()
                reservations = self.supabase.table('reservations').select('*').eq('member_id', member_id).execute()
                
                if transactions.data:
                    related_data[f'transactions_{member_id}'] = transactions.data
                if reservations.data:
                    related_data[f'reservations_{member_id}'] = reservations.data
        
        return related_data

class ResponseGenerator:
    """Generates AI-powered responses using Google Gemini"""
    
    def __init__(self):
        load_dotenv()
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def generate_response(self, 
                         original_query: str, 
                         query_type: str,
                         primary_data: List[Dict], 
                         related_data: Dict[str, List[Dict]] = None) -> str:
        """Generate a comprehensive response based on fetched data"""
        
        # Build context for AI
        context = f"""You are a helpful library management assistant. 
        
User asked: "{original_query}"
Query type identified: {query_type}

Database results:"""
        
        if primary_data:
            context += f"\n\nPrimary data found ({len(primary_data)} records):\n"
            for i, record in enumerate(primary_data[:5], 1):  # Limit to 5 records
                context += f"{i}. {record}\n"
        else:
            context += "\n\nNo primary data found for this query."
        
        if related_data:
            context += f"\n\nRelated data:\n"
            for key, data in related_data.items():
                context += f"{key}: {len(data)} records\n"
                if data:
                    context += f"Sample: {data[0]}\n"
        
        context += f"""

Please provide a helpful, detailed response to the user's query based on this library data. 
Be specific about book availability, member information, fines, or whatever the user asked about.
If no data was found, suggest alternative searches or actions.

IMPORTANT: Format your response in clean, readable plain text WITHOUT any markdown formatting. 
Do NOT use asterisks (*), hashtags (#), or other markdown symbols. 
Use simple formatting like:
- Use line breaks for readability
- Use "Book Title:" instead of "**Book Title:**"
- Use bullet points with dashes (-) instead of markdown lists
- Keep the text natural and conversational"""
        
        try:
            response = self.genai_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=context
            )
            return response.text
            
        except Exception as e:
            return f"I apologize, but I encountered an error generating a response: {e}"

class LibraryChatBot:
    """Main chatbot orchestrator that coordinates all components"""
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.database_manager = DatabaseManager()
        self.response_generator = ResponseGenerator()
        print("📚 Library ChatBot initialized successfully!")
    
    def process_user_query(self, user_query: str) -> str:
        """Process a user query and return a comprehensive response"""
        
        # Step 1: Classify query and extract search terms
        query_type = self.query_processor.classify_query(user_query)
        search_terms = self.query_processor.extract_search_terms(user_query)
        
        print(f"🔍 Query type: {query_type}")
        print(f"🎯 Search terms: {search_terms}")
        
        # Step 2: Generate SQL query
        table, filter_condition = self.query_processor.generate_sql_query(query_type, search_terms)
        
        print(f"📋 SQL Query: SELECT * FROM {table} WHERE {filter_condition}")
        
        # Step 3: Execute database query
        primary_data = self.database_manager.execute_query(table, filter_condition)
        
        # Step 4: Get related data if needed
        related_data = self.database_manager.get_related_data(query_type, primary_data)
        
        # Step 5: Generate AI response
        response = self.response_generator.generate_response(
            user_query, query_type, primary_data, related_data
        )
        
        return response
    
    def chat(self):
        """Interactive chat interface"""
        print("\n" + "="*70)
        print("📚 LIBRARY MANAGEMENT CHATBOT - NATURAL LANGUAGE TO SQL")
        print("="*70)
        print("🤖 I can help you with:")
        print("  📖 Book searches: 'Find books by J.K. Rowling'")
        print("  👤 Member info: 'Show details for john@email.com'")
        print("  📋 Transactions: 'Who borrowed Harry Potter?'")
        print("  ✅ Availability: 'Is The C Programming Language available?'")
        print("  💰 Fines: 'Show overdue books'")
        print("  🔖 Reservations: 'Show pending reservations'")
        print("\nType 'quit' to exit.\n")
        
        while True:
            user_input = input("💭 Ask me anything about the library: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n📚 Thank you for using the Library ChatBot! Goodbye! 👋")
                break
            
            if user_input:
                print(f"\n🔄 Processing your query...")
                try:
                    response = self.process_user_query(user_input)
                    print(f"\n🤖 Library Assistant: {response}\n")
                    print("-" * 70)
                except Exception as e:
                    print(f"\n❌ Error: {e}\n")

def main():
    """Main function to run the chatbot"""
    try:
        bot = LibraryChatBot()
        bot.chat()
    except Exception as e:
        print(f"❌ Failed to initialize Library ChatBot: {e}")
        print("Please check your .env file and database connection.")

if __name__ == "__main__":
    main()