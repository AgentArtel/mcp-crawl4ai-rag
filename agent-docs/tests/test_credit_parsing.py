#!/usr/bin/env python3
"""
Test script to verify the improved credit parsing logic works correctly.
This tests the calculate_credits function with various course scenarios.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import the context helper and credit calculation tool
from crawl4ai_mcp import get_supabase_from_context, calculate_credits

class MockContext:
    """Mock context for testing"""
    def __init__(self):
        # Standard FastMCP context structure
        self.request_context = MockRequestContext()

class MockRequestContext:
    def __init__(self):
        self.lifespan_context = MockLifespanContext()

class MockLifespanContext:
    def __init__(self):
        from utils import get_supabase_client
        self.supabase_client = get_supabase_client()

async def test_credit_parsing():
    """Test the improved credit parsing logic"""
    print("🧪 Testing Improved Credit Parsing Logic")
    print("=" * 60)
    
    # Test courses with different credit scenarios
    test_cases = [
        {
            "name": "Standard Psychology Courses",
            "courses": "PSYC 1010, PSYC 2010, PSYC 3010",
            "expected_behavior": "Should find credit information for psychology courses"
        },
        {
            "name": "Mixed Level Courses", 
            "courses": "BIOL 1010, BIOL 3450, MATH 1050, MATH 3000",
            "expected_behavior": "Should classify upper/lower division correctly"
        },
        {
            "name": "Engineering Courses",
            "courses": "ENGR 1000, ENGR 2010, ENGR 4000",
            "expected_behavior": "Should handle 3-4 digit course numbers"
        },
        {
            "name": "Single Course Test",
            "courses": "HIST 1700",
            "expected_behavior": "Should handle single course correctly"
        }
    ]
    
    # Create mock context
    mock_ctx = MockContext()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"   Courses: {test_case['courses']}")
        print(f"   Expected: {test_case['expected_behavior']}")
        
        try:
            # Test the credit calculation
            result_json = await calculate_credits(
                ctx=mock_ctx,
                course_list=test_case['courses'],
                source_id='catalog.utahtech.edu'
            )
            
            result = json.loads(result_json)
            
            if result.get('success'):
                analysis = result.get('analysis', {})
                print(f"✅ Success!")
                print(f"   Total Courses: {analysis.get('total_courses', 0)}")
                print(f"   Total Credits: {analysis.get('total_credits', 0)}")
                print(f"   Upper Division: {analysis.get('upper_division_credits', 0)}")
                print(f"   Lower Division: {analysis.get('lower_division_credits', 0)}")
                
                # Show course breakdown
                course_breakdown = analysis.get('course_breakdown', [])
                for course_info in course_breakdown:
                    print(f"     - {course_info.get('course_code')}: {course_info.get('credits')} credits ({course_info.get('level')})")
                    
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def test_regex_patterns():
    """Test the regex patterns directly"""
    print(f"\n🔍 Testing Credit Extraction Regex Patterns")
    print("=" * 60)
    
    import re
    
    # Test content samples
    test_content = [
        "PSYC 1010 - General Psychology (3 credit hours) - An introduction to psychology",
        "BIOL 3450 - Genetics (4 credits) - Advanced study of genetics",
        "MATH 1050 - College Algebra. 4 cr. Prerequisite: MATH 1010",
        "ENGR 2010 - Engineering Statics (3 units) - Study of forces",
        "HIST 1700 - American History 3 hrs - Survey of American history",
        "Invalid content with 15 credit hours mentioned but not for a course",
        "CHEM 1210 - General Chemistry I (4 credit hours) Laboratory included"
    ]
    
    # Current patterns from the actual function
    credit_patterns = [
        r'\((\d+)\s*credit\s*hours?\)',  # (3 credit hours)
        r'\((\d+)\s*credits?\)',         # (4 credits)
        r'(?:^|\s)(\d+)\s*credit\s*hours?(?:\s|$|\.|,)',
        r'(?:^|\s)(\d+)\s*credits?(?:\s|$|\.|,)',
        r'(?:^|\s)(\d+)\s*cr\.?(?:\s|$|\.|,)',
        r'\((\d+)\s*units?\)',           # (3 units)
        r'(?:^|\s)(\d+)\s*units?(?:\s|$|\.|,)',
        r'(?:^|\s)(\d+)\s*hrs?(?:\s|$|\.|,)'
    ]
    
    for i, content in enumerate(test_content, 1):
        print(f"\n📝 Test Content {i}: {content[:50]}...")
        
        credits_found = None
        for pattern in credit_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    # Filter out unrealistic credit values (1-6 credits typical)
                    potential_credits = [int(m) for m in matches if 1 <= int(m) <= 6]
                    if potential_credits:
                        credits_found = potential_credits[0]
                        print(f"   ✅ Found {credits_found} credits using pattern: {pattern}")
                        break
                except ValueError:
                    continue
        
        if not credits_found:
            print(f"   ⚠️  No valid credits found")

async def main():
    """Main test function"""
    print("🚀 Starting Credit Parsing Fix Tests")
    print("=" * 60)
    
    # Test regex patterns directly
    await test_regex_patterns()
    
    # Test full credit calculation
    await test_credit_parsing()
    
    print(f"\n🎉 Credit Parsing Fix Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
