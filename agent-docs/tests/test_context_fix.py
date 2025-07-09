#!/usr/bin/env python3
"""
Test script to verify the robust Supabase context access fix works locally.
This tests the IAP functions with the new context helper.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import the context helper and IAP tools
from crawl4ai_mcp import get_supabase_from_context
from iap_tools import IAPManager

class MockContext:
    """Mock context for testing different context structures"""
    def __init__(self, context_type="standard"):
        self.context_type = context_type
        
        if context_type == "standard":
            # Standard FastMCP context structure
            self.request_context = MockRequestContext()
        elif context_type == "direct":
            # Direct supabase_client access
            from utils import get_supabase_client
            self.supabase_client = get_supabase_client()
        elif context_type == "lifespan_direct":
            # Lifespan context directly on ctx
            from utils import get_supabase_client
            self.lifespan_context = MockLifespanContext()

class MockRequestContext:
    def __init__(self):
        self.lifespan_context = MockLifespanContext()

class MockLifespanContext:
    def __init__(self):
        from utils import get_supabase_client
        self.supabase_client = get_supabase_client()

async def test_context_access():
    """Test the robust context access helper with different context structures"""
    print("🧪 Testing Robust Supabase Context Access Helper")
    print("=" * 60)
    
    # Test different context structures
    context_types = ["standard", "direct", "lifespan_direct"]
    
    for context_type in context_types:
        print(f"\n📋 Testing {context_type} context structure...")
        
        try:
            # Create mock context
            mock_ctx = MockContext(context_type)
            
            # Test context access
            supabase_client = get_supabase_from_context(mock_ctx)
            
            if supabase_client:
                print(f"✅ Successfully accessed Supabase client from {context_type} context")
                print(f"   Client type: {type(supabase_client)}")
                
                # Test basic Supabase operation
                try:
                    result = supabase_client.from_('sources').select('*').limit(1).execute()
                    print(f"✅ Supabase connection test passed - found {len(result.data)} records")
                except Exception as e:
                    print(f"⚠️  Supabase connection test failed: {str(e)}")
                    
            else:
                print(f"❌ Failed to access Supabase client from {context_type} context")
                
        except Exception as e:
            print(f"❌ Error testing {context_type} context: {str(e)}")

async def test_iap_manager():
    """Test IAP Manager with the robust context access"""
    print(f"\n🎯 Testing IAP Manager with Robust Context Access")
    print("=" * 60)
    
    try:
        # Create mock context
        mock_ctx = MockContext("standard")
        
        # Get Supabase client using our robust helper
        supabase_client = get_supabase_from_context(mock_ctx)
        
        # Create IAP Manager
        iap_manager = IAPManager(supabase_client)
        
        print("✅ Successfully created IAP Manager with robust context access")
        
        # Test a simple IAP operation (create template)
        result = await iap_manager.create_iap_template(
            student_name="Test Student",
            student_id="TEST123",
            degree_emphasis="Psychology and Data Science",
            student_email="test@utahtech.edu"
        )
        
        if result.get('success'):
            print("✅ IAP template creation test passed")
            print(f"   Template ID: {result.get('template_id', 'N/A')}")
        else:
            print(f"⚠️  IAP template creation test failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing IAP Manager: {str(e)}")

async def main():
    """Main test function"""
    print("🚀 Starting Local Context Fix Tests")
    print("=" * 60)
    
    # Test context access
    await test_context_access()
    
    # Test IAP manager
    await test_iap_manager()
    
    print(f"\n🎉 Context Fix Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
