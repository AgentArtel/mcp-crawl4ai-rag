# IAP MCP Tool Descriptions and Usage Guide

## Overview

This document provides detailed descriptions of all MCP tools available for IAP management, including specific guidance on how to use each tool in collaborative student interactions.

## Template Management Tools

### `create_iap_template`

**Purpose**: Initialize a new IAP template with student information and default structure.

**Parameters**:
- `student_name` (required): Full name of the student
- `student_id` (required): Utah Tech student ID number
- `student_email` (optional): Student's email address
- `degree_emphasis` (required): Chosen degree emphasis/title

**Returns**: JSON with created IAP template ID and initial structure

**Student Collaboration Context**:
- **When to Use**: At the beginning of the first advising session
- **How to Introduce**: "Let's start by creating your personalized IAP template"
- **Student Involvement**: Have student provide their information directly
- **Follow-up**: "Great! I've created your IAP foundation. Now we can start building your plan together."

**Example Usage**:
```python
result = await create_iap_template(
    student_name="Sarah Johnson",
    student_id="87654321", 
    student_email="sarah.johnson@utahtech.edu",
    degree_emphasis="Digital Marketing and Data Analytics"
)
```

**Communication Tips**:
- Explain that this creates their "academic blueprint"
- Reassure students that everything can be modified later
- Emphasize that this is the start of a collaborative process

---

### `update_iap_section`

**Purpose**: Update specific sections of an existing IAP template.

**Parameters**:
- `iap_id` (required): ID of the IAP to update
- `section` (required): Section name to update (mission_statement, program_goals, etc.)
- `content` (required): New content for the section

**Returns**: JSON with update status and validation results

**Student Collaboration Context**:
- **When to Use**: After collaborative discussions and decisions
- **How to Introduce**: "Let's update your IAP with what we've discussed"
- **Student Involvement**: Review changes together before implementing
- **Follow-up**: "Perfect! Your IAP now reflects our discussion. What should we work on next?"

**Example Usage**:
```python
await update_iap_section(
    iap_id="iap_123",
    section="mission_statement",
    content="To integrate creative digital media skills with data analytics..."
)
```

**Communication Tips**:
- Always review the content with the student before updating
- Explain what section is being modified and why
- Confirm student agreement with changes

---

### `generate_iap_suggestions`

**Purpose**: Generate AI-powered suggestions for IAP content based on context.

**Parameters**:
- `iap_id` (required): ID of the IAP
- `section_type` (required): Type of content to generate
- `context` (optional): Additional context for suggestions

**Returns**: JSON with multiple suggestion options

**Student Collaboration Context**:
- **When to Use**: When students need inspiration or are stuck
- **How to Introduce**: "Let me generate some ideas to help spark your thinking"
- **Student Involvement**: Review suggestions together and choose/modify preferred options
- **Follow-up**: "Which of these resonates with you? How would you modify it to make it your own?"

**Example Usage**:
```python
suggestions = await generate_iap_suggestions(
    iap_id="iap_123",
    section_type="mission_statement",
    context="digital media, data analytics, creative technology"
)
```

**Communication Tips**:
- Present suggestions as starting points, not final answers
- Encourage students to personalize and modify suggestions
- Use suggestions to facilitate discussion about student goals

---

### `validate_complete_iap`

**Purpose**: Perform comprehensive validation of an entire IAP against all requirements.

**Parameters**:
- `iap_id` (required): ID of the IAP to validate

**Returns**: JSON with detailed validation report including compliance status and recommendations

**Student Collaboration Context**:
- **When to Use**: Before final submission and at major milestones
- **How to Introduce**: "Let's run a comprehensive check to make sure everything is in order"
- **Student Involvement**: Review results together and discuss any issues
- **Follow-up**: "Here's what we need to address..." or "Excellent! Your IAP meets all requirements."

**Example Usage**:
```python
validation = await validate_complete_iap(iap_id="iap_123")
```

**Communication Tips**:
- Frame validation as a helpful check, not a test
- Explain any issues in understandable terms
- Work together to resolve validation problems

## Specialized Analysis Tools

### `conduct_market_research`

**Purpose**: Generate comprehensive market research analysis for degree viability.

**Parameters**:
- `degree_emphasis` (required): The degree emphasis to research
- `concentration_areas` (optional): List of concentration areas

**Returns**: JSON with market analysis, salary data, job prospects, and viability score

**Student Collaboration Context**:
- **When to Use**: When discussing career prospects or preparing cover letters
- **How to Introduce**: "Let's research the job market for your chosen field"
- **Student Involvement**: Discuss findings and their implications for career planning
- **Follow-up**: "Based on this research, how do you feel about your career prospects? Should we adjust anything?"

**Example Usage**:
```python
research = await conduct_market_research(
    degree_emphasis="Digital Marketing and Data Analytics",
    concentration_areas=["Marketing", "Computer Science", "Business"]
)
```

**Communication Tips**:
- Present data objectively but encouragingly
- Help students understand how to use this information
- Address any concerns about market viability
- Connect research to cover letter development

---

### `track_general_education`

**Purpose**: Track student progress on Utah Tech's general education requirements.

**Parameters**:
- `courses` (required): List of completed or planned courses

**Returns**: JSON with GE completion status, missing requirements, and recommendations

**Student Collaboration Context**:
- **When to Use**: Early in planning process and before graduation
- **How to Introduce**: "Let's make sure we're covering all your graduation requirements"
- **Student Involvement**: Review transcript together and plan remaining GE courses
- **Follow-up**: "Here's what you still need for graduation. Let's find courses that also support your concentrations."

**Example Usage**:
```python
ge_status = await track_general_education(
    courses=["ENGL 1010", "MATH 1050", "BIOL 1010", "HIST 1700", "PHIL 2050"]
)
```

**Communication Tips**:
- Explain the purpose of general education requirements
- Look for courses that serve multiple purposes
- Help students see GE as part of well-rounded education

---

### `validate_concentration_areas`

**Purpose**: Validate that concentration areas meet BIS program requirements.

**Parameters**:
- `course_mappings` (required): Dictionary mapping concentration areas to course lists

**Returns**: JSON with validation results, credit analysis, and compliance status

**Student Collaboration Context**:
- **When to Use**: After course selection and before plan finalization
- **How to Introduce**: "Let's verify that your concentration areas meet the program requirements"
- **Student Involvement**: Review credit distribution and discuss any needed adjustments
- **Follow-up**: "Your concentrations look great!" or "We need to add a few more credits in this area."

**Example Usage**:
```python
validation = await validate_concentration_areas(
    course_mappings={
        "Computer Science": ["CS 1400", "CS 2420", "CS 3005", "CS 4700"],
        "Digital Media": ["DIGI 1000", "DIGI 2500", "DIGI 3000", "DIGI 4000"],
        "Business": ["BSAD 2050", "BSAD 3400", "BSAD 4800"]
    }
)
```

**Communication Tips**:
- Explain the rationale behind concentration requirements
- Help students understand credit distribution needs
- Suggest specific courses to meet requirements

## Knowledge Graph Tools

### Academic Search Tools

These tools help students explore available courses and programs:

#### `search_degree_programs`
- **Purpose**: Find degree programs and concentrations
- **Student Context**: "Let's explore what programs Utah Tech offers in your areas of interest"
- **Collaboration**: Review options together and discuss how they align with goals

#### `search_courses`
- **Purpose**: Find specific courses by subject, level, or keywords
- **Student Context**: "Let me find courses that would support your learning goals"
- **Collaboration**: Discuss course descriptions and how they fit the overall plan

#### `validate_iap_requirements`
- **Purpose**: Check course prerequisites and academic requirements
- **Student Context**: "Let's make sure you can take these courses in the right sequence"
- **Collaboration**: Plan course timing and identify any prerequisite gaps

## Tool Integration Strategies

### Sequential Tool Usage

**Typical IAP Development Sequence**:
1. `create_iap_template` - Start the process
2. `generate_iap_suggestions` - Develop mission and goals
3. `search_degree_programs` / `search_courses` - Explore options
4. `validate_concentration_areas` - Check course selections
5. `track_general_education` - Ensure graduation requirements
6. `conduct_market_research` - Validate career prospects
7. `validate_complete_iap` - Final comprehensive check

### Iterative Refinement

**Continuous Improvement Process**:
- Use `update_iap_section` after each major decision
- Run validation tools regularly to catch issues early
- Generate new suggestions when students need fresh ideas
- Validate requirements before making major changes

### Error Handling and Recovery

**When Tools Return Errors**:
- Explain the issue in student-friendly terms
- Suggest alternative approaches or solutions
- Use the opportunity to teach about requirements
- Maintain positive, problem-solving attitude

**Example Error Communication**:
- Tool Error: "Insufficient credits in concentration area"
- Student Communication: "It looks like we need a few more credits in Computer Science to meet the requirements. Let's find some additional courses that interest you in that area."

## Best Practices for Tool Usage

### Before Using Tools
- Explain what you're about to do and why
- Set expectations for what the results will show
- Involve the student in providing input parameters

### During Tool Execution
- Keep students engaged while tools run
- Explain any delays or processing time
- Prepare students for different possible outcomes

### After Tool Results
- Interpret results in context of student goals
- Highlight key findings and implications
- Translate technical information into actionable insights
- Always connect results back to the student's overall plan

### Documentation and Follow-up
- Update IAP sections based on tool results and discussions
- Document decisions and rationale
- Plan next steps based on findings
- Schedule follow-up sessions as needed

## Troubleshooting Common Issues

### Tool Connection Problems
- **Issue**: Database or service unavailable
- **Student Communication**: "I'm having a technical issue. Let me try a different approach while we wait for this to resolve."
- **Alternative**: Use manual processes or reschedule if necessary

### Validation Failures
- **Issue**: IAP doesn't meet requirements
- **Student Communication**: "The system found a few areas we need to address. Let's work through them together."
- **Approach**: Frame as opportunities for improvement, not failures

### Conflicting Requirements
- **Issue**: Course selections don't satisfy multiple requirements
- **Student Communication**: "It looks like we have some competing requirements here. Let's find creative solutions."
- **Strategy**: Look for courses that serve multiple purposes

Remember: Tools are meant to enhance, not replace, the collaborative relationship between advisor and student. Always use tools in service of student learning and empowerment.
