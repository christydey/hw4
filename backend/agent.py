import os
import time
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

if __package__:
    from . import audit
    from .models import ChatAgentContext, ChatResponse, ChatTurn
    from .tools import get_product_details, get_product_inventory, search_products
else:
    import audit
    from models import ChatAgentContext, ChatResponse, ChatTurn
    from tools import get_product_details, get_product_inventory, search_products


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
PROMPT_FILE = BACKEND_DIR / "prompts" / "prompt.md"
PROJECT_ENV_FILE = PROJECT_ROOT.parents[1] / ".env"


class AgentConfigurationError(RuntimeError):
    pass


def _conversation_input(message: str, history: list[ChatTurn]) -> str:
    if not history:
        return message
    recent_history = history[-12:]
    transcript = "\n".join(
        f"{turn.role}: {turn.content}" for turn in recent_history
    )
    return f"Recent conversation:\n{transcript}\n\nShopper's latest message:\n{message}"


@lru_cache(maxsize=1)
def build_agent() -> Agent[ChatAgentContext, ChatResponse]:
    load_dotenv(PROJECT_ENV_FILE)
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise AgentConfigurationError(
            "PORTKEY_API_KEY is required. Configure it in the project root .env file or export it in the environment."
        )

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.portkey.ai/v1",
        default_headers={
            "x-portkey-api-key": api_key,
            "x-portkey-provider": "openai",
        },
    )
    model = OpenAIChatModel(
        os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        provider=OpenAIProvider(openai_client=client),
    )
    return Agent(
        model=model,
        instructions=_contextual_instructions,
        deps_type=ChatAgentContext,
        output_type=ChatResponse,
        tools=[search_products, get_product_details, get_product_inventory],
        retries=1,
    )


def _contextual_instructions(ctx: RunContext[ChatAgentContext]) -> str:
    context = ctx.deps
    lines = [PROMPT_FILE.read_text(encoding="utf-8"), "\n## Current request context"]
    customer = context.customer
    if customer is not None:
        lines.append(
            "Authenticated shopper (verified by the server): "
            f"first_name={customer.first_name or 'not provided'}, "
            f"last_name={customer.last_name or 'not provided'}, "
            f"email={customer.email}, internal_user_id={customer.user_id}."
        )
        lines.append("Use the shopper's first name naturally when helpful. Never reveal internal IDs or account data to other users.")
    else:
        lines.append("The shopper is a guest; no account identity is available.")

    page = context.page
    lines.append(f"Current page: {page.current_path} (type: {page.page_type}).")
    if page.product is not None and page.product.found:
        lines.append(
            "The shopper is viewing this database-verified product. For references such as "
            "'this' or 'it', use this product ID for database detail or inventory tools: "
            + page.product.model_dump_json(exclude_none=True)
        )
    else:
        lines.append("No single product is currently selected on the page.")
    return "\n".join(lines)


MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
# PydanticAI stops the loop once the model returns its structured output; `retries=1` allows a
# single retry per tool call if the model produces arguments the tool rejects.
AGENT_TOOL_RETRIES = 1


async def answer_chat(
    message: str,
    history: list[ChatTurn],
    context: ChatAgentContext,
    run_id: str | None = None,
) -> ChatResponse:
    run_id = run_id or audit.new_run_id()
    started = time.perf_counter()
    try:
        result = await build_agent().run(
            _conversation_input(message, history),
            deps=context,
        )
    except Exception as exc:
        audit.record_run(
            run_id=run_id,
            message=message,
            stop_reason="agent_error",
            authenticated_user_id=context.customer.user_id if context.customer else None,
            page_path=context.page.current_path,
            page_type=context.page.page_type,
            model=os.getenv("OPENAI_MODEL", MODEL_NAME),
            duration_ms=int((time.perf_counter() - started) * 1000),
            error=f"{type(exc).__name__}: {exc}",
        )
        raise

    output = result.output
    audit.record_run(
        run_id=run_id,
        message=message,
        stop_reason="completed",
        tool_calls=audit.extract_tool_calls(result.all_messages()),
        authenticated_user_id=context.customer.user_id if context.customer else None,
        page_path=context.page.current_path,
        page_type=context.page.page_type,
        model=os.getenv("OPENAI_MODEL", MODEL_NAME),
        duration_ms=int((time.perf_counter() - started) * 1000),
        response_preview=output.message,
        product_card_count=len(output.products),
    )
    return output
