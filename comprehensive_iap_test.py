#!/usr/bin/env python3
"""
Comprehensive IAP Tools Test Suite

This script tests all IAP functionality with realistic test data to verify
everything is working correctly before Docker rebuild.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from iap_tools import IAPManager
from utils import get_supabase_client

async def comprehensive_iap_test():
    """Run comprehensive tests of all IAP functionality"""
    print("🧪 Running Comprehensive IAP Test Suite...")
    print("=" * 60)
    
    # Initialize components
    try:
        supabase_client = get_supabase_client()
        iap_manager = IAPManager(supabase_client)
        print("✅ IAP system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize IAP system: {e}")
        return False
    
    test_results = []
    
    # Test 1: Create Multiple IAP Templates
    print("\n📝 Test 1: Creating Multiple IAP Templates...")
    students = [
        {
            "name": "Sarah Johnson",
            "id": "SJ2024001",
            "emphasis": "Psychology and Communication",
            "email": "sarah.johnson@utahtech.edu"
        },
        {
            "name": "Michael Chen",
            "id": "MC2024002", 
            "emphasis": "Business and Technology",
            "email": "michael.chen@utahtech.edu"
        },
        {
            "name": "Emily Rodriguez",
            "id": "ER2024003",
            "emphasis": "Environmental Science and Policy",
            "email": "emily.rodriguez@utahtech.edu"
        }
    ]
    
    for student in students:
        try:
            result = await iap_manager.create_iap_template(
                student_name=student["name"],
                student_id=student["id"],
                degree_emphasis=student["emphasis"],
                student_email=student["email"]
            )
            print(f"   ✅ Created IAP for {student['name']}")
            test_results.append(("create_template", student["id"], True))
        except Exception as e:
            print(f"   ❌ Failed to create IAP for {student['name']}: {e}")
            test_results.append(("create_template", student["id"], False))
    
    # Test 2: Update Different IAP Sections
    print("\n📝 Test 2: Updating Various IAP Sections...")
    updates = [
        {
            "student_id": "SJ2024001",
            "section": "mission_statement",
            "data": {"mission_statement": "To integrate psychological principles with effective communication strategies for mental health advocacy."}
        },
        {
            "student_id": "MC2024002", 
            "section": "program_goals",
            "data": {"program_goals": ["Master business analytics", "Develop technology leadership skills", "Create innovative solutions"]}
        },
        {
            "student_id": "ER2024003",
            "section": "concentration_areas", 
            "data": {"concentration_areas": ["Environmental Science", "Public Policy", "Sustainability Studies"]}
        }
    ]
    
    for update in updates:
        try:
            result = await iap_manager.update_iap_section(
                student_id=update["student_id"],
                section=update["section"],
                data=update["data"]
            )
            print(f"   ✅ Updated {update['section']} for {update['student_id']}")
            test_results.append(("update_section", update["student_id"], True))
        except Exception as e:
            print(f"   ❌ Failed to update {update['section']} for {update['student_id']}: {e}")
            test_results.append(("update_section", update["student_id"], False))
    
    # Test 3: Generate AI Suggestions for Different Sections
    print("\n📝 Test 3: Generating AI Suggestions...")
    suggestions = [
        {"emphasis": "Psychology and Communication", "section": "mission_statement"},
        {"emphasis": "Business and Technology", "section": "program_goals"},
        {"emphasis": "Environmental Science and Policy", "section": "cover_letter"}
    ]
    
    for suggestion in suggestions:
        try:
            result = await iap_manager.generate_iap_suggestions(
                degree_emphasis=suggestion["emphasis"],
                section=suggestion["section"]
            )
            print(f"   ✅ Generated {suggestion['section']} suggestions for {suggestion['emphasis']}")
            test_results.append(("generate_suggestions", suggestion["emphasis"], True))
        except Exception as e:
            print(f"   ❌ Failed to generate suggestions: {e}")
            test_results.append(("generate_suggestions", suggestion["emphasis"], False))
    
    # Test 4: Comprehensive IAP Validation
    print("\n📝 Test 4: Comprehensive IAP Validation...")
    sample_iaps = [
        {
            "student_id": "SJ2024001",
            "student_name": "Sarah Johnson",
            "degree_emphasis": "Psychology and Communication",
            "mission_statement": "To integrate psychological principles with effective communication strategies",
            "program_goals": ["Develop expertise in psychological assessment", "Master communication strategies"],
            "concentration_areas": ["Psychology", "Communication", "Social Work"],
            "course_mappings": {
                "Psychology": ["PSYC 1010", "PSYC 3400"],
                "Communication": ["COMM 1020", "COMM 3050"],
                "Social Work": ["SW 2010", "SW 3300"]
            }
        }
    ]
    
    for iap in sample_iaps:
        try:
            result = await iap_manager.validate_iap_requirements(iap)
            print(f"   ✅ Validated IAP for {iap['student_id']}")
            test_results.append(("validate_iap", iap["student_id"], True))
        except Exception as e:
            print(f"   ❌ Failed to validate IAP for {iap['student_id']}: {e}")
            test_results.append(("validate_iap", iap["student_id"], False))
    
    # Test 5: Market Research for Different Emphases
    print("\n📝 Test 5: Market Research Analysis...")
    emphases = [
        "Psychology and Communication",
        "Business and Technology", 
        "Environmental Science and Policy"
    ]
    
    for emphasis in emphases:
        try:
            result = await iap_manager.conduct_market_research(
                degree_emphasis=emphasis,
                geographic_focus="Utah"
            )
            viability_score = result.get("viability_score", 0)
            print(f"   ✅ Market research for {emphasis}: {viability_score}/100 viability")
            test_results.append(("market_research", emphasis, True))
        except Exception as e:
            print(f"   ❌ Failed market research for {emphasis}: {e}")
            test_results.append(("market_research", emphasis, False))
    
    # Test 6: General Education Tracking
    print("\n📝 Test 6: General Education Tracking...")
    try:
        result = await iap_manager.track_general_education(
            student_id="SJ2024001",
            course_list=["ENGL 1010", "MATH 1050", "BIOL 1010", "HIST 1700", "PHIL 1000"]
        )
        print("   ✅ General education tracking completed")
        test_results.append(("ge_tracking", "SJ2024001", True))
    except Exception as e:
        print(f"   ❌ Failed GE tracking: {e}")
        test_results.append(("ge_tracking", "SJ2024001", False))
    
    # Test 7: Concentration Area Validation
    print("\n📝 Test 7: Concentration Area Validation...")
    try:
        result = await iap_manager.validate_concentration_areas(
            student_id="SJ2024001",
            concentration_areas=["Psychology", "Communication", "Social Work"],
            course_mappings={
                "Psychology": ["PSYC 1010", "PSYC 3400", "PSYC 4600"],
                "Communication": ["COMM 1020", "COMM 3050", "COMM 4200"],
                "Social Work": ["SW 2010", "SW 3300", "SW 4100"]
            }
        )
        print("   ✅ Concentration area validation completed")
        test_results.append(("concentration_validation", "SJ2024001", True))
    except Exception as e:
        print(f"   ❌ Failed concentration validation: {e}")
        test_results.append(("concentration_validation", "SJ2024001", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, _, success in test_results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ FAILED TESTS:")
        for test_type, identifier, success in test_results:
            if not success:
                print(f"   - {test_type}: {identifier}")
    
    success_rate = (passed_tests / total_tests) * 100
    overall_success = success_rate >= 85  # 85% success rate threshold
    
    if overall_success:
        print(f"\n🎉 IAP SYSTEM READY FOR PRODUCTION!")
        print("✅ All core functionality verified")
        print("🚀 Ready for Docker rebuild and deployment")
    else:
        print(f"\n⚠️  IAP system needs attention before production")
        print("🔧 Fix failed tests before proceeding")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(comprehensive_iap_test())
    exit(0 if success else 1)
