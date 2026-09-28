# AI Prompts Log

This file tracks the prompts used while completing the Campus Customs homework project. Add one section per problem and fill in the details as you work through the assignment.

---

## Problem 1: Prompt log setup

### Main Prompt

````text
I’m starting a homework project in file hwv4, where I’m building a Campus Customs online store with an AI chatbot. Before we start building anything else, please create a file called `AI_prompts.md` in the root of my project. I need this file to keep track of the prompts I use while completing the assignment. Please set it up with sections for Problems 1 through 13. For each problem, give me a place to record:
- the problem number and title
- the main prompt I gave you
- a follow-up prompt, if I needed one
- one sentence explaining what was missing or needed to be fixed after the first prompt

For Problem 1, record this current prompt as my main prompt. Please only do this setup for now. Do not start Problems 2–13 yet. I want to work through the assignment one problem at a time.
````

### Follow-up Prompt

None yet.

### What was missing or needed to be fixed?

None yet.

---

## Problem 2: Understand the database

### Main Prompt

````text
I’m working on Problem 2. I need to understand the database that will power the Campus Customs shop and chatbot.

Please inspect `data/campus_customs.db` and identify all of the tables and the fields in each table. At a minimum, make sure you analyze the `catalogue`, `inventory`, and `users` tables.

Then create a new file called `output/harness.md`. In that file:

1. List each database table.
2. Under each table, list every field/column and briefly explain what information it stores.
3. For every field, add one short explanation of why that field matters for either the online shop or the chatbot. For example, I want to understand which information would help display products, answer customer questions, check inventory, or manage user accounts.

Please base the documentation on what you actually find in the database rather than guessing the schema.

Also update the Problem 2 section of `AI_prompts.md` with this prompt as my main prompt.

Only work on Problem 2 for now. Do not start the later problems.
````

### Follow-up Prompt

None yet.

### What was missing or needed to be fixed?

None yet.

---

## Problem 3: Build the Campus Customs storefront

### Main Prompt

````text
I’m working on Problem 3 now. I want to build the customer-facing Campus Customs website using React, Vite, and TypeScript.

Please scaffold the frontend inside my `hw4` project and create a navigation bar with these pages: Home, Products, About Us, Log in, and Create account.

For the Home and About Us pages, research the public Campus Customs website at yalebulldogblue.com so you can understand the brand, style, and type of information Campus Customs uses. Write the content in original wording rather than copying text from the website. I want the site to feel like a real Campus Customs/Yale merchandise store rather than a generic demo website.

For the Products page, use the real product information from `data/campus_customs.db`. Display the products from the `catalogue` table as product cards. Each card should show the product image using the image path stored in the database, along with the product name, price, and a short description.

Make every product card clickable. Clicking it should open a single-product page for that item. The single-product page should have a large product image on one side and the product information on the other, including the full description, price, and available sizes/stock when that information exists in the database.

Please add a floating chat interface in the bottom-right corner of the website. It does not need to connect to an AI agent yet. For now, just build the interface and structure it so we can connect it to the backend later.

Since the frontend needs access to the database products and images, please create a simple FastAPI backend in `backend/main.py` that can read the SQLite database and serve the product data and product images to the frontend. Keep this backend simple because I will expand it into the AI-agent backend in a later problem.

Make sure the website can actually run locally. Please install or configure whatever project dependencies are needed, and check for obvious TypeScript or build errors when you finish.

Finally, update the Problem 3 section of `AI_prompts.md` with this prompt as my main prompt. Only work on Problem 3 right now and do not start the later problems.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

No follow-up correction was needed after the main prompt.

---

## Problem 4: Create account and log in

### Main Prompt

````text
I’m working on Problem 4 now. I want to make the Create account and Log in pages from Problem 3 actually work using the existing `users` table in `data/campus_customs.db`.

For Create account, please build a working form that asks for first name, last name, email, password, and confirm password. Validate the inputs, make sure the passwords match, and prevent duplicate accounts with the same email.

When a new account is created, save the user to the existing `users` table in the SQLite database. Please store passwords securely using password hashing. Never store or log a user's plain-text password.

For Log in, let a user enter their email and password. Check those credentials against the stored user information and password hash in the database. Show a clear success state when the credentials are correct and an appropriate error when they are not.

Please connect these forms to the FastAPI backend we started in Problem 3.

The seed database already contains a test account. Please verify that I can successfully log in using:

Email: `test@campuscustoms.yale.edu`

Password: `password`

Also test the full new-user flow by creating a brand-new test account, confirming that it is actually written to the `users` table, and then confirming that the newly created account can log in successfully. Please tell me what test account you created so I can verify it in the browser too.

Update `output/harness.md` with a section explaining how authentication works, including which information is stored for each user and how passwords are protected. Do not put any plain-text passwords in the harness.

Also update the Problem 4 section of `AI_prompts.md` with this prompt as my main prompt.

Please test the backend endpoints and frontend build when you're finished. Only work on Problem 4 right now and do not start later problems.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

No follow-up correction was needed after the main prompt.

---

## Problem 5: AI shopping chatbot

### Main Prompt

````text
okay thank you, the login test works. Now, I’m working on Problem 5 now. I want to turn the Campus Customs chat widget I built earlier into a working AI chatbot using a PydanticAI agent behind my existing FastAPI backend.

Please keep `backend/main.py` as the FastAPI application and the file that I run with Uvicorn. Organize the agent using these four files:

- `backend/prompts/prompt.md` for the system prompt
- `backend/agent.py` for the PydanticAI agent setup and wiring
- `backend/tools.py` for tools the agent can call
- `backend/models.py` for Pydantic/PydanticAI structured types, including the chat response and product-card structures as needed
Please build a real PydanticAI agent and connect it to a chat endpoint in `backend/main.py`. Then connect my existing frontend chat widget to that endpoint so that when a shopper sends a message on the website, the message goes to FastAPI, the PydanticAI agent processes it, and the response appears back in the chat widget.

For `backend/prompts/prompt.md`, write an initial system prompt that gives the chatbot a helpful Campus Customs shopping-assistant voice. It should be friendly and concise, help shoppers with Campus Customs merchandise, and be honest when it does not know something. Include basic safety instructions such as not inventing product information, prices, or stock. We will expand the agent's tools and safety rules in later problems, so keep this initial version focused on the requirements for Problem 5.

Use my existing AI API configuration/environment variables rather than hardcoding any API key into the source code. Do not expose or print the API key. If an API key or environment variable required for the agent is missing, tell me exactly what variable I need to configure rather than putting a secret in the code.

Please preserve the existing product, image, account creation, and login functionality from Problems 3 and 4.

Update `output/harness.md` with a section explaining:

1. how the frontend chat widget sends a message to FastAPI,
2. how FastAPI passes the message to the PydanticAI agent,
3. how the agent loads its system prompt from `backend/prompts/prompt.md`,
4. which AI model/configuration the agent uses, and
5. how the agent's response gets returned to the frontend.
Make sure the backend can be started **from inside the `backend/` folder** using exactly:

`uvicorn main:app --reload --port 8000`

Please actually test that startup method and test the chat endpoint with a simple message to confirm that a real agent response is returned. Also check that the frontend still builds successfully.

Finally, update the Problem 5 section of `AI_prompts.md` with this prompt as my main prompt.

Only work on Problem 5 right now. Do not start Problems 6–13.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

No follow-up correction was needed after the main prompt.

---

## Problem 6: Database-backed product and inventory tools

### Main Prompt

````text
I’m working on Problem 6 now. I want to give my Campus Customs PydanticAI agent tools that retrieve real product information and inventory from `data/campus_customs.db` instead of allowing the model to guess.

Please expand `backend/tools.py` with database-backed tools the agent can call to retrieve:

- product descriptions and other relevant product information
- the real product price
- current inventory quantities
- inventory by size when the customer asks about a particular size
These tools must query the actual `catalogue` and `inventory` data in `campus_customs.db`. The agent should never invent a price, stock quantity, or product detail when that information can be retrieved from the database.

Please design the tools so the agent can identify the correct product from a shopper's natural-language question. If a product cannot be confidently identified, the agent should ask the shopper to clarify rather than guessing which product they mean.

For stock questions, make sure the tool can distinguish inventory by size. If a requested size has a quantity of zero or is unavailable, the chatbot should clearly tell the customer that size is out of stock rather than implying that it is available.

Update `backend/prompts/prompt.md` so the agent knows that for questions about product descriptions, prices, sizes, or stock, it should use these database tools and base its answer on the returned information. Tell the agent not to invent prices or quantities.

Add or update the structured Pydantic return types in `backend/models.py` as needed for these product and inventory lookup results. Please use fields that make the tool results clear and reliable for the agent.

Update `output/harness.md` with a Problem 6 section that:

1. lists each new tool,
2. explains what each tool retrieves from the database,
3. lists the model/return fields you chose for the lookup results, and
4. briefly explains why those fields are useful.
Please test the tools and the full chatbot flow using actual products in my database. Test at least:

- a question asking for a product's price,
- a question asking for its description,
- a question asking how many are in stock,
- a question asking about stock for a specific size,
- and, if the database contains one, a size with zero inventory to confirm the chatbot clearly says it is out of stock.
Compare the chatbot's answers with the actual database values so we know it is retrieving rather than inventing the information. Please tell me which product and size you used for the tests so I can reproduce them in the browser.

Preserve everything that already works from Problems 3–5, including the website, authentication, FastAPI backend, and PydanticAI chat connection.

Finally, update the Problem 6 section of `AI_prompts.md` with this prompt as my main prompt.

Only work on Problem 6 right now. Do not start the later problems.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

No follow-up correction was needed after the main prompt.

---

## Problem 7: Dynamic catalogue product cards

### Main Prompt

````text
I’m working on Problem 7 now. I want my Campus Customs chatbot to search the real product catalogue and dynamically display matching products on the website.

When a shopper asks the chatbot about a type of product, such as “What hoodies do you have?”, the PydanticAI agent should search the actual `catalogue` table in `data/campus_customs.db` and return the matching products as structured data.

Please create or update the appropriate search tool in `backend/tools.py` so the agent can search the catalogue based on a shopper’s natural-language request. The search results must come from the database rather than being invented by the model.

Update the structured response types in `backend/models.py` as needed so the chat API can return both:

1. the chatbot’s normal text response, and
2. structured matching product data that the frontend can render.
Each returned product should contain the information the frontend needs for a product card, including the product identifier or slug needed for navigation, image, name, price, and short product information.

Update the frontend chat flow so that when the chat API returns matching products, the website dynamically displays those products as product cards. The shopper should not have to manually search again or refresh the page.

The dynamically generated cards should visually fit with the existing Campus Customs storefront and should use the real product images and information from the database.

Most importantly, preserve the single-item page behavior from Problem 3. Every dynamically generated product card must be clickable, and clicking it should open that product’s existing detail page with its large image, full description, price, sizes, and stock information.

Update `backend/prompts/prompt.md` so the agent understands that when a shopper asks to browse, find, or see a category/type of merchandise, it should use the catalogue search tool and return structured product matches for the frontend rather than only describing products in text.

Update `output/harness.md` with a Problem 7 section explaining the full flow:

shopper message → frontend chat widget → FastAPI → PydanticAI agent → catalogue search tool → structured product matches → FastAPI response → frontend renders product cards.

Please test the entire feature end-to-end using the live website. At minimum, test a request such as “What hoodies do you have?” and confirm that:

- the agent searches the real catalogue,
- matching products appear dynamically on the website as cards,
- the cards show real images, names, prices, and short information,
- and clicking one of the dynamically loaded cards opens the correct existing single-item product page.
Please tell me exactly what search phrase you tested and how many matching products were returned so I can reproduce the test myself.

Preserve all functionality from Problems 3–6, including authentication, product pages, database-grounded price and stock answers, and the existing chatbot.

Finally, update the Problem 7 section of `AI_prompts.md` with this prompt as my main prompt.

Only work on Problem 7 right now. Do not start Problems 8–13.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

No follow-up correction was needed after the main prompt.

---

## Problem 8: Customer memory and context

### Main Prompt

````text
Great, Question 7 is complete. I’m working on Problem 8 now. I want to add customer memory to the existing Campus Customs chatbot while preserving everything we built in Problems 1–7.

Please implement the following:

1. PERSIST CHAT HISTORY FOR LOGGED-IN USERS
When a shopper is logged in, save their chat history to the existing Campus Customs SQLite database using an appropriate table, such as the existing chat_messages table if it is suitable.

Each stored message should be associated with the correct user so that different customers cannot see each other’s conversations.

When that logged-in user returns to the site or reloads the page, retrieve their previous chat history from the database and display it again in the chat widget.

Guests should still be able to use the chatbot, but their chat history does NOT need to persist in the database.

2. GIVE THE AGENT CUSTOMER CONTEXT
When a logged-in customer sends a message, make sure the PydanticAI agent knows who is chatting.

At minimum, provide the agent with:
- first name
- last name, if available
- email
- user ID if useful internally

Use PydanticAI dependencies/agent deps or another clear structured pattern rather than inserting random customer information directly into the system prompt.

Do not expose sensitive authentication information such as password hashes to the agent or frontend.

3. PASS PAGE/PRODUCT CONTEXT TO THE AGENT
The chatbot should also know what page the shopper is currently viewing.

Most importantly, when the shopper is on a single-product page, pass enough structured product context to the backend/agent to identify that product.

For example, if I am viewing the Basic Hoodie Big Yale product page and ask:

“Do you have this in size M?”

or:

“Do you have this in pink?”

the agent should understand that “this” means Basic Hoodie Big Yale without requiring me to type the product name again.

Use a clear structured page-context object. Include useful fields such as the current route/page and product ID or product identifier when the shopper is viewing a product.

The agent should still use the database tools we built previously to answer factual questions about price, color, size, or inventory. Do not invent product information.

4. CONNECT THIS TO THE EXISTING FRONTEND
Update the existing chat widget so that it sends the appropriate logged-in customer information/session identity and current page context to the FastAPI backend.

Do not break the dynamic product-card functionality from Problem 7.

Preserve all previous functionality, including:
- account creation
- login
- catalogue/product browsing
- individual product pages
- database-backed product information
- stock lookup
- PydanticAI chatbot
- dynamic chat search/product cards

5. SECURITY
Do not trust arbitrary user identity information sent from the browser if there is already a safer authenticated/session mechanism available in the project.

Make sure one customer cannot request or retrieve another customer’s stored chat history.

Do not expose password hashes, API keys, or other secrets.

6. DOCUMENTATION
Update output/harness.md to clearly document:
- how logged-in user chat history is stored
- which database table and fields are used
- how messages are associated with the correct user
- how previous chat history is retrieved
- which customer fields the agent receives
- how customer context is passed into the PydanticAI agent
- how page/product context is passed from the frontend to FastAPI and then to the agent
- how guest chat differs from logged-in chat

Also record this entire prompt as the Main Prompt for Problem 8 in AI_prompts.md. Do not overwrite the prompts from Problems 1–7.

7. TEST EVERYTHING
Please actually test the complete flow rather than only writing the code.

At minimum, verify:
A. Log in as a user.
B. Send at least two chat messages.
C. Confirm those messages were saved to the database for that specific user.
D. Reload/return to the site and confirm the previous conversation loads.
E. Confirm a guest can chat without requiring persistent history.
F. Open a specific product page and ask a contextual question such as “Do you have this in size M?” Confirm the agent correctly understands which product “this” refers to and answers using real database information.
G. Confirm another user cannot retrieve the first user’s chat history.
H. Confirm the Problem 7 dynamic product search/cards still work.

After implementation, give me a concise completion report telling me:
- what files you changed
- how chat memory works
- how customer identity reaches the agent
- how page/product context reaches the agent
- the results of each test above
- whether Problem 8 is fully complete

Please focus only on Problem 8. Do not begin Problems 9–13.
````

### Follow-up Prompt

None needed.

### What was missing or needed to be fixed?

Nothing had to be corrected in the code: the session-cookie auth, `chat_messages` persistence, `AgentCustomerContext` deps, and server-verified `AgentPageContext` were already in place from earlier work, so this problem only required end-to-end verification (tests A–H) and writing the Problem 8 section of `output/harness.md`.

---

## Problem 9: Usability improvements

### Main Prompt

````text
Okay thank you. I’m working on Problem 9 now. I want to improve the usability of my Campus Customs store by implementing 2 front-end usability improvements and 2 agent/backend usability improvements.

Please build all four improvements into the existing application. Preserve everything that already works from Problems 1–8, including the storefront, product detail pages, account creation/login, PydanticAI chat agent, database-backed product and inventory tools, dynamic product cards from chat search, persistent customer chat history, and page context.

Before changing anything, inspect the existing implementation and choose four improvements that are useful, clearly visible/testable by the grader, and appropriate for the current Campus Customs application. Do not choose improvements that are merely cosmetic code changes or documentation — they need to actually improve the running application.

Please implement:

FRONT-END IMPROVEMENT 1:
Improve product discovery by adding useful catalogue search and/or filtering controls to the Products page. A shopper should be able to quickly narrow the existing catalogue by something useful such as product name/category/type. Use the real catalogue data and keep the existing product cards and product-detail-page behavior working.

FRONT-END IMPROVEMENT 2:
Improve the chat widget experience. Add clear user feedback while the AI is working, such as a visible loading/thinking state, and make error states understandable if the backend or agent request fails. Prevent accidental duplicate submissions while a request is processing. Keep the existing chat design consistent with the Campus Customs site.

AGENT/BACKEND IMPROVEMENT 1:
Improve the agent’s handling of ambiguous shopping requests. If the shopper gives too little information to make a reliable recommendation or lookup, the agent should ask a concise clarifying question instead of guessing. It must continue using the database tools for factual product, price, and inventory information.

AGENT/BACKEND IMPROVEMENT 2:
Improve reliability and efficiency of the chat backend. Inspect the current implementation and add an appropriate improvement such as stronger request validation, graceful error handling, or another concrete backend enhancement that makes the agent safer, faster, cheaper, or more reliable. Choose something that is meaningful and demonstrable. Do not weaken any functionality from Problems 1–8.

IMPORTANT:
- Continue using campus_customs.db as the source of truth for catalogue, price, and inventory information.
- Do not invent products, prices, descriptions, sizes, or stock quantities.
- Do not break persistent chat memory or logged-in-user context from Problem 8.
- Do not break page context, including the agent understanding which product a shopper is viewing.
- Do not break the structured product-card response from Problem 7.
- Do not break existing authentication.
- Do not hardcode API keys or secrets.
- Keep the current Campus Customs visual design rather than redesigning the whole website.

Create `output/usability.md`.

For EACH of the four improvements, document:
1. The name of the improvement
2. Whether it is front-end or agent/backend
3. What you added
4. Why it helps a Campus Customs shopper or the business
5. Which files were changed
6. How a grader can test the improvement in the running app

Then actually test all four improvements in the running application. Also regression-test the important functionality from Problems 1–8 to make sure these changes did not break anything.

Please report back with:
- the exact 4 improvements implemented,
- the files changed,
- how each improvement was tested,
- the results of those tests,
- confirmation that `output/usability.md` was created,
- and confirmation that the existing Problems 1–8 functionality still works.

Also record this Problem 9 prompt in my existing `AI_prompts.md` under the Problem 9 section.

Do not begin Problem 10.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

Two things surfaced during testing rather than from the prompt itself: an "in stock only" toggle was pointless because no product is fully sold out, so it became "all sizes in stock" (25 of 102 products), and the first catalogue cache keyed only on the database file's modification time, which the app's own chat-message writes invalidated on every turn, so a second fingerprint check over `catalogue` and `inventory` was added.

---

## Problem 10: Design and visual polish

### Main Prompt

````text
Okay thank you. I’m working on Problem 10 now. I want to style and polish my existing Campus Customs website so it feels like a real, intentional, modern Campus Customs storefront rather than a basic class-project website.

Please improve the creative design of the EXISTING site while preserving all functionality from Problems 1–9.

Focus specifically on:
- typography and font hierarchy
- color palette and consistent use of color
- spacing and visual hierarchy
- navigation/header design
- product-card presentation
- product-detail-page presentation
- buttons, forms, and interactive states
- the chat widget and chat experience
- subtle motion, hover states, and transitions where appropriate
- responsive/mobile presentation
- consistency across Home, Products, About Us, Login, Create Account, product detail pages, and dynamically generated product cards

DESIGN DIRECTION:

Campus Customs should feel like a polished, elevated university lifestyle/apparel brand — youthful and modern, but not childish or overly busy.

Please preserve the existing Campus Customs identity and build on the visual language already present rather than replacing it with a generic template.

I want:
- a clean editorial/e-commerce feel
- strong product photography
- intentional whitespace
- clear visual hierarchy
- sophisticated typography
- restrained use of Yale-inspired navy/neutral tones with the existing pink accent where appropriate
- polished product cards
- clear calls to action
- subtle animations and hover interactions
- a chat widget that visually belongs to the same brand

Avoid:
- excessive gradients
- excessive shadows
- unnecessary animations
- clutter
- generic SaaS-style design
- making everything rounded
- changing the site into a completely different brand

PRODUCT EXPERIENCE:
Make the catalogue feel like a real shopping experience. Product cards should make the image, product name, price, and useful information easy to scan. Hover/focus behavior should make cards feel interactive. Clicking cards must continue opening the existing product-detail experience.

CHAT EXPERIENCE:
Polish the existing AI shopping assistant visually so it feels integrated into Campus Customs. Preserve all functionality from Problems 5–9, including database-backed answers, product cards, memory, page context, loading states, and error handling.

RESPONSIVENESS:
Check desktop and smaller/mobile layouts. Navigation, product grids, forms, product pages, and chat should remain usable without awkward overflow or broken layouts.

IMPORTANT:
This is primarily a styling/design problem. Do not unnecessarily rewrite backend architecture or change working business logic.

Do not break:
- catalogue/database integration
- product search/filtering
- individual product pages
- create account/login
- password security
- PydanticAI agent
- database-backed product/price/inventory tools
- structured chat product cards
- dynamic catalogue results from chat
- logged-in customer chat memory
- user identity/context
- product-page context
- the usability improvements from Problem 9

Use the real existing product images and data. Do not invent new products or replace the catalogue with mock data.

Create `output/design.md`.

Keep this file concrete and short. Explain:
1. the major visual/design changes you made,
2. why each change should help customers stick around, browse, and potentially buy,
3. any responsive/mobile improvements you made.

After implementing the design, run the application and visually inspect the major pages. Test both desktop and mobile/responsive layouts where possible.

Also run regression checks to make sure the important functionality from Problems 1–9 still works after the styling changes.

Report back with:
- the major design changes you made,
- which files you changed,
- confirmation that `output/design.md` was created,
- what pages/layouts you visually tested,
- whether responsive/mobile behavior works,
- whether Problems 1–9 still work,
- and any issues you found.

Also record this exact Problem 10 prompt in my existing `AI_prompts.md` under the Problem 10 section.

Do not begin Problem 11.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

The product-image treatment took three attempts before it was right: framing every photo inside a light tile stamped a black rectangle onto the 73 of 102 catalogue images that are shot on black, switching the tile to near-black simply inverted the problem onto the 29 white-background shots, and only filling the frame edge-to-edge in the grid (while keeping `contain` on the detail page, where cropping was cutting off garment hems) removed the artifact in both cases.

---

## Problem 11: Live-site app check and visual testing report

### Main Prompt

````text
Okay thank you. I’m working on Problem 11 now. I want to perform the required live-site app check for my completed Campus Customs website and create the required visual testing report.

Please test the ACTUAL RUNNING WEBSITE through the browser. Do not rely only on API calls, code inspection, or previous test results. I need screenshots from the live website that visibly demonstrate the required functionality.

Create:

`output/app_check.html`

and put all screenshot image files in:

`output/app_check_images/`

The HTML must use RELATIVE paths to those images so I can double-click `output/app_check.html` locally and the screenshots will load correctly.

I need exactly these three required checks documented clearly:

CHECK 1 — INVENTORY / STOCK LOOKUP THROUGH CHAT

Use the live Campus Customs chat widget to ask about the inventory level of a specific real product and size.

Choose a product/size whose inventory can be verified directly against `campus_customs.db`.

The screenshot should clearly show:
- the shopper’s question,
- the chatbot’s response,
- the real stock quantity and, where appropriate, price.

Before documenting the result, independently verify the product, size, stock quantity, and price against the database so we know the chatbot is returning honest database-backed information rather than inventing it.

Save an appropriate screenshot such as:

`output/app_check_images/inventory.png`

In the HTML, include a heading and 1–2 sentences explaining what the screenshot proves, including that the value was checked against the database.

CHECK 2 — DYNAMIC SEARCH-RESULT PRODUCT CARDS

Through the live chat widget, ask a category question such as:

“What hoodies do you have?”

Use whichever category gives a clear demonstration with the current catalogue.

The screenshot must visibly show that after the chat request, matching product cards dynamically appear on the website.

The screenshot should capture enough of the page to show:
- the chat/category request,
- dynamically rendered product results,
- recognizable product information such as images, names, and/or prices.

Verify that these cards correspond to real products from `campus_customs.db`.

Also verify that at least one dynamically generated card still opens its existing single-product detail page when clicked.

Save an appropriate screenshot such as:

`output/app_check_images/dynamic_search.png`

In the HTML, include a heading and 1–2 sentences explaining what the screenshot proves.

CHECK 3 — PROBLEM 9 USABILITY FEATURE

Demonstrate one of the usability improvements implemented in Problem 9.

Prefer the catalogue search/filter feature because it should be especially easy for the grader to see and verify visually.

Use the live Products page, enter/select a useful search or filter, and capture a screenshot showing the resulting filtered catalogue.

The screenshot should make it obvious that the usability feature is active and changing what the shopper sees.

Save an appropriate screenshot such as:

`output/app_check_images/usability.png`

In the HTML, include a heading and 1–2 sentences explaining:
- what usability feature is being demonstrated,
- and why the screenshot proves it works.

APP_CHECK.HTML REQUIREMENTS

Make `output/app_check.html` extremely easy for the grader to inspect.

Use:
- a clear title such as “Campus Customs — App Check”
- one clearly labeled section for each of the 3 required checks
- the screenshot for each check
- only 1–2 concise sentences below each screenshot explaining what it proves
- readable, simple styling
- relative image paths ONLY, such as:
  `app_check_images/inventory.png`

Do NOT embed absolute local filesystem paths such as `/Users/...`.

Do not use screenshots from earlier development work. Capture fresh screenshots of the final live application as it currently exists after Problem 10.

IMPORTANT TESTING RULES:

- Use the real running frontend and backend.
- Do not fabricate screenshots.
- Do not fabricate test results.
- Do not manually alter the database just to make a test pass.
- Do not pollute the real database with unnecessary test users/messages.
- Do not expose passwords, API keys, environment variables, or other secrets in the screenshots or HTML.
- Keep all functionality from Problems 1–10 intact.
- If you discover a genuine bug while doing these checks, fix it carefully, re-test it, and document what you fixed.
- Do not redesign the application for this problem. This problem is primarily testing and documentation.

After creating the files, actually verify that `output/app_check.html` works as a standalone local HTML report:
1. Open/double-click the HTML file.
2. Confirm all 3 screenshot images load using the relative paths.
3. Confirm each screenshot is readable.
4. Confirm each required heading and caption appears.
5. Confirm the report does not depend on the development server just to display its screenshots.

Then perform a final regression sanity check that the important functionality from Problems 1–10 still works.

Also record this exact Problem 11 prompt in my existing `AI_prompts.md` under the Problem 11 section.

When finished, report back with:
- the three tests you performed,
- the exact product/size/stock information used for the inventory test,
- confirmation that the inventory answer matched `campus_customs.db`,
- the category query used for the dynamic-product-card test,
- the Problem 9 usability feature demonstrated,
- the screenshot filenames created,
- confirmation that `output/app_check.html` was created,
- confirmation that you opened the HTML and all images loaded correctly using relative paths,
- any bugs discovered and fixed,
- confirmation that Problems 1–10 still work.

Do not begin Problem 12.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

No bug was found in the application; the only correction was to my own test tooling — the first dynamic-card screenshot had auto-scrolled past the shopper's question so it had to be re-captured with the transcript scrolled to show both the question and the results, and a regression assertion that slept a fixed 700ms before checking the chat loading state failed spuriously once the whole request began completing in under a second, so it was rewritten to observe the state with a MutationObserver instead.

---

## Problem 12: Audit trail, safety rules, and harness documentation

### Main Prompt

````text
Okay thank you. I’m working on Problem 12 now. I want to add the audit trail and safety requirements to my completed Campus Customs AI shopping system, and finish the technical documentation in the harness.

Please work only on Problem 12 and preserve all functionality from Problems 1–11.

For Problem 12, please do the following:

1. APPEND-ONLY AUDIT TRAIL

Create and maintain:

output/audit_trail.json

This should record agent-loop activity and MUST be append-only. Do not wipe, reset, or overwrite the existing audit history between runs.

For each relevant agent interaction/tool call, record enough information to understand what happened, including:
- timestamp/time
- tool name
- short/safe version of the arguments
- short/safe version of the result
- stop reason / why the agent loop ended

Use a sensible JSON structure that remains valid as additional entries are added.

Do not log passwords, API keys, authentication secrets, session tokens, or other sensitive information.

Please actually test this by making more than one agent interaction and confirm that earlier audit entries remain after later interactions.

2. AGENT SAFETY RULES

Update:

backend/prompts/prompt.md

Add clear safety and reliability rules appropriate for the Campus Customs shopping assistant.

At minimum, the agent should:
- never invent product information, prices, inventory quantities, sizes, or availability
- use the database-backed tools when factual product or stock information is needed
- clearly say when information is unavailable rather than guessing
- clearly report when an item or requested size is out of stock
- never expose API keys, passwords, authentication information, or other secrets
- not claim that an action occurred unless the system/tool actually performed it
- treat customer/account information appropriately and not expose another customer's information
- avoid destructive or unauthorized database actions
- ask for clarification when a shopper’s request is too ambiguous to answer reliably

Keep these rules concise enough to be useful as an actual system prompt.

3. FINISH output/harness.md

Review the ACTUAL implementation and finish:

output/harness.md

Make this document a clear technical explanation of how the completed system works.

It must include:

A. MODELS
Document the important model/structured-output fields in backend/models.py.

For each important model, explain:
- the relevant fields
- what each field represents
- why that structure/type was chosen

Do not invent fields. Inspect models.py and document what is actually implemented.

B. TOOLS AND ABILITIES
Document the agent tools and abilities that actually exist.

Include the database-backed product/catalogue/inventory tools from the earlier problems and explain what each tool does and what information it returns.

Also explain the structured product-search behavior that allows chat searches to update the webpage with product cards.

C. SAFETY RULES
Document the safety rules implemented in backend/prompts/prompt.md and briefly explain why they matter.

D. SYSTEM SPECS
Document the important implementation specifications, including:
- agent loop/tool-call limits
- search/result caps or limits
- AI model configuration
- how the model is selected/configured
- relevant environment variables
- how the frontend and backend communicate
- how to start/run the backend
- how to start/run the frontend

Use the actual project configuration rather than guessing.

Also include any other important implementation limits or configuration details that would help a grader understand and reproduce the system.

4. PRESERVE EXISTING WORK

Do not rebuild the application or replace working implementations from Problems 1–11.

Do not alter the database's real catalogue, inventory, users, or legitimate chat history just to complete this problem.

Do not delete existing documentation from output/harness.md that is still correct. Clean it up, organize it, and add what is missing.

Do not expose or print my API key or any secrets.

5. VERIFY EVERYTHING

After implementing Problem 12:

- confirm output/audit_trail.json exists
- confirm it contains actual agent-loop activity
- run at least two test interactions and prove the audit trail APPENDS rather than resets
- confirm each audit entry contains the required information
- confirm secrets are not written to the audit trail
- confirm the safety rules are present in backend/prompts/prompt.md
- confirm output/harness.md covers models, tools, safety rules, and system specs
- run appropriate frontend/backend checks
- confirm the existing website, authentication, chat, database product lookup, inventory lookup, dynamic product cards, customer memory/page context, usability features, styling, and Problem 11 app-check functionality still work

If testing would modify production/seed data unnecessarily, use a safe copy of the database where appropriate.

6. AI PROMPT LOG

Append this exact prompt to the Problem 12 section of AI_prompts.md. Do not overwrite the prompts already recorded for Problems 1–11.

When finished, give me a concise report containing:
- files created
- files modified
- audit-trail format
- how append-only behavior was verified
- safety rules added
- what was added/updated in harness.md
- tests performed and their results
- any issues you found or could not safely fix

Do not begin Problem 13.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

A bug in my own audit code: because a tool result is redacted once when it is summarised and again when the whole entry is written, the nested per-size inventory values exceeded the redactor's depth guard and were logged as `"[truncated]"` instead of real numbers, so the depth budget was raised to cover the full entry → tool_calls → call → result → inventory → row → value path.

---

## Problem 13: GitHub submission packaging

### Main Prompt

````text
Okay, thank you. I’m working on Problem 13, the final problem. I want to prepare my completed Campus Customs Homework 4 for GitHub submission.

Please complete Problem 13 only. Do not redesign, refactor, or change functionality from Problems 1–12 unless something is strictly required to satisfy the Problem 13 submission requirements.

Please do the following:

1. Verify the submission structure. The submitted code must live inside a folder named hw4. Make sure the submission contains the required project files, including:
   - AI_prompts.md
   - requirements.txt
   - .env.example
   - .gitignore
   - README.md
   - the frontend application
   - backend/main.py
   - backend/agent.py
   - backend/models.py
   - backend/tools.py
   - backend/prompts/prompt.md
   - output/harness.md
   - output/design.md
   - output/usability.md
   - output/app_check.html
   - output/app_check_images/
   - output/audit_trail.json

2. Protect private/local files. Verify .gitignore prevents the real .env, campus_customs.db, product images/data pack, and other secrets or local-only files from being committed. Do not delete my local copies; they simply must not be included in Git.

3. Create or verify .env.example containing placeholders only, never my actual API keys or secrets. It should show the environment variables needed to run the project, including the model/API configuration used by the application.

4. Review README.md and make sure it clearly explains how a grader can run the project after cloning the repository and supplying the local data pack. Include the exact commands needed to install dependencies and start both the FastAPI backend and Vite/React frontend.

5. Verify the agent remains organized in the required four files under backend: prompts/prompt.md, agent.py, tools.py, and models.py.

6. Before committing anything, run a final submission audit. Confirm that no .env, API keys, credentials, campus_customs.db, product images, node_modules, virtual environment, or other inappropriate generated/local files would be committed. Also confirm that all required output/ evidence files are included.

7. Run appropriate final build/tests to make sure the project still works. Do not alter my real database or create permanent test records.

8. Update the Problem 13 section of AI_prompts.md with this prompt and a concise record of what was done. Do not overwrite the previous Problems 1–12 sections.

9. Then prepare the repository for submission. If this project is already connected to the correct GitHub repository, commit the final Homework 4 files and push them. Do not force-push, rewrite history, or delete unrelated repository content.

10. If you cannot safely push because GitHub authentication, repository creation, or the destination repo requires my action, stop and tell me exactly what I need to do rather than guessing or creating the wrong repository.

At the end, give me a short Problem 13 submission report showing:
- final hw4 file structure,
- required files present,
- sensitive/local files excluded,
- .env.example verified,
- README/run instructions verified,
- build/tests status,
- Git status,
- commit/push status,
- and, if successfully pushed, the public GitHub repository URL that I should submit to Canvas.

Finally, verify that the GitHub URL is the repository URL graders can open and clone, not a local URL, branch URL, file URL, or ZIP download.

This is the final problem. Do not start any additional work after Problem 13.
````

### Follow-up Prompt

None recorded.

### What was missing or needed to be fixed?

Three packaging gaps were found and fixed — there was no `.env.example`, no top-level `requirements.txt`, and `.gitignore` was still the stock Vite template that would have committed the real `.env`, `data/campus_customs.db`, and all 102 product images — and two things could not be completed without the user: the project folder is named `hwv4` rather than the required `hw4`, and the project is not a Git repository and has no GitHub remote, so no commit or push could be made.

### Record of what was done

- Created `.env.example` (placeholders only — no real key), top-level `requirements.txt`, and a rewritten `.gitignore` that excludes `.env`, `data/`, `*.db`, `public/products/`, `dist/products/`, `node_modules`, `.venv`, `__pycache__`, and audit scratch files while keeping `.env.example` tracked.
- Rewrote `README.md` around a fresh clone: data-pack placement, `cp .env.example .env`, exact install/run commands for both servers, project layout, and configuration.
- Verified the agent is still organized across `backend/prompts/prompt.md`, `agent.py`, `tools.py`, and `models.py`.
- Ran a dry-run submission audit with a temporary Git index (outside the project, never initializing a repo in it) to confirm exactly which files would be committed.
- Re-ran the frontend build and the browser regression suite; left the real database untouched.