import asyncio
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

if __package__:
    from . import audit
    from .agent import AgentConfigurationError, answer_chat
    from .models import (
        AgentCustomerContext,
        AgentPageContext,
        ChatAgentContext,
        ChatHistoryMessage,
        ChatHistoryResponse,
        ChatProductCard,
        ChatRequest,
        ChatResponse,
        ChatTurn,
        ProductDetailsResult,
    )
else:
    import audit
    from agent import AgentConfigurationError, answer_chat
    from models import (
        AgentCustomerContext,
        AgentPageContext,
        ChatAgentContext,
        ChatHistoryMessage,
        ChatHistoryResponse,
        ChatProductCard,
        ChatRequest,
        ChatResponse,
        ChatTurn,
        ProductDetailsResult,
    )


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(
    os.environ.get("CAMPUS_CUSTOMS_DB", PROJECT_ROOT / "data" / "campus_customs.db")
).expanduser()
PRODUCT_IMAGE_DIR = PROJECT_ROOT / "public" / "products"
SESSION_COOKIE = "campus_customs_session"
SESSION_LIFETIME = timedelta(days=30)
CHAT_TIMEOUT_SECONDS = float(os.environ.get("CAMPUS_CUSTOMS_CHAT_TIMEOUT", "60"))
CHAT_RATE_LIMIT = int(os.environ.get("CAMPUS_CUSTOMS_CHAT_RATE_LIMIT", "12"))
CHAT_RATE_WINDOW_SECONDS = float(os.environ.get("CAMPUS_CUSTOMS_CHAT_RATE_WINDOW", "60"))


class InventoryItem(BaseModel):
    size: str
    quantity: int


class Product(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str]
    image_file_path: str
    image_url: str
    price: float
    inventory: list[InventoryItem]
    total_stock: int


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name fields cannot be blank.")
        return normalized

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class PublicUser(BaseModel):
    id: int
    name: str
    email: str
    created_at: str
    first_name: str | None = None
    last_name: str | None = None


class AuthResponse(BaseModel):
    message: str
    user: PublicUser


@asynccontextmanager
async def lifespan(_: FastAPI):
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_nocase "
            "ON users(email COLLATE NOCASE)"
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id)"
        )
        connection.commit()
    finally:
        connection.close()
    yield


app = FastAPI(title="Campus Customs API", version="1.0.0", lifespan=lifespan)
allowed_origins = os.environ.get(
    "CAMPUS_CUSTOMS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/media/products", StaticFiles(directory=PRODUCT_IMAGE_DIR), name="product-images")


def connect_database() -> sqlite3.Connection:
    if not DATABASE_PATH.is_file():
        raise HTTPException(status_code=503, detail="The product database is unavailable.")
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def parse_json_list(value: str) -> list[str]:
    try:
        parsed: Any = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
    return parsed if isinstance(parsed, list) else []


def product_from_row(row: sqlite3.Row, inventory: list[InventoryItem]) -> Product:
    image_path = row["image_file_path"]
    filename = Path(image_path).name
    return Product(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=parse_json_list(row["colors"]),
        search_tags=parse_json_list(row["search_tags"]),
        image_file_path=image_path,
        image_url=f"/media/products/{filename}",
        price=row["price"],
        inventory=inventory,
        total_stock=sum(item.quantity for item in inventory),
    )


def get_inventory(connection: sqlite3.Connection) -> dict[str, list[InventoryItem]]:
    rows = connection.execute(
        "SELECT product_id, size, quantity FROM inventory ORDER BY id"
    ).fetchall()
    inventory: dict[str, list[InventoryItem]] = {}
    for row in rows:
        inventory.setdefault(row["product_id"], []).append(
            InventoryItem(size=row["size"], quantity=row["quantity"])
        )
    return inventory


def hash_password(password: str) -> str:
    iterations = 600_000
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("ascii"), iterations
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, encoded_hash: str) -> bool:
    parts = encoded_hash.split("$")
    if len(parts) == 3 and parts[0] == "pbkdf2_sha256":
        _, salt, expected = parts
        iterations = 120_000
    elif len(parts) == 4 and parts[0] == "pbkdf2_sha256":
        _, iteration_text, salt, expected = parts
        try:
            iterations = int(iteration_text)
        except ValueError:
            return False
    else:
        return False

    if iterations < 1 or len(expected) != 64:
        return False
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("ascii"), iterations
    ).hex()
    return hmac.compare_digest(actual, expected)


def public_user(row: sqlite3.Row) -> PublicUser:
    return PublicUser(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        created_at=row["created_at"],
        first_name=row["first_name"],
        last_name=row["last_name"],
    )


def session_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(connection: sqlite3.Connection, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + SESSION_LIFETIME).replace(tzinfo=None).isoformat(
        sep=" ", timespec="seconds"
    )
    connection.execute(
        "INSERT INTO auth_sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (session_token_hash(token), user_id, expires_at),
    )
    return token


def attach_session_cookie(response: Response, request: Request, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(SESSION_LIFETIME.total_seconds()),
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/",
    )


def resolve_session_user(request: Request, required: bool = False) -> sqlite3.Row | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        if required:
            raise HTTPException(status_code=401, detail="Please log in to access this conversation.")
        return None
    connection = connect_database()
    try:
        user = connection.execute(
            """
            SELECT users.id, users.name, users.email, users.created_at,
                   users.first_name, users.last_name
            FROM auth_sessions
            JOIN users ON users.id = auth_sessions.user_id
            WHERE auth_sessions.token_hash = ?
              AND auth_sessions.expires_at > datetime('now')
            """,
            (session_token_hash(token),),
        ).fetchone()
    finally:
        connection.close()
    if user is None and required:
        raise HTTPException(status_code=401, detail="Your session is invalid or expired. Please log in again.")
    return user


def resolve_page_context(path: str, product_id: str | None) -> AgentPageContext:
    if product_id and path == f"/products/{product_id}":
        connection = connect_database()
        try:
            row = connection.execute(
                """
                SELECT product_id, name, garment_type, description, colors,
                       search_tags, image_file_path, price
                FROM catalogue WHERE product_id = ?
                """,
                (product_id,),
            ).fetchone()
        finally:
            connection.close()
        if row is not None:
            filename = Path(row["image_file_path"]).name
            return AgentPageContext(
                current_path=path,
                page_type="product",
                product=ProductDetailsResult(
                    found=True,
                    product_id=row["product_id"],
                    name=row["name"],
                    garment_type=row["garment_type"],
                    description=row["description"],
                    colors=parse_json_list(row["colors"]),
                    search_tags=parse_json_list(row["search_tags"]),
                    price=row["price"],
                    image_url=f"/media/products/{filename}",
                    message="Current product loaded from the catalogue.",
                ),
            )
    if path == "/":
        page_type = "home"
    elif path == "/products":
        page_type = "catalogue"
    elif path in {"/login", "/create-account"}:
        page_type = "account"
    elif path == "/about":
        page_type = "about"
    else:
        page_type = "other"
    return AgentPageContext(current_path=path, page_type=page_type)


_chat_rate_log: dict[str, deque[float]] = {}


def chat_rate_limit_key(request: Request) -> str:
    """Identify the caller for rate limiting: the session if signed in, otherwise the client IP.

    The session token is hashed rather than stored, so the limiter never holds a usable
    credential in memory.
    """
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        return f"session:{session_token_hash(token)}"
    client = request.client
    return f"ip:{client.host if client else 'unknown'}"


def enforce_chat_rate_limit(key: str) -> None:
    """Allow CHAT_RATE_LIMIT agent calls per caller per rolling window, then return 429.

    Each agent call costs a paid model request, so an accidental render loop or a scripted
    flood would otherwise run up cost and slow every other shopper's replies.
    """
    now = time.monotonic()
    log = _chat_rate_log.setdefault(key, deque())
    while log and now - log[0] > CHAT_RATE_WINDOW_SECONDS:
        log.popleft()
    if not log:
        # Drop callers that have gone quiet so the limiter's memory stays bounded.
        for stale_key in [k for k, v in _chat_rate_log.items() if not v and k != key]:
            del _chat_rate_log[stale_key]
    if len(log) >= CHAT_RATE_LIMIT:
        retry_after = max(1, int(CHAT_RATE_WINDOW_SECONDS - (now - log[0])) + 1)
        raise HTTPException(
            status_code=429,
            detail="You're sending messages faster than the assistant can answer. Please wait a moment and try again.",
            headers={"Retry-After": str(retry_after)},
        )
    log.append(now)


def persisted_agent_history(user_id: int, limit: int = 12) -> list[ChatTurn]:
    connection = connect_database()
    try:
        rows = connection.execute(
            "SELECT role, content FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        connection.close()
    return [ChatTurn(role=row["role"], content=row["content"]) for row in reversed(rows)]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    run_id = audit.new_run_id()
    try:
        enforce_chat_rate_limit(chat_rate_limit_key(request))
    except HTTPException:
        audit.record_run(
            run_id=run_id,
            message=payload.message,
            stop_reason="rate_limited",
            page_path=payload.page_context.current_path,
        )
        raise
    user = resolve_session_user(request)
    customer = None
    if user is not None:
        customer = AgentCustomerContext(
            user_id=user["id"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
        )
        history = persisted_agent_history(user["id"])
    else:
        history = payload.history
    context = ChatAgentContext(
        customer=customer,
        page=resolve_page_context(payload.page_context.current_path, payload.page_context.product_id),
    )
    try:
        result = await asyncio.wait_for(
            answer_chat(payload.message, history, context, run_id=run_id),
            timeout=CHAT_TIMEOUT_SECONDS,
        )
    except AgentConfigurationError as exc:
        audit.record_run(
            run_id=run_id,
            message=payload.message,
            stop_reason="agent_not_configured",
            authenticated_user_id=customer.user_id if customer else None,
            page_path=context.page.current_path,
            page_type=context.page.page_type,
        )
        raise HTTPException(status_code=503, detail=str(exc)) from None
    except asyncio.TimeoutError:
        audit.record_run(
            run_id=run_id,
            message=payload.message,
            stop_reason="timeout",
            authenticated_user_id=customer.user_id if customer else None,
            page_path=context.page.current_path,
            page_type=context.page.page_type,
            duration_ms=int(CHAT_TIMEOUT_SECONDS * 1000),
        )
        raise HTTPException(
            status_code=504,
            detail="The assistant took too long to respond. Please try that question again.",
        ) from None
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The Campus Customs assistant could not complete that request. Please try again.",
        ) from exc

    if user is not None:
        connection = connect_database()
        try:
            connection.executemany(
                "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
                [
                    (user["id"], "user", payload.message, None),
                    (
                        user["id"],
                        "assistant",
                        result.message,
                        json.dumps([product.model_dump() for product in result.products]),
                    ),
                ],
            )
            connection.commit()
        finally:
            connection.close()
    return result


@app.get("/api/chat/history", response_model=ChatHistoryResponse)
def get_chat_history(request: Request) -> ChatHistoryResponse:
    user = resolve_session_user(request, required=True)
    connection = connect_database()
    try:
        rows = connection.execute(
            """
            SELECT role, content, products_json, created_at
            FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 100
            """,
            (user["id"],),
        ).fetchall()
    finally:
        connection.close()

    messages: list[ChatHistoryMessage] = []
    for row in reversed(rows):
        if row["role"] not in {"user", "assistant"}:
            continue
        products: list[ChatProductCard] = []
        if row["products_json"]:
            try:
                parsed = json.loads(row["products_json"])
                if isinstance(parsed, list):
                    products = [ChatProductCard.model_validate(item) for item in parsed]
            except (json.JSONDecodeError, TypeError, ValueError):
                products = []
        messages.append(
            ChatHistoryMessage(
                role=row["role"],
                content=row["content"],
                products=products,
                created_at=row["created_at"],
            )
        )
    return ChatHistoryResponse(messages=messages)


@app.get("/api/auth/me", response_model=PublicUser)
def current_user(request: Request) -> PublicUser:
    return public_user(resolve_session_user(request, required=True))


@app.post("/api/auth/logout")
def logout(request: Request, response: Response) -> dict[str, str]:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        connection = connect_database()
        try:
            connection.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (session_token_hash(token),))
            connection.commit()
        finally:
            connection.close()
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax")
    return {"message": "Logged out."}


@app.post("/api/auth/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, request: Request, response: Response) -> AuthResponse:
    email = str(payload.email).casefold()
    name = f"{payload.first_name} {payload.last_name}"
    connection = connect_database()
    try:
        existing = connection.execute(
            "SELECT 1 FROM users WHERE email = ? COLLATE NOCASE", (email,)
        ).fetchone()
        if existing is not None:
            raise HTTPException(
                status_code=409, detail="An account with this email already exists."
            )
        try:
            cursor = connection.execute(
                """
                INSERT INTO users (name, email, password_hash, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    hash_password(payload.password),
                    payload.first_name,
                    payload.last_name,
                ),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            connection.rollback()
            raise HTTPException(
                status_code=409, detail="An account with this email already exists."
            ) from None

        row = connection.execute(
            """
            SELECT id, name, email, created_at, first_name, last_name
            FROM users WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        session_token = create_session(connection, row["id"])
        connection.commit()
        attach_session_cookie(response, request, session_token)
        return AuthResponse(message="Account created successfully.", user=public_user(row))
    finally:
        connection.close()


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, response: Response) -> AuthResponse:
    email = str(payload.email).casefold()
    connection = connect_database()
    try:
        row = connection.execute(
            """
            SELECT id, name, email, created_at, first_name, last_name, password_hash
            FROM users WHERE email = ? COLLATE NOCASE
            """,
            (email,),
        ).fetchone()
        if row is None or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        session_token = create_session(connection, row["id"])
        connection.commit()
        attach_session_cookie(response, request, session_token)
        return AuthResponse(message="Login successful.", user=public_user(row))
    finally:
        connection.close()


@app.get("/api/products", response_model=list[Product])
def list_products() -> list[Product]:
    connection = connect_database()
    try:
        rows = connection.execute(
            """
            SELECT product_id, name, garment_type, description, colors,
                   search_tags, image_file_path, price
            FROM catalogue
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()
        inventory = get_inventory(connection)
        return [
            product_from_row(row, inventory.get(row["product_id"], []))
            for row in rows
        ]
    finally:
        connection.close()


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> Product:
    connection = connect_database()
    try:
        row = connection.execute(
            """
            SELECT product_id, name, garment_type, description, colors,
                   search_tags, image_file_path, price
            FROM catalogue
            WHERE product_id = ?
            """,
            (product_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found.")
        inventory = get_inventory(connection)
        return product_from_row(row, inventory.get(product_id, []))
    finally:
        connection.close()