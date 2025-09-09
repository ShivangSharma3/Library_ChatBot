import os
from dotenv import load_dotenv
from supabase import create_client

def analyze_complete_database():
    """
    Complete database analysis tool that extracts detailed information
    about all tables, columns, data types, and sample data
    """
    load_dotenv()
    
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_KEY")
        )
        
        print("=" * 80)
        print("COMPREHENSIVE DATABASE ANALYSIS")
        print("=" * 80)
        
        # Known tables from previous analysis
        tables_to_analyze = ['books', 'members', 'staff', 'reservations', 'transactions']
        
        database_info = {}
        
        for table_name in tables_to_analyze:
            print(f"\n📊 ANALYZING TABLE: {table_name.upper()}")
            print("-" * 50)
            
            try:
                # Get sample data (more records for better analysis)
                response = supabase.table(table_name).select('*').limit(5).execute()
                
                table_info = {
                    'name': table_name,
                    'total_sample_records': len(response.data),
                    'columns': [],
                    'sample_data': response.data
                }
                
                if response.data:
                    # Analyze columns and data types
                    sample_record = response.data[0]
                    
                    print(f"✅ Found {len(response.data)} sample records")
                    print(f"📋 Columns ({len(sample_record)} total):")
                    
                    for i, (column, value) in enumerate(sample_record.items(), 1):
                        # Determine data type from sample value
                        value_type = type(value).__name__
                        if value is None:
                            value_type = "NULL"
                        elif isinstance(value, str):
                            if len(value) == 36 and '-' in value:  # UUID pattern
                                value_type = "UUID"
                            elif '@' in value:
                                value_type = "EMAIL"
                            elif value.count('-') == 2 and len(value) == 10:  # Date pattern
                                value_type = "DATE"
                            else:
                                value_type = "TEXT/VARCHAR"
                        elif isinstance(value, (int, float)):
                            value_type = "NUMERIC"
                        
                        column_info = {
                            'name': column,
                            'data_type': value_type,
                            'sample_value': str(value)[:50] + "..." if len(str(value)) > 50 else str(value),
                            'is_likely_primary_key': column.endswith('_id') and i == 1,
                            'is_likely_foreign_key': column.endswith('_id') and i != 1
                        }
                        
                        table_info['columns'].append(column_info)
                        
                        key_indicator = ""
                        if column_info['is_likely_primary_key']:
                            key_indicator = " [PRIMARY KEY]"
                        elif column_info['is_likely_foreign_key']:
                            key_indicator = " [FOREIGN KEY]"
                        
                        print(f"   {i:2d}. {column:20} | {value_type:15} | {column_info['sample_value']:30}{key_indicator}")
                    
                    # Show sample records
                    print(f"\n📄 Sample Records:")
                    for i, record in enumerate(response.data[:3], 1):
                        print(f"   Record {i}: {record}")
                    
                    if len(response.data) > 3:
                        print(f"   ... and {len(response.data) - 3} more records")
                
                else:
                    print("❌ No data found in this table")
                    table_info['columns'] = []
                    table_info['sample_data'] = []
                
                database_info[table_name] = table_info
                
            except Exception as e:
                print(f"❌ Error analyzing table {table_name}: {e}")
                database_info[table_name] = {'error': str(e)}
        
        # Generate relationships analysis
        print(f"\n🔗 RELATIONSHIP ANALYSIS")
        print("-" * 50)
        
        foreign_keys = []
        for table_name, table_info in database_info.items():
            if 'columns' in table_info:
                for column in table_info['columns']:
                    if column['is_likely_foreign_key']:
                        # Try to determine target table
                        fk_table = column['name'].replace('_id', '') + 's'
                        if column['name'].replace('_id', '') + 's' in database_info:
                            foreign_keys.append({
                                'source_table': table_name,
                                'source_column': column['name'],
                                'target_table': fk_table,
                                'target_column': column['name']
                            })
        
        for fk in foreign_keys:
            print(f"   {fk['source_table']}.{fk['source_column']} → {fk['target_table']}.{fk['target_column']}")
        
        # Summary statistics
        print(f"\n📈 DATABASE SUMMARY")
        print("-" * 50)
        print(f"Total Tables Analyzed: {len(database_info)}")
        
        total_columns = sum(len(info.get('columns', [])) for info in database_info.values())
        print(f"Total Columns: {total_columns}")
        
        total_sample_records = sum(info.get('total_sample_records', 0) for info in database_info.values())
        print(f"Total Sample Records: {total_sample_records}")
        
        print(f"Identified Foreign Key Relationships: {len(foreign_keys)}")
        
        print("\nAnalysis complete! ✅")
        
        return database_info
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return {}

if __name__ == "__main__":
    database_structure = analyze_complete_database()
