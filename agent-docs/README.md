# Utah Tech University IAP Advisor Agent

<p align="center">
  <em>AI-Powered Individualized Academic Plan (IAP) Advisor for Bachelor of Individualized Studies Program</em>
</p>

## Overview

The Utah Tech University IAP Advisor Agent is a comprehensive AI system designed to assist students and academic advisors in creating, managing, and validating Individualized Academic Plans (IAPs) for the Bachelor of Individualized Studies (BIS) program.

## System Architecture

### Core Components
- **MCP Server Integration**: 7 specialized IAP management tools
- **Database Layer**: PostgreSQL/Supabase with 5 IAP-specific tables
- **Knowledge Graph**: Neo4j for academic data relationships and validation
- **RAG System**: Crawl4AI for Utah Tech academic content retrieval

### Backup Population Tool

The system includes a standalone backup tool (`populate_supabase_backup.py`) for reliable Supabase table population:

- **Purpose**: Ensures academic data is properly loaded into Supabase tables when MCP tools encounter issues
- **Features**: Intelligent duplicate handling, batch processing, UPSERT logic, data truncation
- **Usage**: `python populate_supabase_backup.py --clear --verbose`
- **Results**: Populates ~976 academic records (35 departments, 654 courses, 287 programs)
- **Documentation**: See [`BACKUP_TOOL_GUIDE.md`](BACKUP_TOOL_GUIDE.md) for detailed instructions

### IAP Management Capabilities

#### 1. **IAP Template Management**
- Create new IAP templates with student information
- Store and retrieve IAP documents from database
- Update specific sections of existing IAPs
- Full CRUD operations for IAP lifecycle management

#### 2. **Mission Statement Generator**
- AI-assisted mission statement creation
- Contextual suggestions based on degree emphasis
- Integration with student goals and career objectives
- Validation against BIS program requirements

#### 3. **Program Goals & PLO Generator**
- Generate Program Learning Outcomes (PLOs)
- Create measurable program goals
- Align goals with Utah Tech's BIS requirements
- Default templates with customization options

#### 4. **Course-to-PLO Mapping**
- Map selected courses to Program Learning Outcomes
- Validate course selections against PLO requirements
- Ensure comprehensive coverage of learning objectives
- Track credit hour distribution across PLOs

#### 5. **Market Research Integration**
- Comprehensive job market analysis for degree viability
- Salary data and industry trend analysis
- Skills demand assessment for chosen emphasis areas
- Viability scoring for cover letter support

#### 6. **General Education Tracking**
- Track completion of Utah Tech's 9 GE requirement categories
- Monitor 36 total credit hour requirement
- Validate course selections against GE requirements
- Progress reporting and completion status

#### 7. **Concentration Area Validation**
- Ensure minimum 3 concentration areas (disciplines)
- Validate 14+ credit hours per concentration area
- Verify 7+ upper-division credits per area
- Cross-disciplinary coherence analysis

## Database Schema

### Core Tables
- **`iap_templates`**: Main IAP document storage
- **`iap_general_education`**: GE requirement tracking
- **`iap_market_research`**: Job market analysis data
- **`iap_concentration_validation`**: Concentration area analysis
- **`iap_course_plo_mappings`**: Course-to-PLO relationships

### Views and Indexes
- **`iap_summary`**: Comprehensive IAP overview
- Optimized indexes for efficient querying
- Foreign key relationships for data integrity

## MCP Tools Reference

### Template Management Tools

#### `create_iap_template`
**Purpose**: Initialize a new IAP template with default structure
**Input**: Student information (name, ID, email, emphasis)
**Output**: Created IAP template with unique ID
**Usage**: Start of IAP creation process

#### `update_iap_section`
**Purpose**: Update specific sections of an existing IAP
**Input**: IAP ID, section name, new content
**Output**: Updated IAP with validation status
**Usage**: Iterative IAP development and refinement

#### `generate_iap_suggestions`
**Purpose**: AI-powered content suggestions for IAP sections
**Input**: IAP ID, section type, context
**Output**: Contextual suggestions and recommendations
**Usage**: Assist students with content creation

#### `validate_complete_iap`
**Purpose**: Comprehensive validation of entire IAP
**Input**: IAP ID
**Output**: Validation report with compliance status
**Usage**: Final IAP review before submission

### Specialized Analysis Tools

#### `conduct_market_research`
**Purpose**: Generate market viability analysis for degree emphasis
**Input**: Degree emphasis, concentration areas
**Output**: Market research report with viability score
**Usage**: Support cover letter and career planning

#### `track_general_education`
**Purpose**: Monitor GE requirement completion
**Input**: Student course list
**Output**: GE completion status and recommendations
**Usage**: Ensure graduation requirements are met

#### `validate_concentration_areas`
**Purpose**: Validate concentration area requirements
**Input**: Course mappings by discipline
**Output**: Validation report with credit analysis
**Usage**: Ensure BIS program compliance

## Agent Instructions

### Student Collaboration Workflow

#### Phase 1: Initial Consultation
1. **Gather Student Information**
   - Name, student ID, contact information
   - Academic interests and career goals
   - Preferred concentration areas (3+ disciplines)

2. **Create IAP Template**
   - Use `create_iap_template` with student data
   - Establish foundation for collaborative development

#### Phase 2: Mission and Goals Development
1. **Mission Statement Creation**
   - Use `generate_iap_suggestions` for mission statement
   - Collaborate with student to refine and personalize
   - Ensure alignment with career objectives

2. **Program Goals Definition**
   - Generate initial PLOs using `generate_iap_suggestions`
   - Work with student to customize goals
   - Validate against BIS requirements

#### Phase 3: Course Planning and Mapping
1. **Course Selection Guidance**
   - Use knowledge graph tools to search relevant courses
   - Check prerequisites and course availability
   - Ensure distribution across concentration areas

2. **PLO Mapping**
   - Map selected courses to Program Learning Outcomes
   - Use `validate_concentration_areas` for compliance
   - Adjust course selections as needed

#### Phase 4: Requirements Validation
1. **General Education Check**
   - Use `track_general_education` with course list
   - Identify missing GE requirements
   - Recommend suitable courses

2. **Market Research Analysis**
   - Conduct `conduct_market_research` for viability
   - Discuss career prospects and market trends
   - Integrate findings into cover letter

#### Phase 5: Final Validation and Submission
1. **Comprehensive Review**
   - Use `validate_complete_iap` for final check
   - Address any compliance issues
   - Ensure all requirements are met

2. **Documentation Finalization**
   - Generate final IAP document
   - Prepare supporting materials
   - Submit for academic approval

### Communication Best Practices

#### Student Engagement
- **Active Listening**: Understand student goals and concerns
- **Collaborative Approach**: Work with, not for, the student
- **Educational Guidance**: Explain requirements and rationale
- **Supportive Feedback**: Encourage and guide improvements

#### Technical Communication
- **Clear Explanations**: Translate technical requirements into understandable terms
- **Visual Aids**: Use progress tracking and completion percentages
- **Step-by-Step Guidance**: Break complex processes into manageable steps
- **Regular Check-ins**: Monitor progress and adjust plans as needed

#### Problem-Solving Approach
- **Identify Issues Early**: Use validation tools proactively
- **Offer Solutions**: Provide specific recommendations and alternatives
- **Explain Consequences**: Help students understand requirement impacts
- **Flexible Planning**: Adapt to changing student needs and circumstances

## Usage Examples

### Creating a New IAP
```python
# Step 1: Create template
result = await create_iap_template(
    student_name="Jane Smith",
    student_id="12345678",
    student_email="jane.smith@utahtech.edu",
    degree_emphasis="Digital Media and Data Analytics"
)

# Step 2: Generate mission statement
mission = await generate_iap_suggestions(
    iap_id=result['iap_id'],
    section_type="mission_statement",
    context="Digital media, data analytics, creative technology"
)

# Step 3: Update with mission
await update_iap_section(
    iap_id=result['iap_id'],
    section="mission_statement",
    content=mission['suggestions'][0]
)
```

### Validating Course Selections
```python
# Check concentration areas
validation = await validate_concentration_areas(
    course_mappings={
        "Computer Science": ["CS 1400", "CS 2420", "CS 3005"],
        "Digital Media": ["DIGI 1000", "DIGI 2500", "DIGI 3000"],
        "Business": ["BSAD 2050", "BSAD 3400", "BSAD 4800"]
    }
)

# Track GE completion
ge_status = await track_general_education(
    courses=["ENGL 1010", "MATH 1050", "BIOL 1010", "HIST 1700"]
)
```

## Troubleshooting

### Common Issues
- **Database Connection**: Verify Supabase credentials in `.env`
- **Missing Prerequisites**: Use knowledge graph to check course requirements
- **Validation Failures**: Review BIS program requirements and adjust accordingly
- **Market Research Errors**: Ensure degree emphasis is clearly defined

### Support Resources
- Utah Tech BIS Program Requirements
- Academic Catalog and Course Descriptions
- Knowledge Graph Query Tools
- Database Schema Documentation

## Development and Testing

### Running Tests
```bash
cd /path/to/utah-tech-mcp-advisor
python test_iap_comprehensive.py
```

### Docker Deployment
```bash
docker build -t utah-tech-iap-advisor .
docker run --env-file .env -p 8051:8051 utah-tech-iap-advisor
```

## Contributing

This system is designed to be extensible and maintainable. When adding new features:

1. Follow the established MCP tool pattern
2. Update database schema as needed
3. Add comprehensive tests
4. Update documentation
5. Validate against BIS program requirements

## License

This project is developed for Utah Tech University's Bachelor of Individualized Studies program.
