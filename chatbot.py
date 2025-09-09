from google import genai
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid
from datetime import datetime

class EnhancedLibraryChatBot:
    def __init__(self):
        load_dotenv()
        
        # Initialize Gemini AI
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Initialize Supabase
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_KEY")
        )
        
        print("🤖 Enhanced Library ChatBot initialized!")
        
    def search_student_info(self, student_identifier):
        """Search for student by ID, name, or email"""
        results = {}
        
        # Try different table names for student data
        student_tables = ['students', 'users', 'members', 'library_members']
        
        for table in student_tables:
            try:
                # Search by different fields
                response = self.supabase.table(table).select('*').or_(
                    f"id.eq.{student_identifier},"
                    f"student_id.eq.{student_identifier},"
                    f"user_id.eq.{student_identifier},"
                    f"email.ilike.%{student_identifier}%,"
                    f"name.ilike.%{student_identifier}%"
                ).execute()
                
                if response.data:
                    results[table] = response.data
                    
            except Exception as e:
                continue
                
        return results
    
    def get_student_reservations(self, student_id):
        """Get student's current reservations"""
        try:
            response = self.supabase.table('reservations').select('*').or_(
                f"user_id.eq.{student_id},"
                f"student_id.eq.{student_id},"
                f"member_id.eq.{student_id}"
            ).execute()
            
            return response.data
        except Exception as e:
            return []
    
    def get_student_books(self, student_id):
        """Get student's borrowed books"""
        book_tables = ['loans', 'borrowed_books', 'transactions']
        
        for table in book_tables:
            try:
                response = self.supabase.table(table).select('*').or_(
                    f"user_id.eq.{student_id},"
                    f"student_id.eq.{student_id},"
                    f"member_id.eq.{student_id}"
                ).execute()
                
                if response.data:
                    return response.data
            except Exception as e:
                continue
                
        return []
    
    def get_student_fines(self, student_id):
        """Get student's fines/fees"""
        fine_tables = ['fines', 'fees', 'accounts', 'transactions']
        
        for table in fine_tables:
            try:
                response = self.supabase.table(table).select('*').or_(
                    f"user_id.eq.{student_id},"
                    f"student_id.eq.{student_id},"
                    f"member_id.eq.{student_id}"
                ).execute()
                
                if response.data:
                    return response.data
            except Exception as e:
                continue
                
        return []
    
    def search_book_by_id_or_name(self, query):
        """Search for books by ID, title, author, or ISBN"""
        try:
            # Search in books table with your exact column names
            response = self.supabase.table('books').select('*').or_(
                f"book_id.eq.{query},"
                f"isbn.eq.{query},"
                f"title.ilike.%{query}%,"
                f"author.ilike.%{query}%,"
                f"publisher.ilike.%{query}%"
            ).execute()
            
            if response.data:
                return {'books': response.data}
            else:
                return {}
                
        except Exception as e:
            print(f"Error searching books: {e}")
            return {}
    
    def generate_comprehensive_response(self, user_message, context_data):
        """Generate AI response with comprehensive context"""
        try:
            # Build detailed context
            context = "You are a helpful library assistant with access to student and library data. "
            
            if context_data.get('student_info'):
                context += f"\nStudent Information:\n"
                for table, data in context_data['student_info'].items():
                    context += f"From {table}: {data}\n"
            
            if context_data.get('reservations'):
                context += f"\nCurrent Reservations: {context_data['reservations']}\n"
            
            if context_data.get('borrowed_books'):
                context += f"\nBorrowed Books: {context_data['borrowed_books']}\n"
            
            if context_data.get('fines'):
                context += f"\nFines/Fees: {context_data['fines']}\n"
            
            if context_data.get('book_search'):
                context += f"\nBook Search Results: {context_data['book_search']}\n"
            
            prompt = f"{context}\nUser Question: {user_message}\n\nProvide a helpful, detailed response:"
            
            response = self.genai_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"
    
    def process_query(self, user_message):
        """Process user query and gather relevant data"""
        context_data = {}
        
        # Extract potential student identifiers from message
        words = user_message.split()
        potential_ids = [word for word in words if word.isalnum() and len(word) > 2]
        
        # If user is asking about a specific student
        for identifier in potential_ids:
            student_info = self.search_student_info(identifier)
            if student_info:
                context_data['student_info'] = student_info
                
                # Get additional student data
                context_data['reservations'] = self.get_student_reservations(identifier)
                context_data['borrowed_books'] = self.get_student_books(identifier)
                context_data['fines'] = self.get_student_fines(identifier)
                break
        
        # If user is searching for books
        if any(word in user_message.lower() for word in ['book', 'author', 'title', 'search']):
            book_results = self.search_books(user_message)
            if book_results:
                context_data['book_search'] = book_results[:5]  # Limit results
        
        return context_data
    
    def chat(self):
        """Interactive chat interface"""
        print("📚 Enhanced Library ChatBot")
        print("Ask me about students, books, reservations, fines, or anything library-related!")
        print("Examples:")
        print("- 'Show me info for student ID 12345'")
        print("- 'What books does John Smith have?'")
        print("- 'Search for books about Python programming'")
        print("- 'Does student 67890 have any fines?'")
        print("\nType 'quit' to exit.\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("📚 Library ChatBot: Goodbye! Have a great day!")
                break
            
            if user_input:
                print("🔍 Searching database...")
                
                # Process query and gather context
                context_data = self.process_query(user_input)
                
                # Generate response
                response = self.generate_comprehensive_response(user_input, context_data)
                print(f"\n📚 Library ChatBot: {response}\n")

if __name__ == "__main__":
    try:
        bot = EnhancedLibraryChatBot()
        bot.chat()
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")
