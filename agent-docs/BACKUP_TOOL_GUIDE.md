# Supabase Backup Population Tool Guide

## Overview

The `populate_supabase_backup.py` tool is a standalone backup solution for populating Supabase academic tables when the main MCP tool encounters issues. It provides robust duplicate handling, batch processing, and comprehensive error recovery.

## Features

- **Intelligent Duplicate Handling**: Automatically skips duplicates based on unique constraints
- **Batch Processing**: Configurable batch sizes for efficient database operations
- **UPSERT Logic**: Uses upsert instead of insert to handle conflicts gracefully
- **Data Truncation**: Automatically truncates long fields to fit database constraints
- **Comprehensive Error Handling**: Catches and reports errors without stopping the process
- **Detailed Statistics**: Shows exactly what was processed, inserted, and skipped
- **Dry Run Mode**: Preview what would be inserted without actually inserting

## Usage

### Basic Commands

```bash
# Basic population (recommended first run)
python agent-docs/populate_supabase_backup.py

# Clear existing data before population
python agent-docs/populate_supabase_backup.py --clear

# Dry run to preview what would be inserted
python agent-docs/populate_supabase_backup.py --dry-run

# Verbose output with detailed progress
python agent-docs/populate_supabase_backup.py --verbose

# Custom batch size (default: 100)
python agent-docs/populate_supabase_backup.py --batch-size 50

# Combined options
python agent-docs/populate_supabase_backup.py --clear --verbose --batch-size 200
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--clear` | Clear existing data before population | False |
| `--batch-size N` | Number of records per batch | 100 |
| `--dry-run` | Show what would be inserted without inserting | False |
| `--verbose` | Show detailed progress information | False |

## When to Use

### Primary Use Cases

1. **MCP Tool Failures**: When the main `build_academic_knowledge_graph` MCP tool fails
2. **Data Corruption**: When Supabase tables become corrupted or incomplete
3. **Fresh Deployments**: When setting up a new environment
4. **Data Validation**: When you need to verify data integrity

### Recommended Workflow

1. **First, try the MCP tool**:
   ```python
   # Via MCP client
   await mcp_client.call_tool("build_academic_knowledge_graph")
   ```

2. **If MCP tool fails, use backup tool**:
   ```bash
   python agent-docs/populate_supabase_backup.py --clear --verbose
   ```

3. **Verify results**:
   ```bash
   python -c "
   import os
   from dotenv import load_dotenv
   from supabase import create_client
   
   load_dotenv()
   supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
   
   dept_count = supabase.table('academic_departments').select('*', count='exact').execute()
   course_count = supabase.table('academic_courses').select('*', count='exact').execute()
   program_count = supabase.table('academic_programs').select('*', count='exact').execute()
   
   print(f'Departments: {dept_count.count}')
   print(f'Courses: {course_count.count}')
   print(f'Programs: {program_count.count}')
   print(f'Total: {dept_count.count + course_count.count + program_count.count}')
   "
   ```

## Expected Results

### Typical Population Results

- **Departments**: ~35 unique departments (96+ duplicates skipped)
- **Courses**: ~654 unique courses
- **Programs**: ~287 unique programs
- **Total Records**: ~976 records inserted

### Sample Output

```
🚀 Starting Backup Supabase Population Process...
   📊 Batch size: 100
   🧹 Clear existing: True
   🔍 Dry run: False

1️⃣ Extracting Academic Data...
   📊 Extracted: 654 courses, 287 programs, 131 departments

2️⃣ Clearing Existing Data...
   ✅ Cleared academic_courses
   ✅ Cleared academic_programs
   ✅ Cleared academic_departments

3️⃣ Populating Departments (131 total)...
   ✅ Upserted batch 1: 35 departments
   📊 Departments: 35 unique records prepared

4️⃣ Populating Courses (654 total)...
   ✅ Upserted batch 1: 100 courses
   ✅ Upserted batch 2: 100 courses
   ...
   📊 Courses: 654 unique records prepared

5️⃣ Populating Programs (287 total)...
   ✅ Upserted batch 1: 100 programs
   ✅ Upserted batch 2: 100 programs
   ✅ Upserted batch 3: 87 programs
   📊 Programs: 287 unique records prepared

🏁 Final Population Statistics:
   📊 Records Processed:
      - Departments: 131 → 35 inserted
      - Courses: 654 → 654 inserted
      - Programs: 287 → 287 inserted
   ⏭️ Duplicates Skipped: 96
   ✅ No errors encountered

🎉 Total Records Inserted: 976

✅ Backup population completed successfully!
```

## Troubleshooting

### Common Issues

1. **Environment Variables Missing**
   ```bash
   # Ensure .env file exists with:
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_KEY=your_service_key
   ```

2. **Neo4j Connection Issues**
   ```bash
   # Ensure Neo4j is running:
   docker ps | grep neo4j
   
   # If not running, start it:
   docker run -d --name neo4j-utah-tech \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password123 \
     neo4j:latest
   ```

3. **Supabase Schema Missing**
   - Ensure academic tables exist in Supabase
   - Run the SQL migration script if needed

4. **Permission Errors**
   ```bash
   # Make script executable:
   chmod +x agent-docs/populate_supabase_backup.py
   ```

### Error Recovery

The tool is designed to be resilient:

- **Duplicate Constraints**: Automatically skipped with UPSERT logic
- **Long Field Values**: Automatically truncated to fit constraints
- **Batch Failures**: Individual batches fail independently
- **Connection Issues**: Clear error messages with retry suggestions

### Validation Commands

```bash
# Check table counts
python -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

tables = ['academic_departments', 'academic_courses', 'academic_programs']
for table in tables:
    count = supabase.table(table).select('*', count='exact').execute()
    print(f'{table}: {count.count} records')
"

# Test MCP tools after population
python -c "
import asyncio
from src.mcp_server import search_courses

async def test():
    result = await search_courses('psychology', match_count=3)
    print('Search test:', len(result.get('courses', [])), 'courses found')

asyncio.run(test())
"
```

## Integration with MCP System

The backup tool integrates seamlessly with the MCP system:

1. **Data Source**: Uses the same extraction logic as MCP tools
2. **Schema Compatibility**: Populates the same Supabase tables used by MCP tools
3. **Data Format**: Maintains identical data structure and relationships
4. **Validation**: Can be validated using existing MCP tool queries

## Maintenance

### Regular Maintenance Tasks

1. **Monthly Data Refresh**:
   ```bash
   python agent-docs/populate_supabase_backup.py --clear
   ```

2. **Data Validation**:
   ```bash
   python agent-docs/populate_supabase_backup.py --dry-run --verbose
   ```

3. **Performance Monitoring**:
   - Monitor batch processing times
   - Adjust `--batch-size` based on performance
   - Check for new duplicate patterns

### Updating the Tool

When updating the tool:

1. Test with `--dry-run` first
2. Backup existing data if needed
3. Use `--verbose` to monitor changes
4. Validate results with MCP tool queries

## Security Considerations

- **Service Key**: Uses Supabase service key (keep secure)
- **Environment Variables**: Store credentials in `.env` file
- **Data Validation**: Always validate results after population
- **Access Control**: Limit access to production environments

## Performance Optimization

### Batch Size Tuning

- **Small datasets** (< 1000 records): `--batch-size 50`
- **Medium datasets** (1000-5000 records): `--batch-size 100` (default)
- **Large datasets** (> 5000 records): `--batch-size 200`

### Memory Usage

The tool is designed for efficient memory usage:
- Processes data in batches
- Releases memory after each batch
- Suitable for production environments

## Support

For issues with the backup tool:

1. Check the troubleshooting section above
2. Run with `--verbose` for detailed logs
3. Use `--dry-run` to test without changes
4. Validate environment setup and dependencies
