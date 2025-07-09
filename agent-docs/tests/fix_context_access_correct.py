#!/usr/bin/env python3
"""
Fix Context Access in MCP Server - Correct Version

This script fixes all instances of context access patterns to use the correct
FastMCP framework structure: ctx.request_context.lifespan_context.supabase_client
"""

import re

def fix_context_access():
    """Fix all context access patterns in the MCP server"""
    file_path = "/Users/artelio/Documents/ARTELIO/MCP-Servers/utah-tech-mcp-advisor/src/crawl4ai_mcp.py"
    
    print("🔧 Fixing context access patterns in MCP server...")
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Count current occurrences
    incorrect_count = content.count('ctx.supabase_client')
    print(f"   Found {incorrect_count} instances to fix")
    
    # Replace the incorrect pattern with the correct one
    fixed_content = content.replace(
        'ctx.supabase_client',
        'ctx.request_context.lifespan_context.supabase_client'
    )
    
    # Verify the replacement worked
    remaining_count = fixed_content.count('ctx.supabase_client')
    new_count = fixed_content.count('ctx.request_context.lifespan_context.supabase_client')
    
    if remaining_count == 0:
        print(f"   ✅ Successfully fixed all {incorrect_count} instances")
        print(f"   ✅ Now using correct pattern 'ctx.request_context.lifespan_context.supabase_client' in {new_count} places")
        
        # Write the fixed content back
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        print("   ✅ File updated successfully!")
        return True
    else:
        print(f"   ❌ Still have {remaining_count} unfixed instances")
        return False

if __name__ == "__main__":
    success = fix_context_access()
    if success:
        print("\n🎉 Context access patterns fixed successfully!")
        print("🚀 MCP tools should now work correctly with test data!")
    else:
        print("\n❌ Failed to fix all context access patterns")
    
    exit(0 if success else 1)
