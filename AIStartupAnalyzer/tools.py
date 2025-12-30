import os
import httpx
from agents import function_tool


@function_tool
def search_startup_info(query: str, num_results: int = 8) -> str:
    """Search web for startup info via Serper API (funding, competitors, news)."""
    
    response = httpx.post(
        "https://google.serper.dev/search",
        json={"q": query, "num": num_results},
        headers={
            "X-API-KEY": os.environ["SERPER_API_KEY"],
            "Content-Type": "application/json"
        },
        timeout=10.0
    )
    response.raise_for_status()
    
    results = response.json().get("organic", [])
    
    formatted_results = "\n".join(
        f"{i}. {r.get('title', 'No title')}\n"
        f"   {r.get('link', '')}\n"
        f"   {r.get('snippet', '')}\n"
        f"   {r.get('date', '')}"
        for i, r in enumerate(results, 1)
    )
    
    return f"Search: {query}\n{'='*50}\n\n{formatted_results}"
