import json
import logging
from typing import Any, Dict, List
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route

from app.config import HOST, LOG_LEVEL, PORT
from app.database import get_db
from app.mcp_server import mcp_server
from data.seed import seed_database
from app.services import (
    search_courses_service,
    get_prerequisites_service,
    lookup_instructor_service,
    get_prerequisite_graph_service,
    get_course_descriptions_service,
    get_department_directory_service,
    get_course_comparison_template_service,
)
from app.schemas import (
    SearchCoursesInput,
    GetPrerequisitesInput,
    LookupInstructorInput,
    GetPrerequisiteGraphInput,
)

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("mcp_server")


# ============================================================================
# REST / Health Endpoints
# ============================================================================

async def health_check(request: Request) -> JSONResponse:
    """Healthcheck endpoint for Docker healthcheck and container orchestrators."""
    return JSONResponse({
        "status": "healthy",
        "service": "mcp-server",
        "version": "1.0.0"
    })


async def root_index(request: Request) -> Response:
    """Root endpoint providing service metadata, routes, or dispatching JSON-RPC POST."""
    if request.method == "POST":
        return await handle_jsonrpc(request)

    return JSONResponse({
        "name": "University Course Catalog MCP Server",
        "status": "running",
        "mcp_endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "streamable_http": "/mcp"
        },
        "rest_endpoints": {
            "health": "/health",
            "tools": "/tools",
            "resources": "/resources",
            "prompts": "/prompts"
        }
    })


# ============================================================================
# REST Tool Endpoints (Direct HTTP API with exact output schemas)
# ============================================================================

async def list_tools_endpoint(request: Request) -> JSONResponse:
    """List all available tools and their schemas."""
    tools = await mcp_server.list_tools()
    return JSONResponse([
        {
            "name": t.name,
            "description": t.description,
            "inputSchema": t.inputSchema,
            "outputSchema": t.outputSchema
        }
        for t in tools
    ])


async def search_courses_endpoint(request: Request) -> JSONResponse:
    """REST endpoint for search_courses."""
    try:
        body = await request.json() if request.method == "POST" else dict(request.query_params)
        validated = SearchCoursesInput(**body)
        with get_db() as db:
            results = search_courses_service(
                db,
                query=validated.query,
                department_code=validated.department_code
            )
        return JSONResponse(results, status_code=200)
    except Exception as e:
        logger.warning(f"Error in search_courses_endpoint: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


async def get_prerequisites_endpoint(request: Request) -> JSONResponse:
    """REST endpoint for get_prerequisites."""
    try:
        body = await request.json() if request.method == "POST" else dict(request.query_params)
        validated = GetPrerequisitesInput(**body)
        with get_db() as db:
            result = get_prerequisites_service(db, course_code=validated.course_code)
        status_code = 404 if "error" in result else 200
        return JSONResponse(result, status_code=status_code)
    except Exception as e:
        logger.warning(f"Error in get_prerequisites_endpoint: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


async def lookup_instructor_endpoint(request: Request) -> JSONResponse:
    """REST endpoint for lookup_instructor."""
    try:
        body = await request.json() if request.method == "POST" else dict(request.query_params)
        validated = LookupInstructorInput(**body)
        with get_db() as db:
            result = lookup_instructor_service(db, instructor_name=validated.instructor_name)
        # Note: Core requirement specifies returning structured error e.g. {"error": "Instructor not found"}
        # Both 200 OK with {"error": "..."} and appropriate body
        return JSONResponse(result, status_code=200)
    except Exception as e:
        logger.warning(f"Error in lookup_instructor_endpoint: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


async def get_prerequisite_graph_endpoint(request: Request) -> JSONResponse:
    """REST endpoint for get_prerequisite_graph."""
    try:
        body = await request.json() if request.method == "POST" else dict(request.query_params)
        validated = GetPrerequisiteGraphInput(**body)
        with get_db() as db:
            result = get_prerequisite_graph_service(db, course_code=validated.course_code)
        status_code = 404 if "error" in result else 200
        return JSONResponse(result, status_code=status_code)
    except Exception as e:
        logger.warning(f"Error in get_prerequisite_graph_endpoint: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


# ============================================================================
# REST Resource & Prompt Endpoints
# ============================================================================

async def list_resources_endpoint(request: Request) -> JSONResponse:
    """List available resources."""
    resources = await mcp_server.list_resources()
    return JSONResponse([
        {
            "name": r.name,
            "uri": str(r.uri),
            "description": r.description
        }
        for r in resources
    ])


async def course_descriptions_endpoint(request: Request) -> Response:
    """Fetch course_descriptions resource."""
    with get_db() as db:
        content = get_course_descriptions_service(db)
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/plain" not in accept:
        return JSONResponse({"name": "course_descriptions", "content": content}, status_code=200)
    return PlainTextResponse(content, status_code=200)


async def department_directory_endpoint(request: Request) -> Response:
    """Fetch department_directory resource."""
    with get_db() as db:
        content = get_department_directory_service(db)
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/plain" not in accept:
        return JSONResponse({"name": "department_directory", "content": content}, status_code=200)
    return PlainTextResponse(content, status_code=200)


async def list_prompts_endpoint(request: Request) -> JSONResponse:
    """List available prompt templates."""
    prompts = await mcp_server.list_prompts()
    return JSONResponse([
        {
            "name": p.name,
            "description": p.description,
            "arguments": [
                {
                    "name": a.name,
                    "description": a.description,
                    "required": a.required
                }
                for a in (p.arguments or [])
            ]
        }
        for p in prompts
    ])


async def course_comparison_template_endpoint(request: Request) -> Response:
    """Fetch course_comparison_template prompt."""
    template = get_course_comparison_template_service()
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/plain" not in accept:
        return JSONResponse({
            "name": "course_comparison_template",
            "template": template,
            "content": template
        }, status_code=200)
    return PlainTextResponse(template, status_code=200)


# ============================================================================
# JSON-RPC 2.0 Dispatcher (Direct protocol support)
# ============================================================================

async def handle_jsonrpc(request: Request) -> JSONResponse:
    """Direct JSON-RPC 2.0 request handler."""
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"}
        }, status_code=400)

    req_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    if not method:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32600, "message": "Invalid Request: missing method"}
        }, status_code=400)

    try:
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "University Course Catalog Server",
                        "version": "1.0.0"
                    }
                }
            })

        elif method == "tools/list":
            tools = await mcp_server.list_tools()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.inputSchema,
                            "outputSchema": t.outputSchema
                        }
                        for t in tools
                    ]
                }
            })

        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            call_res = await mcp_server.call_tool(name, arguments)
            # FastMCP call_tool returns ([TextContent(...)], raw_dict)
            content_list = []
            if isinstance(call_res, tuple) and len(call_res) >= 1:
                content_items = call_res[0]
                for item in content_items:
                    content_list.append({
                        "type": "text",
                        "text": item.text if hasattr(item, "text") else str(item)
                    })
            else:
                content_list.append({"type": "text", "text": json.dumps(call_res)})

            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": content_list,
                    "isError": False
                }
            })

        elif method == "resources/list":
            resources = await mcp_server.list_resources()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "resources": [
                        {
                            "uri": str(r.uri),
                            "name": r.name,
                            "description": r.description,
                            "mimeType": r.mimeType or "text/plain"
                        }
                        for r in resources
                    ]
                }
            })

        elif method == "resources/read":
            uri = params.get("uri")
            with get_db() as db:
                if "course_descriptions" in uri:
                    text = get_course_descriptions_service(db)
                elif "department_directory" in uri:
                    text = get_department_directory_service(db)
                else:
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32602, "message": f"Resource not found: {uri}"}
                    })

            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "text/plain",
                            "text": text
                        }
                    ]
                }
            })

        elif method == "prompts/list":
            prompts = await mcp_server.list_prompts()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "prompts": [
                        {
                            "name": p.name,
                            "description": p.description,
                            "arguments": [
                                {
                                    "name": a.name,
                                    "description": a.description,
                                    "required": a.required
                                }
                                for a in (p.arguments or [])
                            ]
                        }
                        for p in prompts
                    ]
                }
            })

        elif method == "prompts/get":
            name = params.get("name")
            args = params.get("arguments", {})
            prompt_res = await mcp_server.get_prompt(name, args)
            messages_list = []
            for msg in prompt_res.messages:
                messages_list.append({
                    "role": msg.role,
                    "content": {
                        "type": "text",
                        "text": msg.content.text if hasattr(msg.content, "text") else str(msg.content)
                    }
                })
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "description": prompt_res.description,
                    "messages": messages_list
                }
            })

        elif method == "ping":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })

        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })

    except Exception as e:
        logger.error(f"Error handling JSON-RPC method {method}: {e}", exc_info=True)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }, status_code=500)


# ============================================================================
# Build ASGI Application
# ============================================================================

def create_app() -> Starlette:
    """Build and configure the Starlette application with FastMCP and REST routes."""
    # Ensure database is seeded on application initialization
    try:
        seed_database(force=False)
    except Exception as e:
        logger.warning(f"Initial seed check warning: {e}")

    # Register custom routes on FastMCP server
    @mcp_server.custom_route("/health", methods=["GET"])
    async def _health(request: Request):
        return await health_check(request)

    @mcp_server.custom_route("/", methods=["GET", "POST"])
    async def _root(request: Request):
        return await root_index(request)

    @mcp_server.custom_route("/jsonrpc", methods=["POST"])
    async def _jsonrpc(request: Request):
        return await handle_jsonrpc(request)

    @mcp_server.custom_route("/tools", methods=["GET"])
    async def _tools(request: Request):
        return await list_tools_endpoint(request)

    @mcp_server.custom_route("/tools/search_courses", methods=["GET", "POST"])
    async def _search_courses(request: Request):
        return await search_courses_endpoint(request)

    @mcp_server.custom_route("/search_courses", methods=["GET", "POST"])
    async def _search_courses_alias(request: Request):
        return await search_courses_endpoint(request)

    @mcp_server.custom_route("/tools/get_prerequisites", methods=["GET", "POST"])
    async def _get_prerequisites(request: Request):
        return await get_prerequisites_endpoint(request)

    @mcp_server.custom_route("/get_prerequisites", methods=["GET", "POST"])
    async def _get_prerequisites_alias(request: Request):
        return await get_prerequisites_endpoint(request)

    @mcp_server.custom_route("/tools/lookup_instructor", methods=["GET", "POST"])
    async def _lookup_instructor(request: Request):
        return await lookup_instructor_endpoint(request)

    @mcp_server.custom_route("/lookup_instructor", methods=["GET", "POST"])
    async def _lookup_instructor_alias(request: Request):
        return await lookup_instructor_endpoint(request)

    @mcp_server.custom_route("/tools/get_prerequisite_graph", methods=["GET", "POST"])
    async def _get_prerequisite_graph(request: Request):
        return await get_prerequisite_graph_endpoint(request)

    @mcp_server.custom_route("/get_prerequisite_graph", methods=["GET", "POST"])
    async def _get_prerequisite_graph_alias(request: Request):
        return await get_prerequisite_graph_endpoint(request)

    @mcp_server.custom_route("/resources", methods=["GET"])
    async def _resources(request: Request):
        return await list_resources_endpoint(request)

    @mcp_server.custom_route("/resources/course_descriptions", methods=["GET"])
    async def _course_desc(request: Request):
        return await course_descriptions_endpoint(request)

    @mcp_server.custom_route("/course_descriptions", methods=["GET"])
    async def _course_desc_alias(request: Request):
        return await course_descriptions_endpoint(request)

    @mcp_server.custom_route("/resources/department_directory", methods=["GET"])
    async def _dept_dir(request: Request):
        return await department_directory_endpoint(request)

    @mcp_server.custom_route("/department_directory", methods=["GET"])
    async def _dept_dir_alias(request: Request):
        return await department_directory_endpoint(request)

    @mcp_server.custom_route("/prompts", methods=["GET"])
    async def _prompts(request: Request):
        return await list_prompts_endpoint(request)

    @mcp_server.custom_route("/prompts/course_comparison_template", methods=["GET"])
    async def _course_comp(request: Request):
        return await course_comparison_template_endpoint(request)

    @mcp_server.custom_route("/course_comparison_template", methods=["GET"])
    async def _course_comp_alias(request: Request):
        return await course_comparison_template_endpoint(request)

    # Return the combined FastMCP SSE Starlette application
    return mcp_server.sse_app()


app = create_app()


def start():
    """Start the Uvicorn ASGI server."""
    logger.info(f"Starting University Catalog MCP Server on {HOST}:{PORT}...")
    uvicorn.run(app, host=HOST, port=PORT, log_level=LOG_LEVEL)


if __name__ == "__main__":
    start()
