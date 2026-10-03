#!/usr/bin/env bash
# ==============================================================================
# University Course Catalog MCP Server - End-to-End Curl Demonstration Script
# Compatible with Git Bash, Linux, and macOS
# ==============================================================================

set -e

BASE_URL="http://localhost:8080"
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

print_step() {
    echo -e "\n${CYAN}==============================================================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${CYAN}==============================================================================${NC}"
}

format_json() {
    if command -v jq &> /dev/null; then
        jq .
    else
        python3 -m json.tool
    fi
}

echo -e "${GREEN}Running University Course Catalog MCP Server Curl Verification...${NC}"

# 1. Healthcheck
print_step "1. Healthcheck Endpoint [GET /health]"
echo "Command: curl -s ${BASE_URL}/health"
curl -s "${BASE_URL}/health" | format_json

# 2. Server Root & Service Discovery
print_step "2. Server Root & Service Discovery [GET /]"
echo "Command: curl -s ${BASE_URL}/"
curl -s "${BASE_URL}/" | format_json

# 3. List Registered Tools
print_step "3. List Registered Tools [GET /tools]"
echo "Command: curl -s ${BASE_URL}/tools"
curl -s "${BASE_URL}/tools" | format_json

# 4. Tool 1: search_courses (Query 'Introduction')
print_step "4. Tool: search_courses (Query 'Introduction') [POST /tools/search_courses]"
echo "Command: curl -s -X POST ${BASE_URL}/tools/search_courses -H 'Content-Type: application/json' -d '{\"query\": \"Introduction\"}'"
curl -s -X POST "${BASE_URL}/tools/search_courses" \
    -H "Content-Type: application/json" \
    -d '{"query": "Introduction"}' | format_json

# 5. Tool 1: search_courses (Filtered by department 'CS')
print_step "5. Tool: search_courses (Query 'Programming', Department 'CS') [POST /tools/search_courses]"
echo "Command: curl -s -X POST ${BASE_URL}/tools/search_courses -H 'Content-Type: application/json' -d '{\"query\": \"Programming\", \"department_code\": \"CS\"}'"
curl -s -X POST "${BASE_URL}/tools/search_courses" \
    -H "Content-Type: application/json" \
    -d '{"query": "Programming", "department_code": "CS"}' | format_json

# 6. Tool 1: search_courses (Non-existent query -> returns [])
print_step "6. Tool: search_courses (Non-existent query -> returns []) [POST /tools/search_courses]"
echo "Command: curl -s -X POST ${BASE_URL}/tools/search_courses -H 'Content-Type: application/json' -d '{\"query\": \"NonExistentCourseXYZ\"}'"
curl -s -X POST "${BASE_URL}/tools/search_courses" \
    -H "Content-Type: application/json" \
    -d '{"query": "NonExistentCourseXYZ"}' | format_json

# 7. Tool 2: get_prerequisites (Course with prerequisites: CS102 requires CS101)
print_step "7. Tool: get_prerequisites (Course with prerequisite: CS102) [POST /tools/get_prerequisites]"
echo "Command: curl -s -X POST ${BASE_URL}/tools/get_prerequisites -H 'Content-Type: application/json' -d '{\"course_code\": \"CS102\"}'"
curl -s -X POST "${BASE_URL}/tools/get_prerequisites" \
    -H "Content-Type: application/json" \
    -d '{"course_code": "CS102"}' | format_json

# 8. Tool 2: get_prerequisites (Course with NO prerequisites: CS101 -> empty array)
print_step "8. Tool: get_prerequisites (Course with NO prerequisite: CS101) [POST /tools/get_prerequisites]"
echo "Command: curl -s -X POST ${BASE_URL}/tools/get_prerequisites -H 'Content-Type: application/json' -d '{\"course_code\": \"CS101\"}'"
curl -s -X POST "${BASE_URL}/tools/get_prerequisites" \
    -H "Content-Type: application/json" \
    -d '{"course_code": "CS101"}' | format_json

# 9. Tool 3: lookup_instructor (Valid instructor: Dr. Alan Turing)
print_step "9. Tool: lookup_instructor (Valid instructor) [POST /tools/lookup_instructor]"
echo "Command: curl -s -X POST ${BASE_URL}/tools/lookup_instructor -H 'Content-Type: application/json' -d '{\"instructor_name\": \"Dr. Alan Turing\"}'"
curl -s -X POST "${BASE_URL}/tools/lookup_instructor" \
    -H "Content-Type: application/json" \
    -d '{"instructor_name": "Dr. Alan Turing"}' | format_json

# 10. Tool 3: lookup_instructor (Non-existent instructor -> structured error)
print_step "10. Tool: lookup_instructor (Non-existent instructor -> structured error) [POST /tools/lookup_instructor]"
echo "Command: curl -s -X POST ${BASE_URL}/tools/lookup_instructor -H 'Content-Type: application/json' -d '{\"instructor_name\": \"Unknown Professor\"}'"
curl -s -X POST "${BASE_URL}/tools/lookup_instructor" \
    -H "Content-Type: application/json" \
    -d '{"instructor_name": "Unknown Professor"}' | format_json

# 11. Tool 4: get_prerequisite_graph (Multi-level chain for CS301: CS101 -> CS102 -> CS201 -> CS301)
print_step "11. Tool: get_prerequisite_graph (Multi-level chain for CS301) [POST /tools/get_prerequisite_graph]"
echo "Command: curl -s -X POST ${BASE_URL}/tools/get_prerequisite_graph -H 'Content-Type: application/json' -d '{\"course_code\": \"CS301\"}'"
curl -s -X POST "${BASE_URL}/tools/get_prerequisite_graph" \
    -H "Content-Type: application/json" \
    -d '{"course_code": "CS301"}' | format_json

# 12. Resource 1: course_descriptions
print_step "12. Resource: course_descriptions [GET /resources/course_descriptions]"
echo "Command: curl -s ${BASE_URL}/resources/course_descriptions"
curl -s "${BASE_URL}/resources/course_descriptions"

# 13. Resource 2: department_directory
print_step "13. Resource: department_directory [GET /resources/department_directory]"
echo "Command: curl -s ${BASE_URL}/resources/department_directory"
curl -s "${BASE_URL}/resources/department_directory"

# 14. Prompt Template: course_comparison_template
print_step "14. Prompt Template: course_comparison_template [GET /prompts/course_comparison_template]"
echo "Command: curl -s ${BASE_URL}/prompts/course_comparison_template"
curl -s "${BASE_URL}/prompts/course_comparison_template"
echo ""

# 15. Native MCP JSON-RPC 2.0 Call (initialize)
print_step "15. Native MCP JSON-RPC 2.0 (initialize) [POST /]"
echo "Command: curl -s -X POST ${BASE_URL}/ -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{}}'"
curl -s -X POST "${BASE_URL}/" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | format_json

# 16. Native MCP JSON-RPC 2.0 Call (tools/call search_courses)
print_step "16. Native MCP JSON-RPC 2.0 (tools/call search_courses) [POST /]"
echo "Command: curl -s -X POST ${BASE_URL}/ -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"search_courses\",\"arguments\":{\"query\":\"Calculus\"}}}'"
curl -s -X POST "${BASE_URL}/" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_courses","arguments":{"query":"Calculus"}}}' | format_json

echo -e "\n${GREEN}All demonstration requests executed successfully!${NC}"
