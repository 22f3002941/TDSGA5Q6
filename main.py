import hashlib
from typing import Any

from fastmcp import FastMCP
from starlette.requests import Request

EMAIL = "22f3002941@ds.study.iitm.ac.in"

mcp = FastMCP("exam-mcp-server")


def _challenge_from_request_context() -> str:
    ctx = mcp.get_context()
    request = getattr(ctx, "request", None)
    if request is None:
        raise ValueError("No HTTP request context available")
    challenge = request.headers.get("x-exam-challenge")
    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")
    return challenge


@mcp.tool(name="solve_challenge")
def solve_challenge() -> str:
    challenge = _challenge_from_request_context().strip()
    normalized_email = EMAIL.strip().lower()
    return hashlib.sha256(f"{challenge}:{normalized_email}".encode("utf-8")).hexdigest()[:16]


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)