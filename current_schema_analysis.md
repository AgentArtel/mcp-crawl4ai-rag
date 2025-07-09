# Current Supabase Schema Analysis

## Existing Schema (From Your SQL Scripts)

### Core Tables (Script 1)
1. **`sources`** - Source metadata
   - `source_id` (text, primary key)
   - `summary` (text)
   - `total_word_count` (integer, default 0)
   - `created_at`, `updated_at` (timestamptz)

2. **`crawled_pages`** - Main content storage with embeddings
   - `id` (bigserial, primary key)
   - `url` (varchar)
   - `chunk_number` (integer)
   - `content` (text)
   - `metadata` (jsonb)
   - `source_id` (text, FK to sources)
   - `embedding` (vector(1536))
   - `created_at` (timestamptz)
   - Unique constraint: (url, chunk_number)

3. **`code_examples`** - Code examples with embeddings
   - `id` (bigserial, primary key)
   - `url` (varchar)
   - `chunk_number` (integer)
   - `content` (text)
   - `summary` (text)
   - `metadata` (jsonb)
   - `source_id` (text, FK to sources)
   - `embedding` (vector(1536))
   - `created_at` (timestamptz)
   - Unique constraint: (url, chunk_number)

### Academic Tables (Script 2)
4. **`academic_courses`** - Course information
   - `course_id` (serial, primary key)
   - `course_code` (text, unique)
   - `title` (text)
   - `credits` (numeric(3,1))
   - `level` (text) - 'lower' or 'upper' division
   - `description` (text)
   - `prerequisites` (text)
   - `url` (text)
   - `source_id` (text, FK to sources)
   - `created_at` (timestamptz)

5. **`crawled_page_course_mapping`** - Links pages to courses
   - `id` (serial, primary key)
   - `page_id` (bigint, FK to crawled_pages)
   - `course_id` (integer, FK to academic_courses)
   - `created_at` (timestamptz)
   - Unique constraint: (page_id, course_id)

6. **`gen_ed_requirements`** - General education requirements
   - `requirement_id` (serial, primary key)
   - `code` (text) - e.g., "EN", "QL"
   - `name` (text) - e.g., "English", "Quantitative Literacy"
   - `description` (text)
   - `credits_required` (integer)
   - `created_at` (timestamptz)

7. **`course_gen_ed_mapping`** - Course to Gen Ed mapping
   - `course_id` (integer, FK to academic_courses)
   - `requirement_id` (integer, FK to gen_ed_requirements)
   - Primary key: (course_id, requirement_id)

8. **`student_plans`** - Student IAPs
   - `plan_id` (serial, primary key)
   - `student_id` (text)
   - `emphasis_title` (text)
   - `mission_statement` (text)
   - `status` (text, default 'draft')
   - `created_at`, `updated_at` (timestamptz)

9. **`plan_courses`** - Courses in student plans
   - `plan_course_id` (serial, primary key)
   - `plan_id` (integer, FK to student_plans)
   - `course_id` (integer, FK to academic_courses)
   - `semester` (text)
   - `is_completed` (boolean, default false)
   - `grade` (text)
   - `notes` (text)
   - `created_at` (timestamptz)
   - Unique constraint: (plan_id, course_id, semester)

### Views
10. **`academic_search`** - Combined view for academic content search
    - Joins crawled_pages, crawled_page_course_mapping, and academic_courses
    - Provides unified access to content with course information

## Key Observations

### Strengths of Current Schema
1. **Well-designed vector search** with proper indexing
2. **Flexible metadata** using JSONB
3. **Good normalization** with proper foreign keys
4. **IAP-specific tables** already in place
5. **RLS policies** for security

### Missing Elements for Knowledge Graph
1. **Academic hierarchy** (universities, colleges, departments)
2. **Program information** (degree programs, emphases)
3. **Prerequisite relationships** (structured prerequisite chains)
4. **Program requirements** (which courses are required for which programs)

### Compatibility Notes
- Your `academic_courses` table uses `course_id` (serial) as primary key
- Our Neo4j extraction uses `course_code` as the primary identifier
- Your `credits` column is `numeric(3,1)` vs our assumed `integer`
- Your `level` uses 'lower'/'upper' vs our 'lower_division'/'upper_division'
