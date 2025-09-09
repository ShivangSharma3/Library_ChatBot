import os
from google import genai
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import re

class LibraryManagementChatBot:
    def __init__(self):
        load_dotenv()
        
        # Initialize Gemini AI
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Initialize Supabase
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_KEY")
        )
        
        print("📚 Library Management ChatBot initialized!")
        print("Connected to your Supabase database with tables: books, members, reservations, staff, transactions")
        
    def search_book_by_id_or_name(self, query):
        """Search for books by book_id, title, author, ISBN, or publisher"""
        try:
            print(f"🔍 Searching for: {query}")
            
            # Search in books table with your exact column names
            response = self.supabase.table('books').select('*').or_(
                f"book_id.ilike.%{query}%,"
                f"isbn.ilike.%{query}%,"
                f"title.ilike.%{query}%,"
                f"author.ilike.%{query}%,"
                f"publisher.ilike.%{query}%"
            ).execute()
            
            print(f"📚 Found {len(response.data)} books")
            return response.data
                
        except Exception as e:
            print(f"Error searching books: {e}")
            return []
    
    def get_book_issue_info(self, book_id):
        """Get who issued the book and for how long"""
        try:
            # Check transactions table for book issue info
            response = self.supabase.table('transactions').select('*').or_(
                f"book_id.ilike.%{book_id}%,"
                f"isbn.ilike.%{book_id}%"
            ).execute()
            
            issue_info = []
            if response.data:
                issue_info.extend(response.data)
            
            # Also check reservations table
            res_response = self.supabase.table('reservations').select('*').or_(
                f"book_id.ilike.%{book_id}%,"
                f"isbn.ilike.%{book_id}%"
            ).execute()
            
            if res_response.data:
                issue_info.extend(res_response.data)
                
            return issue_info
            
        except Exception as e:
            print(f"Error getting book issue info: {e}")
            return []
    
    def get_member_info(self, member_id):
        """Get member information"""
        try:
            response = self.supabase.table('members').select('*').or_(
                f"member_id.eq.{member_id},"
                f"id.eq.{member_id},"
                f"user_id.eq.{member_id}"
            ).execute()
            
            if response.data:
                return response.data[0]
            return None
                
        except Exception as e:
            print(f"Error getting member info: {e}")
            return None
    
    def search_all_books(self, query):
        """Search all books in library"""
        try:
            response = self.supabase.table('books').select('*').or_(
                f"title.ilike.%{query}%,"
                f"author.ilike.%{query}%,"
                f"publisher.ilike.%{query}%"
            ).execute()
            
            return response.data
                
        except Exception as e:
            print(f"Error searching library: {e}")
            return []
    
    def get_book_availability(self, book_id):
        """Check if book is available or issued"""
        try:
            # Check in transactions and reservations
            issue_info = self.get_book_issue_info(book_id)
            
            if issue_info:
                return {"status": "issued", "details": issue_info}
            else:
                return {"status": "available", "details": None}
                
        except Exception as e:
            return {"status": "unknown", "details": str(e)}
    
    def calculate_days_issued(self, issue_date, return_date=None):
        """Calculate how many days book has been issued"""
        try:
            if isinstance(issue_date, str):
                issue_date = datetime.fromisoformat(issue_date.replace('Z', '+00:00'))
            
            if return_date:
                if isinstance(return_date, str):
                    return_date = datetime.fromisoformat(return_date.replace('Z', '+00:00'))
                days = (return_date - issue_date).days
            else:
                days = (datetime.now() - issue_date.replace(tzinfo=None)).days
            
            return days
        except:
            return "Unknown"
    
    def generate_response(self, user_message, context_data):
        """Generate AI response with library context"""
        try:
            context = """You are a helpful library management assistant for a library system. You can provide information about:
            - Books (by book_id, title, author, ISBN, publisher)
            - Who issued which book and for how long
            - Book availability status
            - Member information
            - Library catalog search
            
            Provide clear, detailed, and helpful responses based on the database information.
            If no data is found, suggest alternative searches or actions."""
            
            if context_data.get('book_info'):
                context += f"\n\n📚 BOOK INFORMATION FOUND:\n"
                for book in context_data['book_info']:
                    context += f"- Title: {book.get('title', 'N/A')}\n"
                    context += f"  Author: {book.get('author', 'N/A')}\n" 
                    context += f"  ISBN: {book.get('isbn', 'N/A')}\n"
                    context += f"  Publisher: {book.get('publisher', 'N/A')}\n"
                    context += f"  Book ID: {book.get('book_id', 'N/A')}\n\n"
            
            if context_data.get('issue_info'):
                context += f"\n\n📋 BOOK ISSUE INFORMATION:\n"
                for issue in context_data['issue_info']:
                    context += f"- {issue}\n"
            
            if context_data.get('member_info'):
                context += f"\n\n👤 MEMBER INFORMATION:\n{context_data['member_info']}"
            
            if context_data.get('availability'):
                context += f"\n\n📊 BOOK AVAILABILITY:\n{context_data['availability']}"
            
            if context_data.get('search_results'):
                context += f"\n\n🔍 SEARCH RESULTS:\n"
                for i, book in enumerate(context_data['search_results'][:5], 1):
                    context += f"{i}. {book.get('title', 'N/A')} by {book.get('author', 'N/A')}\n"
            
            prompt = f"{context}\n\nUser Question: {user_message}\n\nProvide a helpful response:"
            
            response = self.genai_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            return f"Sorry, I encountered an error generating response: {e}"
    
    def process_query(self, user_message):
        """Process user query and gather relevant data"""
        context_data = {}
        
        # Extract potential book IDs, ISBNs, or other identifiers
        numbers = re.findall(r'\b\d+\b', user_message)
        
        # Check if user is asking about a specific book
        if numbers:
            for identifier in numbers:
                # Search for book by ID/ISBN
                book_info = self.search_book_by_id_or_name(identifier)
                if book_info:
                    context_data['book_info'] = book_info
                    
                    # Get issue information for the first book found
                    book_id = book_info[0].get('book_id') or book_info[0].get('isbn')
                    if book_id:
                        issue_info = self.get_book_issue_info(str(book_id))
                        if issue_info:
                            context_data['issue_info'] = issue_info
                            
                            # Get member info if available
                            for issue in issue_info:
                                member_id = issue.get('member_id') or issue.get('user_id')
                                if member_id:
                                    member_info = self.get_member_info(member_id)
                                    if member_info:
                                        context_data['member_info'] = member_info
                                    break
                        
                        # Get availability status
                        availability = self.get_book_availability(str(book_id))
                        context_data['availability'] = availability
                    break
        
        # If no specific ID found, search by title/author
        if not context_data.get('book_info'):
            # Remove common words and search
            search_terms = [word for word in user_message.split() 
                          if len(word) > 2 and word.lower() not in 
                          ['book', 'who', 'issued', 'the', 'and', 'for', 'how', 'long', 'is', 'available']]
            
            if search_terms:
                search_query = ' '.join(search_terms)
                search_results = self.search_all_books(search_query)
                if search_results:
                    context_data['search_results'] = search_results
        
        return context_data
    
    def chat(self):
        """Interactive chat interface"""
        print("\n" + "="*60)
        print("📚 WELCOME TO LIBRARY MANAGEMENT CHATBOT")
        print("="*60)
        print("I can help you with:")
        print("✅ Find book information by ID, title, or author")
        print("✅ Check who issued a specific book")
        print("✅ See how long a book has been issued")
        print("✅ Check book availability status")
        print("✅ Search library catalog")
        print("✅ Get member information")
        print("\n📖 EXAMPLE QUERIES:")
        print("• 'Show info for book ID 12345'")
        print("• 'Who issued Harry Potter book?'")
        print("• 'Is ISBN 9780028 available?'")
        print("• 'Search for Python programming books'")
        print("• 'Books by J.K. Rowling'")
        print("• 'Show all C programming books'")
        print("\nType 'quit' to exit.\n")
        
        while True:
            user_input = input("🔍 Ask me about your library: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n📚 Library ChatBot: Thank you for using the library system! Goodbye! 👋")
                break
            
            if user_input:
                print("\n🔄 Searching library database...")
                
                # Process query and gather context
                context_data = self.process_query(user_input)
                
                # Generate response
                response = self.generate_response(user_input, context_data)
                print(f"\n📚 Library Assistant: {response}\n")
                print("-" * 60)

if __name__ == "__main__":
    try:
        bot = LibraryManagementChatBot()
        bot.chat()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("Please check your .env file and internet connection.")
