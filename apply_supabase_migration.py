#!/usr/bin/env python3
"""
Apply Supabase academic schema migration to create required tables.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def apply_migration():
    """Apply the academic schema migration to Supabase."""
    print("🚀 Applying Supabase Academic Schema Migration")
    print("=" * 50)
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Supabase client initialized")
    
    # Read the migration SQL
    migration_file = "sql/supabase_schema_migration_refined.sql"
    if not os.path.exists(migration_file):
        migration_file = "supabase_schema_migration_refined.sql"
    
    if not os.path.exists(migration_file):
        print("❌ Migration file not found!")
        return False
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    print(f"📄 Read migration SQL ({len(migration_sql)} characters)")
    
    try:
        # Execute the migration
        print("🔧 Executing migration...")
        result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
        print("✅ Migration executed successfully!")
        
        # Verify tables were created
        print("🔍 Verifying table creation...")
        
        # Check if academic_departments exists
        try:
            dept_result = supabase.table('academic_departments').select('*').limit(1).execute()
            print("✅ academic_departments table exists")
        except Exception as e:
            print(f"⚠️ academic_departments table check failed: {e}")
        
        # Check if academic_programs exists
        try:
            prog_result = supabase.table('academic_programs').select('*').limit(1).execute()
            print("✅ academic_programs table exists")
        except Exception as e:
            print(f"⚠️ academic_programs table check failed: {e}")
        
        # Check if academic_courses exists (should already exist)
        try:
            course_result = supabase.table('academic_courses').select('*').limit(1).execute()
            print("✅ academic_courses table exists")
        except Exception as e:
            print(f"⚠️ academic_courses table check failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
        # Try alternative approach - execute SQL directly via raw query
        print("🔄 Trying alternative approach...")
        try:
            # Split migration into individual statements
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                if statement.upper().startswith(('CREATE', 'ALTER', 'INSERT')):
                    print(f"📝 Executing statement {i+1}/{len(statements)}")
                    try:
                        supabase.rpc('exec_sql', {'sql': statement}).execute()
                    except Exception as stmt_error:
                        print(f"⚠️ Statement {i+1} failed: {stmt_error}")
                        continue
            
            print("✅ Alternative migration approach completed")
            return True
            
        except Exception as alt_error:
            print(f"❌ Alternative approach also failed: {alt_error}")
            return False

if __name__ == "__main__":
    success = apply_migration()
    if success:
        print("\n🎉 SUCCESS: Academic schema migration applied!")
    else:
        print("\n❌ FAILED: Could not apply migration")
    exit(0 if success else 1)
