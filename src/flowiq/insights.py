"""
insights.py

Why it exists:
    Turns SQL analytics output (numbers) into a plain-language business
    recommendation. This is the ONLY module that talks to an LLM.

What problem it solves:
    Business stakeholders don't want a table of numbers, they want a
    sentence like "Finance Review causes the longest delay in Invoice
    Approval, averaging 18.3 hours -- consider adding a second approver
    for low-value invoices." That phrasing is what an LLM is good at;
    the underlying 18.3-hour figure comes from analytics.py, not the LLM.
    The LLM is never given raw tables or asked to compute anything --
    only to explain numbers that SQL already produced.

Inputs:
    report_name: which report was run (e.g. "bottlenecks", "sla")
    rows: the list[dict] returned by the matching analytics.py function

Outputs:
    A short (2-3 sentence) natural-language business recommendation.

Note: requires GEMINI_API_KEY (or OPENROUTER_API_KEY) in .env.
Uncomment the matching import/client below based on which you use --
see requirements.txt for the matching package.
"""

import os

from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATE = """You are a business process analyst. Given the following
{report_name} data from a workflow analytics system, write a 2-3 sentence
recommendation for operations leadership. Be specific -- cite the numbers
given. Do not invent numbers that aren't in the data below.

Data:
{data}

Recommendation:"""


def summarize(report_name: str, rows: list[dict]) -> str:
    """Send analytics results to an LLM and return a short recommendation."""
    # --- Gemini via LangChain ---
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=os.environ["GEMINI_API_KEY"],
    )

    # --- OpenRouter via LangChain (OpenAI-compatible) -- use instead of the above ---
    # from langchain_openai import ChatOpenAI
    # llm = ChatOpenAI(
    #     model="openrouter/auto",
    #     openai_api_key=os.environ["OPENROUTER_API_KEY"],
    #     openai_api_base="https://openrouter.ai/api/v1",
    # )

    prompt = PROMPT_TEMPLATE.format(report_name=report_name, data=rows)
    response = llm.invoke(prompt)
    return response.content
