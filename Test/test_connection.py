import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Test Supabase connection and discover existing tables
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"Connecting to: {supabase_url}")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Test connection first
    print("✅ Successfully connected to Supabase!")
    
    # Check for books table specifically
    print("\n🔍 Checking for 'books' table...")
    try:
        books_response = supabase.table('books').select('*').limit(3).execute()
        print("✅ Books table found!")
        print(f"📚 Found {len(books_response.data)} books (showing first 3):")
        for book in books_response.data:
            print(f"   - {book.get('title', 'N/A')} by {book.get('author', 'N/A')}")
        if books_response.data:
            print(f"📋 Books table columns: {list(books_response.data[0].keys())}")
    except Exception as books_error:
        print(f"❌ Books table error: {books_error}")
    
    # Check reservations table
    print("\n🔍 Checking 'reservations' table...")
    try:
        response = supabase.table('reservations').select('*').limit(3).execute()
        print("✅ Reservations table found!")
        print(f"Reservations table data: {response.data}")
        if response.data:
            print(f"📋 Reservations table columns: {list(response.data[0].keys())}")
    except Exception as res_error:
        print(f"❌ Reservations table error: {res_error}")
    
    # Check other common library tables
    print("\n🔍 Checking for other common library tables...")
    tables_to_check = {
        'members': 'Member information',
        'transactions': 'Transaction records', 
        'staff': 'Staff information',
        'reservations': 'Book reservations'
    }
    
    for table, description in tables_to_check.items():
        try:
            test_response = supabase.table(table).select('*').limit(3).execute()
            print(f"✅ Found table: {table} ({description})")
            if test_response.data:
                print(f"   📊 Sample data: {test_response.data[0]}")
                print(f"   📋 Columns: {list(test_response.data[0].keys())}")
            else:
                print(f"   📊 Table exists but is empty")
            print()
        except Exception as e:
            if "PGRST205" in str(e):
                print(f"❌ Table '{table}' not found")
            else:
                print(f"⚠️  Error accessing '{table}': {e}")
                print()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")