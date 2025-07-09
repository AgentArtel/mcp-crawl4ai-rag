#!/usr/bin/env python3
"""
Simple Test Data Script for MCP Tool Testing

This script adds minimal test data to enable testing of MCP tools
without schema conflicts.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def main():
    """Add simple test data for MCP tool testing"""
    print("🧪 Adding Simple Test Data for MCP Tool Testing...")
    
    supabase = create_client(
        os.getenv('SUPABASE_URL'), 
        os.getenv('SUPABASE_SERVICE_KEY')
    )
    
    # Test 1: Check what tables exist
    print("\n1️⃣ Checking existing tables...")
    try:
        # Try to query each expected table to see what exists
        tables_to_check = [
            'iap_templates',
            'iap_general_education', 
            'iap_market_research',
            'iap_concentration_validation',
            'iap_course_plo_mappings'
        ]
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"   ✅ {table}: exists ({len(result.data)} sample records)")
                if result.data:
                    print(f"      Sample fields: {list(result.data[0].keys())}")
            except Exception as e:
                print(f"   ❌ {table}: {e}")
    
    except Exception as e:
        print(f"   Error checking tables: {e}")
    
    # Test 2: Try to add a simple IAP template with minimal fields
    print("\n2️⃣ Testing IAP template creation...")
    try:
        simple_template = {
            'student_name': 'Test Student',
            'student_id': 'TEST001',
            'degree_emphasis': 'Psychology and Communication',
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('iap_templates').insert(simple_template).execute()
        print(f"   ✅ Created simple IAP template: {result.data[0]['student_id']}")
        
    except Exception as e:
        print(f"   ❌ Failed to create IAP template: {e}")
    
    # Test 3: Add some general education data
    print("\n3️⃣ Testing GE data creation...")
    try:
        ge_record = {
            'student_id': 'TEST001',
            'category': 'English',
            'requirement': 'College Writing',
            'credits_required': 3,
            'credits_completed': 3,
            'status': 'completed',
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('iap_general_education').insert(ge_record).execute()
        print(f"   ✅ Created GE record for {ge_record['category']}")
        
    except Exception as e:
        print(f"   ❌ Failed to create GE record: {e}")
    
    print("\n✅ Simple test data creation complete!")

if __name__ == "__main__":
    main()
