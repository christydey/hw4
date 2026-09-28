# Campus Customs Usability Improvements (Problem 9)

Four improvements were added to the running application: two on the front end and two in the
agent/backend. Everything from Problems 1–8 was preserved and re-tested afterwards.

Two servers must be running to test any of these:

```sh
# terminal 1
cd homeworks/hwv4/backend && uvicorn main:app --reload --port 8000
# terminal 2
cd homeworks/hwv4 && npm run dev
```

---

## 1. Size, color, and availability filters with shareable URLs

**Type:** Front end

### What was added

The Products page already had a text search, a garment-type dropdown, and a price sort. Three
filters were added alongside them, all built from real `campus_customs.db` values:

- **Size** — the six sizes that actually appear in the `inventory` table (XS, S, M, L, XL, XXL).
  A product matches only when that size has `quantity > 0`, so a sold-out size hides the product
  rather than disappointing the shopper on the detail page.
- **Color** — the 22 distinct values across `catalogue.colors`.
- **All sizes in stock** — a toggle that keeps only products with no sold-out size.

Every filter is stored in the URL query string (`/products?type=pullover+hoodie&size=M&color=navy+blue`)
rather than in component state, so a filtered view survives a page reload, works with the browser
back button, and can be pasted to someone else. Active filters appear as removable chips beneath
the toolbar, with a "Clear all" control, and the result counter reads "14 PIECES OF 102" so the
shopper can see how much of the catalogue is hidden.

### Why it helps

The catalogue holds 102 products and 145 individual sizes are sold out. Before this change, a
shopper who wears size M had no way to ask "what can I actually buy in my size?" — they had to
open products one at a time to find out. Filtering by size cuts the pullover-hoodie category from
18 products to the 14 genuinely available in M. For the business, a shareable filtered URL is a
link worth sending to a friend or posting, and fewer clicks into out-of-stock items means fewer
abandoned sessions.

### Files changed

- `src/App.tsx` — `ProductsPage` rewritten to read and write filters through `useSearchParams`
- `src/App.css` — `.stock-toggle`, `.filter-chips`, `.filter-chip`, `.filter-clear`

### How to test

1. Open `http://localhost:5173/products` — the counter reads **102 PIECES**.
2. Choose **pullover hoodie** from the type dropdown → 18 results.
3. Add **M** from the size dropdown → **14 results**, and two filter chips appear.
4. Add **navy blue** from the color dropdown → 11 results.
5. Reload the page. The filters and results are unchanged, because they are in the URL.
6. Press the browser back button — the previous filter combination returns.
7. Click the **×** on a chip to drop one filter, or **Clear all** to reset to 102.
8. Turn on **All sizes in stock** with no other filters → **25 of 102** products remain.
9. Click any surviving card — the Problem 3 detail page opens exactly as before.

---

## 2. Chat widget loading, error, and duplicate-submission handling

**Type:** Front end

### What was added

- **Animated typing indicator.** The pending state now shows three pulsing dots next to
  "Checking the collection…" inside a `role="status"` region, and the message list carries
  `aria-busy`, so screen readers announce that a reply is coming.
- **Errors look like errors.** Previously a failure was pushed into the transcript as an ordinary
  assistant bubble, so "The assistant could not respond right now" appeared to be something the
  chatbot said. Failures now render in a distinct pink-bordered bubble headed "MESSAGE NOT SENT"
  with `role="alert"`, and they are excluded from the history sent on the next request.
- **A retry button.** The failed message is remembered and can be resent with one click; the retry
  clears the error bubble rather than stacking another copy of the question.
- **Specific messages per failure.** HTTP 429, 502, 503, and 504 each map to plain-language text,
  and network failures and client-side timeouts are distinguished from server errors.
- **Duplicate submissions blocked.** The input is disabled while a reply is in flight, the send
  button shows a spinner, and submission is guarded by a `useRef` rather than the `pending` state.
  React state updates are asynchronous, so two fast submits could previously both observe
  `pending === false` and fire two paid agent calls; a ref updates synchronously and cannot.
- **A client-side timeout.** An `AbortController` gives up after 65 seconds — deliberately longer
  than the backend's own 60-second agent timeout, so a server-side 504 surfaces its specific
  message instead of being masked by the browser giving up first.

### Why it helps

An agent call that runs several database tools can take a few seconds. Without visible feedback a
shopper assumes the widget is broken and clicks send again, which doubles the cost and produces a
confusing double reply. Making failures visually distinct matters for trust: a shopper should never
wonder whether the store genuinely said something odd, and a one-click retry turns a dead end into
a recoverable moment.

### Files changed

- `src/App.tsx` — `ChatWidget`: `submitMessage`, the `inFlight` ref, `ERROR_BY_STATUS`,
  `REQUEST_TIMEOUT_MS`, and the error/typing markup
- `src/App.css` — `.chat-typing`, `.chat-send-spinner`, `.chat-error`, `.chat-error-head`,
  `.chat-retry`

### How to test

1. Open the chat widget and ask "What hoodies do you have?". While it works, the dots animate, the
   input is greyed out and cannot be typed in, and the send button shows a spinner.
2. Try pressing Enter repeatedly during that wait — no second message is sent.
3. Stop the backend (`Ctrl-C` in terminal 1) and send another message. A pink **MESSAGE NOT SENT**
   bubble appears reading "We could not reach the Campus Customs assistant…", with a **Try again**
   button.
4. Restart the backend and click **Try again** — the original question is resent and answered, and
   the error bubble disappears.
5. To see the rate-limit message, restart the API with `CAMPUS_CUSTOMS_CHAT_RATE_LIMIT=2` and send
   three messages quickly; the third returns "You are sending messages a little too quickly."

---

## 3. Clarifying questions for under-specified requests

**Type:** Agent / backend

### What was added

`search_products` previously handled three outcomes: a unique match, an ambiguous set, or no match
at all. A request like "I need a gift" tokenized down to nothing useful and fell into `no_match`,
so the assistant replied that it could not find anything — unhelpful, when the real problem was
that the shopper had not said enough yet.

A fourth status, `needs_clarification`, was added. When a query contains no meaningful terms or
only vague ones (`gift`, `something`, `nice`, `warm`, `recommend`, and similar), the tool returns
that status together with facets computed from the live catalogue: the six most common garment
types and the true minimum and maximum price. The `no_match` branch now carries the same facets so
that a genuine miss can also suggest real alternatives.

`prompts/prompt.md` instructs the agent to call the tool even for vague requests, to ask exactly
one short question built from the returned facets, to offer two or three concrete options rather
than an open-ended question, and to return no product cards on that turn.

### Why it helps

The clarifying question is grounded in the database rather than invented, so the categories and the
"$32 to $98" range it quotes are real. The shopper gets a useful next step instead of a dead end,
and the store avoids the worse failure of guessing a product and recommending something arbitrary.

### Files changed

- `backend/tools.py` — `VAGUE_TERMS`, `_catalogue_facets`, and the new branch in `search_products`
- `backend/models.py` — `ProductSearchResult` gains the `needs_clarification` status plus
  `suggested_garment_types` and `price_range`
- `backend/prompts/prompt.md` — rules covering vague, ambiguous, and no-match results

### How to test

1. In the chat widget, send **"I need a gift"**. The reply asks a single question naming real
   catalogue categories and the real price range, and **no product cards appear**.
2. Reply **"a hoodie, around $70"**. The assistant now searches and returns hoodie cards.
3. Confirm specific questions are unaffected: "What is the price of the Basic Hoodie Big Yale?"
   still answers **$68** directly, with no clarifying question.

---

## 4. Chat endpoint guardrails: rate limiting, timeout, and a cached catalogue

**Type:** Agent / backend

### What was added

Three related protections on `POST /api/chat`:

- **Per-caller rate limiting.** Twelve agent calls per rolling 60-second window, keyed by the
  hashed session cookie for signed-in shoppers and by client IP for guests. Exceeding it returns
  **429** with a `Retry-After` header and a friendly message. The limiter stores only a SHA-256
  hash, never a usable credential, and prunes idle callers so memory stays bounded. Limits are
  configurable via `CAMPUS_CUSTOMS_CHAT_RATE_LIMIT` and `CAMPUS_CUSTOMS_CHAT_RATE_WINDOW`.
- **An agent timeout.** The agent call is wrapped in `asyncio.wait_for` with a 60-second budget
  (`CAMPUS_CUSTOMS_CHAT_TIMEOUT`). A hung model request now returns **504** with a clear message
  instead of holding the connection open indefinitely.
- **A cached catalogue snapshot.** Every `search_products` call previously re-read all 102 products
  and all inventory rows, re-parsing the JSON `colors` and `search_tags` columns each time — and a
  single agent turn often calls two or three tools. The snapshot is now cached in two tiers:
  if the database file's size and modification time are unchanged, the cache is served with no
  query at all; if the file did change, six indexed aggregates over `catalogue` and `inventory`
  (row counts, price sum, quantity sum, max rowids) are compared before any full re-read. That
  second tier matters because the app writes `chat_messages` into the same file on every turn, so
  a modification-time check alone would throw the cache away after each message.

### Why it helps

Each agent call is a paid model request. An accidental render loop or a scripted flood would
otherwise run up real cost and slow replies for every other shopper; the rate limit caps that, and
the timeout stops one stuck request from occupying a worker. The cache makes repeated lookups
roughly **2.9× faster** (15.2 ms cold vs 5.3 ms warm, averaged over 20 runs), which compounds
across multi-tool turns.

Correctness was the constraint throughout: a real stock change or price edit invalidates the cache
immediately, verified by test. The one acknowledged gap is that a text-only edit — changing a
description while leaving all six aggregates identical — would not be detected until the next
write. Prices, stock levels, and the product list, which are the values the agent actually quotes,
are always current.

### Files changed

- `backend/main.py` — `chat_rate_limit_key`, `enforce_chat_rate_limit`, the `asyncio.wait_for`
  wrapper and 504 handler, and the new configuration constants
- `backend/tools.py` — `_catalogue_snapshot`, `_FINGERPRINT_SQL`, and the `_catalogue_cache`

### How to test

**Rate limiting.** Start the API with a low limit and send three messages:

```sh
CAMPUS_CUSTOMS_CHAT_RATE_LIMIT=2 uvicorn main:app --port 8001
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8001/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What hoodies do you have?","history":[],"page_context":{"current_path":"/","product_id":null}}'
```

The first two return `200`, the third returns `429` with a `Retry-After` header.

**Timeout.** Start with an impossibly short budget and send one message:

```sh
CAMPUS_CUSTOMS_CHAT_TIMEOUT=0.01 uvicorn main:app --port 8002
```

The request returns `504` with "The assistant took too long to respond", and `/api/health` confirms
the server is still up.

**Cache.** From `backend/`:

```sh
python -c "
import time, tools
tools.search_products('hoodie', browse=True)
t=time.perf_counter(); [tools.search_products('hoodie', browse=True) for _ in range(20)]
print('warm avg ms:', (time.perf_counter()-t)/20*1000)"
```

Then change a quantity in `inventory` with `sqlite3` and confirm `get_product_inventory` reports
the new number immediately.

---

## Regression testing

After all four changes, Problems 1–8 were re-verified against a copy of the database so the real
one stayed untouched:

| Problem | Check | Result |
| --- | --- | --- |
| 3 | `/api/products` and a product detail page | 102 products; Basic Hoodie Big Yale $68 with 6 sizes |
| 4 | Seeded login, wrong password, registration | 200 / 401 / new account created |
| 5 | Chat endpoint returns an agent reply | Reply returned |
| 6 | Price and per-size stock from the database | "$68, and size XS has 15 units" — matches the database exactly |
| 7 | Dynamic product cards | 27 hoodie cards, each linking to `/products/{id}` |
| 8 | Page context, persistence, isolation | "this" resolved to the viewed product (5 in size M); history restored; a second account saw 0 messages; guest received 401 |

The frontend also compiles clean: `tsc --noEmit` reports no errors and `npm run build` succeeds.
