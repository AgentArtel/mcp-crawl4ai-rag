#!/usr/bin/env python3
"""
Debug script to test and perfect the credit parsing regex patterns.
"""

import re

def test_regex_patterns():
    """Test regex patterns against real content"""
    
    # Test content samples that should work
    test_content = [
        "PSYC 1010 - General Psychology (3 credit hours) - An introduction to psychology",
        "BIOL 3450 - Genetics (4 credits) - Advanced study of genetics", 
        "MATH 1050 - College Algebra. 4 cr. Prerequisite: MATH 1010",
        "ENGR 2010 - Engineering Statics (3 units) - Study of forces",
        "HIST 1700 - American History 3 hrs - Survey of American history",
        "CHEM 1210 - General Chemistry I (4 credit hours) Laboratory included",
        "CS 1400 - Introduction to Programming (3 credits) with lab",
        "PHYS 2210 - Physics I. 4 credit hours. Calculus-based physics"
    ]
    
    # Current patterns from the code
    current_patterns = [
        r'\((\d+)\s*credit\s*hours?\)',  # (3 credit hours)
        r'\((\d+)\s*credits?\)',         # (4 credits)
        r'(?:^|\s)(\d+)\s*credit\s*hours?(?:\s|$|\.|,)',
        r'(?:^|\s)(\d+)\s*credits?(?:\s|$|\.|,)',
        r'(?:^|\s)(\d+)\s*cr\.?(?:\s|$|\.|,)',
        r'\((\d+)\s*units?\)',           # (3 units)
        r'(?:^|\s)(\d+)\s*units?(?:\s|$|\.|,)',
        r'(?:^|\s)(\d+)\s*hrs?(?:\s|$|\.|,)'
    ]
    
    print("🔍 Testing Current Regex Patterns")
    print("=" * 60)
    
    for i, content in enumerate(test_content, 1):
        print(f"\n📝 Test {i}: {content}")
        
        found_credits = None
        matched_pattern = None
        
        for j, pattern in enumerate(current_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    potential_credits = [int(m) for m in matches if 1 <= int(m) <= 6]
                    if potential_credits:
                        found_credits = potential_credits[0]
                        matched_pattern = f"Pattern {j+1}: {pattern}"
                        break
                except ValueError:
                    continue
        
        if found_credits:
            print(f"   ✅ Found {found_credits} credits using {matched_pattern}")
        else:
            print(f"   ❌ No credits found")
            # Let's test each pattern individually
            for j, pattern in enumerate(current_patterns):
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"      Pattern {j+1} matched: {matches} but failed validation")

def test_improved_patterns():
    """Test improved regex patterns"""
    
    # Test content samples
    test_content = [
        "PSYC 1010 - General Psychology (3 credit hours) - An introduction to psychology",
        "BIOL 3450 - Genetics (4 credits) - Advanced study of genetics", 
        "MATH 1050 - College Algebra. 4 cr. Prerequisite: MATH 1010",
        "ENGR 2010 - Engineering Statics (3 units) - Study of forces",
        "HIST 1700 - American History 3 hrs - Survey of American history",
        "CHEM 1210 - General Chemistry I (4 credit hours) Laboratory included",
        "CS 1400 - Introduction to Programming (3 credits) with lab",
        "PHYS 2210 - Physics I. 4 credit hours. Calculus-based physics"
    ]
    
    # Improved patterns - more comprehensive and specific
    improved_patterns = [
        r'\((\d+)\s+credit\s+hours?\)',      # (3 credit hours) - exact spacing
        r'\((\d+)\s+credits?\)',             # (4 credits) - exact spacing  
        r'(\d+)\s+credit\s+hours?',          # 4 credit hours (no parens)
        r'(\d+)\s+credits?(?:\s|$|\.|,)',    # 3 credits (with boundaries)
        r'(\d+)\s+cr\.(?:\s|$|\.|,)',        # 4 cr. (with boundaries)
        r'\((\d+)\s+units?\)',               # (3 units) - exact spacing
        r'(\d+)\s+units?(?:\s|$|\.|,)',      # 3 units (with boundaries)
        r'(\d+)\s+hrs?(?:\s|$|\.|,)'         # 3 hrs (with boundaries)
    ]
    
    print(f"\n🚀 Testing Improved Regex Patterns")
    print("=" * 60)
    
    for i, content in enumerate(test_content, 1):
        print(f"\n📝 Test {i}: {content}")
        
        found_credits = None
        matched_pattern = None
        
        for j, pattern in enumerate(improved_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    potential_credits = [int(m) for m in matches if 1 <= int(m) <= 6]
                    if potential_credits:
                        found_credits = potential_credits[0]
                        matched_pattern = f"Improved Pattern {j+1}: {pattern}"
                        break
                except ValueError:
                    continue
        
        if found_credits:
            print(f"   ✅ Found {found_credits} credits using {matched_pattern}")
        else:
            print(f"   ❌ Still no credits found")

if __name__ == "__main__":
    test_regex_patterns()
    test_improved_patterns()
