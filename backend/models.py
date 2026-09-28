from typing import Literal

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    size: str
    quantity: int


class ChatProductCard(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    price: float
    image_url: str
    product_url: str
    available_sizes: list[SizeStock] = Field(default_factory=list)
    total_stock: int


class ProductSearchResult(BaseModel):
    query: str
    status: Literal[
        "unique_match",
        "ambiguous",
        "browse_results",
        "no_match",
        "needs_clarification",
    ]
    matched_product_id: str | None = None
    matches: list[ChatProductCard] = Field(default_factory=list)
    total_matches: int = 0
    clarification_question: str | None = None
    suggested_garment_types: list[str] = Field(default_factory=list)
    price_range: tuple[float, float] | None = None


class ProductDetailsResult(BaseModel):
    found: bool
    product_id: str | None = None
    name: str | None = None
    garment_type: str | None = None
    description: str | None = None
    colors: list[str] = Field(default_factory=list)
    search_tags: list[str] = Field(default_factory=list)
    price: float | None = None
    image_url: str | None = None
    message: str


class ProductInventoryResult(BaseModel):
    status: Literal["found", "product_not_found", "size_not_carried"]
    product_id: str | None = None
    product_name: str | None = None
    requested_size: str | None = None
    matched_size: str | None = None
    quantity: int | None = None
    available: bool | None = None
    out_of_stock: bool = False
    inventory: list[SizeStock] = Field(default_factory=list)
    total_stock: int = 0
    message: str


class ChatPageContext(BaseModel):
    current_path: str = Field(default="/", max_length=500)
    product_id: str | None = Field(default=None, max_length=200)


class AgentPageContext(BaseModel):
    current_path: str
    page_type: Literal["home", "catalogue", "product", "account", "about", "other"]
    product: ProductDetailsResult | None = None


class AgentCustomerContext(BaseModel):
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    email: str


class ChatAgentContext(BaseModel):
    customer: AgentCustomerContext | None = None
    page: AgentPageContext


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1200)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1200)
    history: list[ChatTurn] = Field(default_factory=list, max_length=12)
    page_context: ChatPageContext = Field(default_factory=ChatPageContext)


class ChatResponse(BaseModel):
    message: str = Field(min_length=1)
    products: list[ChatProductCard] = Field(default_factory=list)


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    products: list[ChatProductCard] = Field(default_factory=list)
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryMessage] = Field(default_factory=list)
