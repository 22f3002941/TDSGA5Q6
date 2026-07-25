import hashlib
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request

EMAIL = "22f3002941@ds.study.iitm.ac.in"
mcp = FastMCP("exam-mcp-server")


@mcp.tool(name="solve_challenge")
async def solve_challenge() -> str:
    request = get_http_request()  # Starlette Request for the current call
    if request is None:
        raise RuntimeError("HTTP request context not available")

    challenge = request.headers.get("x-exam-challenge")
    if not challenge:
        raise RuntimeError("Missing X-Exam-Challenge header")

    normalized_email = EMAIL.strip().lower()
    digest = hashlib.sha256(f"{challenge}:{normalized_email}".encode("utf-8")).hexdigest()
    return digest[:16]


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)