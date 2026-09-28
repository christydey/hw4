# Campus Customs Design Pass (Problem 10)

Styling only. No backend, agent, or business logic changed. Files touched:
`src/App.css`, `src/index.css`, and two markup-level changes in `src/App.tsx`
(the add-to-bag label and its state class).

---

## 1. Product photography, fixed by measurement

**What changed.** Product tiles now fill edge to edge (`object-fit: cover`); the detail page
uses `object-fit: contain` inside a near-black panel.

**Why.** The catalogue images do not share a background. Measuring the corner pixels of all
102 files: **73 are shot on black, 29 on white.** The old grid letterboxed every photo inside
a warm-grey tile, which stamped a hard black rectangle onto 73 cards. Switching the tile to
black just inverted the problem — 29 harsh white boxes instead. Filling the frame removes the
tile from view entirely, so no card shows a rectangle-inside-a-rectangle either way.

The detail page keeps `contain` because the old `cover` was cropping the hem off tall garment
shots. Against the dark panel, black-background shots bleed away to nothing and white-background
shots read as a framed gallery print. Both cases were checked visually.

**Why it helps.** The grid is the shopping surface. A consistent frame lets a shopper scan 102
products by garment rather than by background colour, and the uncropped detail shot means the
product page shows the whole piece being bought.

## 2. Typography and hierarchy

A single type scale (`--step--2` … `--step-6`) replaces ad-hoc pixel values. Product name moved
to the display serif; **price is now the second-strongest element on a card**, set in ink rather
than muted grey. The detail-page price is serif at 22px, and the product title is fluid
(`clamp(32px, 3.1vw, 45px)` with `text-wrap: balance`) so long names break across two balanced
lines instead of one awkward orphan.

**Why it helps.** Name and price are the two facts that drive a click. Making price legible at a
glance reduces the work of comparing 102 items.

## 3. Navigation

The header is now sticky, translucent, with a blur. **Why it helps:** the catalogue is a long
scroll; a shopper 60 products down can reach Products, About, or Log in without scrolling back.

## 4. Buttons, forms, and interactive states

- Disabled buttons keep their outline and drop the fill instead of fading to grey mush. The
  add-to-bag button now reads **"Select a size to continue"** until a size is chosen, and turns
  green on success.
- Size buttons show a diagonal hatch when sold out, alongside the existing strikethrough.
- Inputs get a hover border, and a focus ring in the brand pink.
- Every interactive element has a visible `:focus-visible` outline.

**Why it helps.** The greyed-out add-to-bag button previously looked broken; saying what is
missing turns a dead end into an instruction. Sold-out sizes are now obvious before the click.

## 5. Chat widget

Navy header with the brand mark, matching the site's Yale-navy band. Result cards use the same
framed-thumbnail treatment as the catalogue, hover to pink with a small slide, and the message
bubbles animate in. All Problem 5–9 behaviour is untouched: database-backed answers, structured
product cards, memory, page context, typing indicator, error bubble, retry.

**Why it helps.** The assistant now looks like part of the store rather than a bolted-on widget,
which matters for trusting what it says about price and stock.

## 6. Motion

Kept deliberately small: a 4% image zoom and outline on card hover, a rising arrow badge, message
bubbles fading in, the sheet sliding up on mobile. Everything is 180–500ms. The existing
`prefers-reduced-motion` block disables all of it.

---

## Responsive work

- **Chat is now a bottom sheet on phones** (full width, pinned to the bottom, slide-up), instead
  of a floating card leaving slivers of page around every edge. The duplicate floating close
  button is hidden while the sheet is open, since the sheet header has its own.
- Detail-page padding, size buttons, and filter chips tightened at ≤620px.
- **Verified: zero horizontal overflow** on Home, Products, product detail, About, Log in, and
  Create account at 390×844.

## What was verified

Rendered every page in headless Chrome at 1440×900 and 390×844 and inspected the screenshots:
Home, Products, filtered Products, product detail (both a black-background and a
white-background product), About, Log in, Create account, chat open, chat mid-request, and chat
with product cards.

17 automated UI checks pass, including: 102 cards render; `?type=pullover+hoodie&size=M` still
yields 14 of 102 with two filter chips; a card click opens the detail page at $68.00 with six
sizes; the chat returns 27 linked product cards; "Do you have this in size M?" on a product page
still answers "5 units"; no uncaught page errors.

## Known limitation

Black- and white-background photographs still sit side by side in the grid. That is baked into
the source images — some even have black bars inside the JPEG itself — and cannot be corrected
in CSS without editing the assets, which was out of scope. The consistent frame is a mitigation,
not a fix.
