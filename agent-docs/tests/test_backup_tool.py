#!/usr/bin/env python3
"""
Test script to verify the backup tool logic before Docker rebuild
"""

import sys
import os
sys.path.append('src')

from academic_graph_builder import AcademicGraphBuilder

def test_backup_tool_methods():
    """Test that the backup tool can access the required methods"""
    print("🧪 Testing backup tool method access...")
    
    try:
        # Initialize the builder
        builder = AcademicGraphBuilder()
        print("✅ AcademicGraphBuilder initialized successfully")
        
        # Check if the method exists
        if hasattr(builder, '_extract_academic_data'):
            print("✅ _extract_academic_data method exists")
        else:
            print("❌ _extract_academic_data method NOT found")
            return False
            
        # Check if the method is callable
        if callable(getattr(builder, '_extract_academic_data')):
            print("✅ _extract_academic_data method is callable")
        else:
            print("❌ _extract_academic_data method is not callable")
            return False
            
        # Check other required methods
        required_methods = ['_populate_supabase_tables']
        for method_name in required_methods:
            if hasattr(builder, method_name):
                print(f"✅ {method_name} method exists")
            else:
                print(f"❌ {method_name} method NOT found")
                return False
        
        builder.close()
        print("✅ All required methods are available")
        return True
        
    except Exception as e:
        print(f"❌ Error testing backup tool: {e}")
        return False

if __name__ == "__main__":
    success = test_backup_tool_methods()
    if success:
        print("\n🎉 Backup tool method access test PASSED")
        print("✅ Ready for Docker rebuild")
    else:
        print("\n💥 Backup tool method access test FAILED")
        print("❌ Fix issues before Docker rebuild")
    
    sys.exit(0 if success else 1)
