#!/usr/bin/env python3
"""
Debug MCP Context Structure

This script adds a debug tool to understand the actual MCP context structure.
"""

def add_debug_tool():
    """Add a debug tool to the MCP server to inspect context structure"""
    
    debug_tool_code = '''
@mcp.tool()
async def debug_context_structure(ctx: Context) -> str:
    """
    Debug tool to inspect the MCP context structure.
    This helps understand how to properly access the supabase_client.
    """
    try:
        context_info = {
            "context_type": str(type(ctx)),
            "context_attributes": dir(ctx),
            "has_request_context": hasattr(ctx, 'request_context'),
            "has_supabase_client": hasattr(ctx, 'supabase_client'),
        }
        
        if hasattr(ctx, 'request_context'):
            context_info["request_context_type"] = str(type(ctx.request_context))
            context_info["request_context_attributes"] = dir(ctx.request_context)
            
            if hasattr(ctx.request_context, 'lifespan_context'):
                context_info["has_lifespan_context"] = True
                context_info["lifespan_context_type"] = str(type(ctx.request_context.lifespan_context))
                context_info["lifespan_context_attributes"] = dir(ctx.request_context.lifespan_context)
                context_info["has_supabase_in_lifespan"] = hasattr(ctx.request_context.lifespan_context, 'supabase_client')
            else:
                context_info["has_lifespan_context"] = False
        
        return json.dumps(context_info, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to debug context: {str(e)}",
            "context_type": str(type(ctx)) if ctx else "None"
        }, indent=2)
'''
    
    # Read the MCP server file
    file_path = "/Users/artelio/Documents/ARTELIO/MCP-Servers/utah-tech-mcp-advisor/src/crawl4ai_mcp.py"
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find a good place to insert the debug tool (after imports, before other tools)
    import_end = content.find('@mcp.tool()')
    if import_end == -1:
        print("❌ Could not find insertion point for debug tool")
        return False
    
    # Insert the debug tool
    new_content = content[:import_end] + debug_tool_code + '\n\n' + content[import_end:]
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Debug tool added to MCP server")
    return True

if __name__ == "__main__":
    success = add_debug_tool()
    if success:
        print("🔍 Debug tool added successfully!")
        print("🚀 You can now call debug_context_structure to inspect the MCP context")
    else:
        print("❌ Failed to add debug tool")
    
    exit(0 if success else 1)
