#!/usr/bin/env python3
"""
Test IAP Tools Locally

This script tests the IAP tools directly without going through the MCP framework
to verify they work with our realistic test data.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from iap_tools import IAPManager
from utils import get_supabase_client

async def test_iap_tools():
    """Test IAP tools with realistic test data"""
    print("🧪 Testing IAP Tools Locally...")
    
    # Initialize Supabase client
    try:
        supabase_client = get_supabase_client()
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        return False
    
    # Initialize IAP Manager
    try:
        iap_manager = IAPManager(supabase_client)
        print("✅ IAP Manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize IAP Manager: {e}")
        return False
    
    # Test 1: Create IAP Template
    print("\n📝 Test 1: Creating IAP Template...")
    try:
        result = await iap_manager.create_iap_template(
            student_name="Sarah Johnson",
            student_id="SJ2024001", 
            degree_emphasis="Psychology and Communication",
            student_email="sarah.johnson@utahtech.edu",
            student_phone="555-0123"
        )
        print("✅ IAP Template created successfully")
        print(f"   Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Failed to create IAP template: {e}")
        return False
    
    # Test 2: Update IAP Section
    print("\n📝 Test 2: Updating IAP Section...")
    try:
        mission_data = {
            "mission_statement": "To integrate psychological principles with effective communication strategies to create meaningful impact in mental health advocacy and community outreach."
        }
        result = await iap_manager.update_iap_section(
            student_id="SJ2024001",
            section="mission_statement",
            data=mission_data
        )
        print("✅ IAP Section updated successfully")
        print(f"   Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Failed to update IAP section: {e}")
        return False
    
    # Test 3: Generate IAP Suggestions
    print("\n📝 Test 3: Generating IAP Suggestions...")
    try:
        result = await iap_manager.generate_iap_suggestions(
            degree_emphasis="Psychology and Communication",
            section="program_goals",
            context={"student_interests": "mental health, community outreach"}
        )
        print("✅ IAP Suggestions generated successfully")
        print(f"   Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Failed to generate IAP suggestions: {e}")
        return False
    
    # Test 4: Validate Complete IAP
    print("\n📝 Test 4: Validating Complete IAP...")
    try:
        # Create a sample IAP data structure
        sample_iap = {
            "student_id": "SJ2024001",
            "student_name": "Sarah Johnson",
            "degree_emphasis": "Psychology and Communication",
            "mission_statement": "To integrate psychological principles with effective communication strategies",
            "program_goals": [
                "Develop expertise in psychological assessment and intervention",
                "Master effective communication strategies for diverse populations"
            ],
            "concentration_areas": ["Psychology", "Communication", "Social Work"],
            "course_mappings": {
                "Psychology": ["PSYC 1010", "PSYC 3400", "PSYC 4600"],
                "Communication": ["COMM 1020", "COMM 3050", "COMM 4200"],
                "Social Work": ["SW 2010", "SW 3300", "SW 4100"]
            }
        }
        
        result = await iap_manager.validate_iap_requirements(sample_iap)
        print("✅ IAP Validation completed successfully")
        print(f"   Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Failed to validate IAP: {e}")
        return False
    
    # Test 5: Conduct Market Research
    print("\n📝 Test 5: Conducting Market Research...")
    try:
        result = await iap_manager.conduct_market_research(
            degree_emphasis="Psychology and Communication",
            geographic_focus="Utah"
        )
        print("✅ Market Research completed successfully")
        print(f"   Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Failed to conduct market research: {e}")
        return False
    
    print("\n🎉 All IAP tools tested successfully!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_iap_tools())
    if success:
        print("\n✅ IAP tools are working correctly with test data!")
        print("🚀 Ready to test through MCP framework!")
    else:
        print("\n❌ IAP tools have issues that need to be fixed")
    
    exit(0 if success else 1)
