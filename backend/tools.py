import json
import os
import re
import sqlite3
from pathlib import Path

if __package__:
    from .models import (
        ChatProductCard,
        ProductDetailsResult,
        ProductInventoryResult,
        ProductSearchResult,
        SizeStock,
    )
else:
    from models import (
        ChatProductCard,
        ProductDetailsResult,
        ProductInventoryResult,
        ProductSearchResult,
        SizeStock,
    )


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = Path(
    os.environ.get("CAMPUS_CUSTOMS_DB", PROJECT_ROOT / "data" / "campus_customs.db")
).expanduser()
STOP_WORDS = {
    "a", "an", "and", "are", "about", "available", "can", "cost", "do",
    "does", "for", "find", "from", "have", "how", "i", "in", "is", "it",
    "me", "much", "of", "please", "price", "prices", "quantity", "show",
    "some", "stock", "tell", "the", "there", "this", "that", "these", "they",
    "want", "what", "which", "with", "would", "you", "your", "size", "sizes",
    "units", "piece", "item", "product", "products", "inventory",
}
PLURAL_ALIASES = {
    "hoodies": "hoodie",
    "sweatshirts": "sweatshirt",
    "crewnecks": "crewneck",
    "jackets": "jacket",
    "sweaters": "sweater",
    "shirts": "shirt",
}
SIZE_NAMES = {
    "extra small": "XS",
    "x small": "XS",
    "small": "S",
    "medium": "M",
    "large": "L",
    "extra large": "XL",
    "x large": "XL",
    "xx large": "XXL",
    "double extra large": "XXL",
    "2xl": "XXL",
    "3xl": "XXXL",
}


def _parse_list(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def _tokens(value: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", value.casefold())
    normalized = []
    for token in tokens:
        if token in PLURAL_ALIASES:
            token = PLURAL_ALIASES[token]
        elif token.endswith("s") and not token.endswith("ss") and len(token) > 3:
            token = token[:-1]
        if len(token) > 1 and token not in STOP_WORDS:
            normalized.append(token)
    return normalized


VAGUE_TERMS = {
    "gift", "present", "something", "anything", "stuff", "thing", "things",
    "merch", "merchandise", "clothe", "clothing", "apparel", "gear", "wear",
    "nice", "cool", "warm", "cozy", "comfy", "cheap", "good", "best", "new",
    "recommendation", "recommend", "suggestion", "suggest", "idea", "help",
    "look", "browse", "shop", "buy", "need", "like", "yale", "campus", "custom",
}


def _connection() -> sqlite3.Connection:
    if not DATABASE_PATH.is_file():
        raise RuntimeError("The Campus Customs product database is unavailable.")
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


_catalogue_cache: dict[str, object] = {
    "file_key": None,
    "fingerprint": None,
    "rows": None,
    "inventory": None,
}

_FINGERPRINT_SQL = """
SELECT (SELECT COUNT(*) FROM catalogue),
       (SELECT COALESCE(SUM(price), 0) FROM catalogue),
       (SELECT COALESCE(MAX(rowid), 0) FROM catalogue),
       (SELECT COUNT(*) FROM inventory),
       (SELECT COALESCE(SUM(quantity), 0) FROM inventory),
       (SELECT COALESCE(MAX(rowid), 0) FROM inventory)
"""


def _catalogue_snapshot() -> tuple[list[sqlite3.Row], dict[str, list[SizeStock]]]:
    """Return the catalogue rows and inventory map, re-reading only when the product data changes.

    Two tiers, because the storefront writes chat messages into the same database file on
    every turn:

    1. If the file's size and modification time are unchanged, nothing at all was written,
       so the cached snapshot is served with no query.
    2. If the file did change, that was usually a `chat_messages` insert rather than a
       catalogue edit. Six indexed aggregates over `catalogue` and `inventory` are compared
       against the cached fingerprint; only a genuine product or stock change triggers the
       full re-read of every product plus every inventory row.

    Row counts, price sum, quantity sum, and max rowid together catch inserts, deletes,
    price edits, and stock movements. A text-only edit that changed a description while
    leaving all six aggregates identical would not be detected until the next real write;
    prices, stock, and the product list — the values the agent quotes — are always current.
    """
    if not DATABASE_PATH.is_file():
        raise RuntimeError("The Campus Customs product database is unavailable.")
    stat = DATABASE_PATH.stat()
    file_key = (stat.st_mtime_ns, stat.st_size)
    if _catalogue_cache["rows"] is not None and _catalogue_cache["file_key"] == file_key:
        return _catalogue_cache["rows"], _catalogue_cache["inventory"]  # type: ignore[return-value]

    connection = _connection()
    try:
        fingerprint = tuple(connection.execute(_FINGERPRINT_SQL).fetchone())
        if _catalogue_cache["rows"] is not None and _catalogue_cache["fingerprint"] == fingerprint:
            _catalogue_cache["file_key"] = file_key
            return _catalogue_cache["rows"], _catalogue_cache["inventory"]  # type: ignore[return-value]
        rows = connection.execute(
            """
            SELECT product_id, name, garment_type, description, colors,
                   search_tags, image_file_path, price
            FROM catalogue
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()
        inventory = _inventory_by_product(connection)
    finally:
        connection.close()

    _catalogue_cache.update(
        {"file_key": file_key, "fingerprint": fingerprint, "rows": rows, "inventory": inventory}
    )
    return rows, inventory


def _catalogue_facets(rows: list[sqlite3.Row]) -> tuple[list[str], tuple[float, float] | None]:
    """Summarize the real catalogue so a clarifying question can offer genuine options."""
    counts: dict[str, int] = {}
    prices: list[float] = []
    for row in rows:
        counts[row["garment_type"]] = counts.get(row["garment_type"], 0) + 1
        prices.append(float(row["price"]))
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold()))
    top_types = [name for name, _ in ranked[:6]]
    price_range = (min(prices), max(prices)) if prices else None
    return top_types, price_range


def _inventory_by_product(connection: sqlite3.Connection) -> dict[str, list[SizeStock]]:
    rows = connection.execute(
        "SELECT product_id, size, quantity FROM inventory ORDER BY id"
    ).fetchall()
    inventory: dict[str, list[SizeStock]] = {}
    for row in rows:
        inventory.setdefault(row["product_id"], []).append(
            SizeStock(size=row["size"], quantity=row["quantity"])
        )
    return inventory


def _product_card(row: sqlite3.Row, inventory: list[SizeStock]) -> ChatProductCard:
    filename = Path(row["image_file_path"]).name
    return ChatProductCard(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        price=row["price"],
        image_url=f"/media/products/{filename}",
        product_url=f"/products/{row['product_id']}",
        available_sizes=inventory,
        total_stock=sum(item.quantity for item in inventory),
    )


def search_products(query: str, browse: bool = False, limit: int = 30) -> ProductSearchResult:
    """Search the catalogue; use browse=True to return all matching category cards."""
    limit = max(1, min(limit, 30))
    products, inventory = _catalogue_snapshot()

    query_terms = set(_tokens(query))
    if not query_terms or query_terms <= VAGUE_TERMS:
        top_types, price_range = _catalogue_facets(products)
        readable = ", ".join(top_types[:4])
        return ProductSearchResult(
            query=query,
            status="needs_clarification",
            total_matches=0,
            clarification_question=(
                "Happy to help narrow it down. Are you after something like "
                f"{readable}? A garment type, a size, or who it's for is enough to go on."
            ),
            suggested_garment_types=top_types,
            price_range=price_range,
        )
    ranked: list[tuple[int, int, float, sqlite3.Row]] = []
    for row in products:
        colors = _parse_list(row["colors"])
        tags = _parse_list(row["search_tags"])
        name_terms = set(_tokens(row["name"]))
        searchable_terms = set(
            _tokens(" ".join([row["name"], row["garment_type"], row["description"], *colors, *tags]))
        )
        name_matches = len(query_terms & name_terms)
        text_matches = len(query_terms & searchable_terms)
        score = name_matches * 4 + (text_matches - name_matches)
        if score:
            coverage = name_matches / max(1, len(query_terms))
            ranked.append((score, name_matches, coverage, row))

    ranked.sort(key=lambda item: (-item[0], -item[1], item[3]["name"].casefold()))
    candidates = ranked[:limit]
    if not candidates:
        top_types, price_range = _catalogue_facets(products)
        return ProductSearchResult(
            query=query,
            status="no_match",
            total_matches=0,
            clarification_question=(
                "I couldn't match that to a catalogue item. We do carry "
                f"{', '.join(top_types[:4])} — would one of those work, or is there "
                "another product name I should look up?"
            ),
            suggested_garment_types=top_types,
            price_range=price_range,
        )

    total_matches = len(ranked)
    if browse:
        selected = [row for _, _, _, row in candidates]
        cards = [_product_card(row, inventory.get(row["product_id"], [])) for row in selected]
        return ProductSearchResult(
            query=query,
            status="browse_results",
            matches=cards,
            total_matches=total_matches,
        )

    best_score, best_name_matches, best_coverage, best_row = candidates[0]
    second_score = candidates[1][0] if len(candidates) > 1 else 0
    normalized_query = " ".join(_tokens(query))
    normalized_name = " ".join(_tokens(best_row["name"]))
    exact_name = bool(normalized_name and normalized_name in normalized_query)
    unique_match = exact_name or (
        len(query_terms) >= 2
        and best_name_matches >= 2
        and best_coverage >= 0.5
        and best_score - second_score >= 3
    )
    if unique_match:
        selected = [best_row]
        status = "unique_match"
        question = None
        product_id = best_row["product_id"]
    else:
        selected = [row for _, _, _, row in candidates]
        status = "ambiguous"
        names = ", ".join(row["name"] for row in selected[:3])
        question = f"Which product did you mean: {names}?"
        product_id = None

    cards = [_product_card(row, inventory.get(row["product_id"], [])) for row in selected]
    return ProductSearchResult(
        query=query,
        status=status,
        matched_product_id=product_id,
        matches=cards,
        total_matches=total_matches,
        clarification_question=question,
    )


def get_product_details(product_id: str) -> ProductDetailsResult:
    """Retrieve the exact catalogue description, price, colors, tags, and image for a product ID."""
    connection = _connection()
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
    if row is None:
        return ProductDetailsResult(found=False, message="No catalogue product exists with that ID.")
    filename = Path(row["image_file_path"]).name
    return ProductDetailsResult(
        found=True,
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=_parse_list(row["colors"]),
        search_tags=_parse_list(row["search_tags"]),
        price=row["price"],
        image_url=f"/media/products/{filename}",
        message="Product details retrieved from the catalogue.",
    )


def _normalize_size(size: str) -> str:
    normalized = " ".join(re.findall(r"[a-z0-9]+", size.casefold()))
    if normalized in SIZE_NAMES:
        return SIZE_NAMES[normalized]
    compact = normalized.replace(" ", "").upper()
    return compact


def get_product_inventory(product_id: str, size: str | None = None) -> ProductInventoryResult:
    """Retrieve current total stock or the exact quantity and availability for one size."""
    connection = _connection()
    try:
        product = connection.execute(
            "SELECT product_id, name FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if product is None:
            return ProductInventoryResult(
                status="product_not_found",
                requested_size=size,
                message="No catalogue product exists with that ID; inventory was not checked.",
            )
        rows = connection.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id",
            (product_id,),
        ).fetchall()
    finally:
        connection.close()

    inventory = [SizeStock(size=row["size"], quantity=row["quantity"]) for row in rows]
    total_stock = sum(item.quantity for item in inventory)
    if size is None:
        return ProductInventoryResult(
            status="found",
            product_id=product_id,
            product_name=product["name"],
            inventory=inventory,
            total_stock=total_stock,
            message=f"Current inventory retrieved for {product['name']}.",
        )

    requested_size = _normalize_size(size)
    matched = next((item for item in inventory if item.size.upper() == requested_size), None)
    if matched is None:
        return ProductInventoryResult(
            status="size_not_carried",
            product_id=product_id,
            product_name=product["name"],
            requested_size=requested_size,
            available=False,
            inventory=inventory,
            total_stock=total_stock,
            message=f"{product['name']} does not list size {requested_size} in inventory.",
        )

    out_of_stock = matched.quantity == 0
    return ProductInventoryResult(
        status="found",
        product_id=product_id,
        product_name=product["name"],
        requested_size=requested_size,
        matched_size=matched.size,
        quantity=matched.quantity,
        available=matched.quantity > 0,
        out_of_stock=out_of_stock,
        inventory=inventory,
        total_stock=total_stock,
        message=(
            f"Size {matched.size} is currently out of stock (0 units)."
            if out_of_stock
            else f"Size {matched.size} has {matched.quantity} unit(s) in stock."
        ),
    )
