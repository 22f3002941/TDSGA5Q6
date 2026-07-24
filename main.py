import os
import hashlib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from mcp.server.fastmcp import FastMCP

EMAIL = "22f3002941@ds.study.iitm.ac.in"

mcp = FastMCP("exam-mcp-server")
app = FastAPI()


@mcp.tool(name="solve_challenge")
async def solve_challenge() -> str:
    return "ok"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.api_route("/mcp", methods=["GET", "POST"])
async def mcp_endpoint(request: Request):
    challenge = request.headers.get("x-exam-challenge")
    timestamp = request.headers.get("x-exam-timestamp")
    signature = request.headers.get("x-exam-signature")

    body = await request.body()

    if request.method == "GET":
        return Response(status_code=200)

    if challenge is None:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": None, "error": {"code": -32602, "message": "Missing X-Exam-Challenge header"}},
            status_code=400,
        )

    if body:
        try:
            payload = await request.json()
        except Exception:
            payload = None
    else:
        payload = None

    if not payload or payload.get("method") != "tools/call":
        return await _handle_mcp_request(request, payload)

    result = hashlib.sha256(f"{challenge}:{EMAIL}".encode("utf-8")).hexdigest()[:16]

    return JSONResponse(
        {
            "jsonrpc": "2.0",
            "id": payload.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result,
                    }
                ]
            },
        }
    )


async def _handle_mcp_request(request: Request, payload):
    if payload is None:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
            status_code=400,
        )

    method = payload.get("method")
    req_id = payload.get("id")

    if method == "initialize":
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "serverInfo": {"name": "exam-mcp-server", "version": "1.0.0"},
                    "capabilities": {"tools": {}},
                },
            }
        )

    if method == "notifications/initialized":
        return Response(status_code=204)

    if method == "tools/list":
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "solve_challenge",
                            "description": "Solve the exam challenge from request headers.",
                            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
                        }
                    ]
                },
            }
        )

    if method == "tools/call":
        challenge = request.headers.get("x-exam-challenge")
        if not challenge:
            return JSONResponse(
                {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing X-Exam-Challenge header"}},
                status_code=400,
            )

        result = hashlib.sha256(f"{challenge}:{EMAIL}".encode("utf-8")).hexdigest()[:16]

        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result,
                        }
                    ]
                },
            }
        )

    return JSONResponse(
        {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}},
        status_code=400,
    )