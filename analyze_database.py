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
        
    def search_book_by_id_or_name(self, query):
        """Search for books by ID, title, author, or ISBN"""
        results = {}
        book_tables = ['books', 'catalog', 'library', 'book_inventory']
        
        for table in book_tables:
            try:
                # Search by ID, title, author, ISBN
                response = self.supabase.table(table).select('*').or_(
                    f"id.eq.{query},"
                    f"book_id.eq.{query},"
                    f"isbn.eq.{query},"
                    f"title.ilike.%{query}%,"
                    f"author.ilike.%{query}%"
                ).execute()
                
                if response.data:
                    results[table] = response.data
                    
            except Exception as e:
                continue
                
        return results
    
    def get_book_issue_info(self, book_id):
        """Get who issued the book and for how long"""
        issue_tables = ['reservations', 'loans', 'borrowed_books', 'transactions', 'issues']
        
        for table in issue_tables:
            try:
                response = self.supabase.table(table).select('*').or_(
                    f"book_id.eq.{book_id},"
                    f"isbn.eq.{book_id},"
                    f"id.eq.{book_id}"
                ).execute()
                
                if response.data:
                    return {table: response.data}
                    
            except Exception as e:
                continue
                
        return {}
    
    def get_student_info(self, student_id):
        """Get student information who issued the book"""
        student_tables = ['students', 'users', 'members', 'library_members']
        
        for table in student_tables:
            try:
                response = self.supabase.table(table).select('*').or_(
                    f"id.eq.{student_id},"
                    f"student_id.eq.{student_id},"
                    f"user_id.eq.{student_id}"
                ).execute()
                
                if response.data:
                    return response.data[0]
                    
            except Exception as e:
                continue
                
        return None
    
    def search_all_books(self, query):
        """Search all books in library"""
        book_tables = ['books', 'catalog', 'library', 'book_inventory']
        
        for table in book_tables:
            try:
                response = self.supabase.table(table).select('*').or_(
                    f"title.ilike.%{query}%,"
                    f"author.ilike.%{query}%,"
                    f"subject.ilike.%{query}%,"
                    f"category.ilike.%{query}%"
                ).execute()
                
                if response.data:
                    return response.data
                    
            except Exception as e:
                continue
                
        return []
    
    def get_book_availability(self, book_id):
        """Check if book is available or issued"""
        try:
            # Check in issue/reservation tables
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
            context = """You are a helpful library management assistant. You can provide information about:
            - Books (by ID, title, author, ISBN)
            - Who issued which book and for how long
            - Book availability status
            - Student information
            - Library catalog search
            
            Provide clear, detailed responses based on the database information."""
            
            if context_data.get('book_info'):
                context += f"\n\nBook Information Found:\n"
                for table, books in context_data['book_info'].items():
                    for book in books:
                        context += f"- {book}\n"
            
            if context_data.get('issue_info'):
                context += f"\n\nBook Issue Information:\n{context_data['issue_info']}"
            
            if context_data.get('student_info'):
                context += f"\n\nStudent Information:\n{context_data['student_info']}"
            
            if context_data.get('availability'):
                context += f"\n\nBook Availability:\n{context_data['availability']}"
            
            if context_data.get('search_results'):
                context += f"\n\nSearch Results:\n"
                for book in context_data['search_results'][:5]:  # Limit to 5 results
                    context += f"- {book}\n"
            
            prompt = f"{context}\n\nUser Question: {user_message}\n\nResponse:"
            
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
        
        # Extract potential book IDs or ISBNs (numbers)
        numbers = re.findall(r'\b\d+\b', user_message)
        
        # Extract potential book titles or author names
        words = user_message.split()
        
        # Check if user is asking about a specific book
        if numbers:
            for book_id in numbers:
                # Search for book by ID
                book_info = self.search_book_by_id_or_name(book_id)
                if book_info:
                    context_data['book_info'] = book_info
                    
                    # Get issue information
                    issue_info = self.get_book_issue_info(book_id)
                    if issue_info:
                        context_data['issue_info'] = issue_info
                        
                        # Extract student ID and get student info
                        for table, issues in issue_info.items():
                            for issue in issues:
                                student_id = issue.get('user_id') or issue.get('student_id') or issue.get('member_id')
                                if student_id:
                                    student_info = self.get_student_info(student_id)
                                    if student_info:
                                        context_data['student_info'] = student_info
                                    
                                    # Calculate days issued
                                    issue_date = issue.get('issue_date') or issue.get('created_at') or issue.get('date')
                                    return_date = issue.get('return_date') or issue.get('due_date')
                                    
                                    if issue_date:
                                        days = self.calculate_days_issued(issue_date, return_date)
                                        context_data['days_issued'] = days
                    
                    # Get availability status
                    availability = self.get_book_availability(book_id)
                    context_data['availability'] = availability
                    break
        
        # If no specific book ID, search by title/author
        if not context_data.get('book_info'):
            # Remove common words and search
            search_terms = [word for word in words if len(word) > 2 and word.lower() not in ['book', 'who', 'issued', 'the', 'and', 'for', 'how', 'long']]
            
            if search_terms:
                search_query = ' '.join(search_terms)
                search_results = self.search_all_books(search_query)
                if search_results:
                    context_data['search_results'] = search_results
        
        return context_data
    
    def chat(self):
        """Interactive chat interface"""
        print("\n📚 Library Management ChatBot")
        print("=" * 50)
        print("I can help you with:")
        print("✅ Find book information by ID, title, or author")
        print("✅ Check who issued a specific book")
        print("✅ See how long a book has been issued")
        print("✅ Check book availability status")
        print("✅ Search library catalog")
        print("\nExamples:")
        print("- 'Show info for book ID 12345'")
        print("- 'Who issued Harry Potter book?'")
        print("- 'Is book 67890 available?'")
        print("- 'Search for Python programming books'")
        print("- 'Book issued by student 123 for how long?'")
        print("\nType 'quit' to exit.\n")
        
        while True:
            user_input = input("🔍 Ask me: ").strip()
            
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
                print("-" * 50)

if __name__ == "__main__":
    try:
        bot = LibraryManagementChatBot()
        bot.chat()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("Please check your .env file and internet connection.")