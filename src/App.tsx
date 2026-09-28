import { useEffect, useRef, useState, type FormEvent } from 'react'
import { BrowserRouter, Link, NavLink, Route, Routes, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { AlertCircle, ArrowDown, ArrowLeft, ArrowRight, ArrowUpRight, Check, ChevronDown, Menu, MessageCircle, RotateCcw, Send, ShoppingBag, Sparkles, X } from 'lucide-react'
import './App.css'

type Product = {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  image_file_path: string
  image_url: string
  price: number
  inventory?: { size: string; quantity: number }[]
  total_stock?: number
}

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

function useProducts() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/api/products`)
      .then((response) => {
        if (!response.ok) throw new Error('The catalogue could not be loaded.')
        return response.json() as Promise<Product[]>
      })
      .then(setProducts)
      .catch(() => setError('The catalogue is taking a moment. Check that the Campus Customs API is running.'))
      .finally(() => setLoading(false))
  }, [])

  return { products, loading, error }
}

function ProductImage({ product, className = '', priority = false }: { product: Product; className?: string; priority?: boolean }) {
  return <img className={className} src={`${API_BASE}${product.image_url}`} alt={product.name} loading={priority ? 'eager' : 'lazy'} />
}

function Header() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <>
      <div className="announcement">A little Yale. A lot of you. <span>Explore the collection <ArrowRight size={13} /></span></div>
      <header className="site-header">
        <Link className="wordmark" to="/" aria-label="Campus Customs home">
          <span className="wordmark-mark">CC</span><span>CAMPUS<br />CUSTOMS</span>
        </Link>
        <button className="icon-button mobile-menu-button" aria-label="Toggle navigation" onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? <X size={21} /> : <Menu size={21} />}
        </button>
        <nav className={menuOpen ? 'primary-nav is-open' : 'primary-nav'} aria-label="Main navigation">
          <NavLink to="/" onClick={() => setMenuOpen(false)}>Home</NavLink>
          <NavLink to="/products" onClick={() => setMenuOpen(false)}>Products</NavLink>
          <NavLink to="/about" onClick={() => setMenuOpen(false)}>About Us</NavLink>
          <NavLink className="mobile-login-link" to="/login" onClick={() => setMenuOpen(false)}>Log in</NavLink>
        </nav>
        <div className="header-actions">
          <NavLink to="/login">Log in</NavLink>
          <NavLink className="account-link" to="/create-account">Create account <ArrowUpRight size={15} /></NavLink>
        </div>
      </header>
    </>
  )
}

function ProductCard({ product, index = 0 }: { product: Product; index?: number }) {
  return (
    <Link className="product-card" to={`/products/${product.product_id}`} style={{ animationDelay: `${Math.min(index, 8) * 45}ms` }}>
      <div className="product-card-image">
        <ProductImage product={product} />
        <span className="product-card-arrow"><ArrowUpRight size={17} /></span>
      </div>
      <div className="product-card-meta"><span>{product.garment_type}</span><span>${product.price.toFixed(2)}</span></div>
      <h3>{product.name}</h3>
      <p className="product-card-description">{product.description}</p>
    </Link>
  )
}

function CatalogueState({ loading, error }: { loading: boolean; error: string }) {
  if (loading) return <div className="catalogue-state"><span className="loader-mark">CC</span><p>Opening the catalogue…</p></div>
  if (error) return <div className="catalogue-state"><p>{error}</p><a className="text-link" href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">Check the API <ArrowUpRight size={14} /></a></div>
  return null
}

function HomePage({ products, loading, error }: { products: Product[]; loading: boolean; error: string }) {
  const featured = products.slice(0, 4)

  return (
    <main>
      <section className="home-hero">
        <div className="hero-copy">
          <span className="eyebrow"><span className="eyebrow-dot" /> NEW HAVEN, MADE PERSONAL</span>
          <h1>Wear your<br /><em>Yale</em> your way.</h1>
          <p>Campus classics, team colors, and the little things that make this place yours.</p>
          <Link className="button button-dark" to="/products">Shop the collection <ArrowRight size={16} /></Link>
          <div className="hero-note"><span>01 / 03</span><span>Thoughtful gear for every chapter</span></div>
        </div>
        <div className="hero-art" aria-label="Campus Customs collection">
          <div className="hero-art-frame">
            <div className="hero-stamp">NEW HAVEN<br />EST. FOR YOU</div>
            <div className="hero-art-type">THE<br /><span>BLUE</span><br />EDIT</div>
            {featured[0] && <div className="hero-product-shot"><ProductImage product={featured[0]} priority /></div>}
            <div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" />
            <div className="hero-art-caption"><span>YALE, BUT MAKE IT YOURS</span><ArrowDown size={15} /></div>
          </div>
          <span className="hero-art-index">CAMPUS CUSTOMS / 2025</span>
        </div>
        <div className="hero-side-label">A NEW HAVEN ORIGINAL</div>
      </section>

      <section className="ticker" aria-label="Campus Customs collection values">
        <div className="ticker-track"><span>MADE FOR THE MOMENT</span><i>✳</i><span>ROOTED IN NEW HAVEN</span><i>✳</i><span>YOUR CAMPUS, YOUR CALL</span><i>✳</i><span>MADE FOR THE MOMENT</span><i>✳</i><span>ROOTED IN NEW HAVEN</span><i>✳</i></div>
      </section>

      <section className="section featured-section">
        <div className="section-heading"><div><span className="eyebrow">THE CAMPUS EDIT</span><h2>Good things<br /><em>wear well.</em></h2></div><Link className="text-link" to="/products">See all 102 pieces <ArrowRight size={15} /></Link></div>
        {loading || error ? <CatalogueState loading={loading} error={error} /> : <div className="product-grid">{featured.map((product, index) => <ProductCard key={product.product_id} product={product} index={index} />)}</div>}
      </section>

      <section className="manifesto-band"><span className="manifesto-number">02 / A NOTE FROM CAMPUS CUSTOMS</span><p>Not just what you wear.<br /><em>Where you belong.</em></p><Link className="round-link" to="/about" aria-label="Read about Campus Customs"><ArrowUpRight size={21} /></Link></section>
    </main>
  )
}

const SIZE_ORDER = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
const ANY_TYPE = 'All pieces'
const ANY_SIZE = 'Any size'
const ANY_COLOR = 'Any color'

function titleCase(value: string) {
  return value.replace(/\b[a-z]/g, (letter) => letter.toUpperCase())
}

function ProductsPage({ products, loading, error }: { products: Product[]; loading: boolean; error: string }) {
  // Filters live in the URL so a filtered view survives a reload, works with the browser
  // back button, and can be shared or bookmarked.
  const [params, setParams] = useSearchParams()
  const search = params.get('q') ?? ''
  const category = params.get('type') ?? ANY_TYPE
  const size = params.get('size') ?? ANY_SIZE
  const color = params.get('color') ?? ANY_COLOR
  const inStockOnly = params.get('stock') === 'in'
  const sort = params.get('sort') ?? 'featured'

  function setFilter(key: string, value: string, fallback: string) {
    const next = new URLSearchParams(params)
    if (!value || value === fallback) next.delete(key)
    else next.set(key, value)
    setParams(next, { replace: true })
  }

  function clearAll() {
    setParams(new URLSearchParams(), { replace: true })
  }

  const categories = [ANY_TYPE, ...[...new Set(products.map((product) => product.garment_type))].sort((a, b) => a.localeCompare(b))]
  const sizes = [ANY_SIZE, ...[...new Set(products.flatMap((product) => (product.inventory ?? []).map((item) => item.size)))]
    .sort((a, b) => {
      const left = SIZE_ORDER.indexOf(a), right = SIZE_ORDER.indexOf(b)
      return left !== -1 && right !== -1 ? left - right : a.localeCompare(b)
    })]
  const colors = [ANY_COLOR, ...[...new Set(products.flatMap((product) => product.colors))].sort((a, b) => a.localeCompare(b))]

  const visibleProducts = products
    .filter((product) => category === ANY_TYPE || product.garment_type === category)
    .filter((product) => `${product.name} ${product.description} ${product.search_tags.join(' ')}`.toLowerCase().includes(search.toLowerCase()))
    .filter((product) => size === ANY_SIZE || (product.inventory ?? []).some((item) => item.size === size && item.quantity > 0))
    .filter((product) => color === ANY_COLOR || product.colors.some((item) => item.toLowerCase() === color.toLowerCase()))
    // Every product currently has *some* stock, so a plain "in stock" toggle would filter
    // nothing. What a shopper actually wants is the pieces that have not sold out of any size.
    .filter((product) => !inStockOnly || ((product.inventory ?? []).length > 0 && (product.inventory ?? []).every((item) => item.quantity > 0)))
    .sort((first, second) => sort === 'price-low' ? first.price - second.price : sort === 'price-high' ? second.price - first.price : 0)

  const activeFilters = [
    search && { key: 'q', label: `“${search}”`, fallback: '' },
    category !== ANY_TYPE && { key: 'type', label: category, fallback: ANY_TYPE },
    size !== ANY_SIZE && { key: 'size', label: `Size ${size}`, fallback: ANY_SIZE },
    color !== ANY_COLOR && { key: 'color', label: titleCase(color), fallback: ANY_COLOR },
    inStockOnly && { key: 'stock', label: 'All sizes in stock', fallback: '' },
  ].filter(Boolean) as { key: string; label: string; fallback: string }[]

  return (
    <main className="catalogue-page">
      <section className="catalogue-intro"><span className="eyebrow">THE FULL CAMPUS CUSTOMS COLLECTION</span><h1>Find your<br /><em>favorite.</em></h1><p>From the stands to the stacks, there’s a piece with your name on it.</p></section>
      <div className="catalogue-toolbar">
        <label className="search-field"><span className="sr-only">Search products</span><input value={search} onChange={(event) => setFilter('q', event.target.value, '')} placeholder="Search the collection" /><ArrowRight size={17} /></label>
        <label className="select-field"><span className="sr-only">Filter by garment type</span><select value={category} onChange={(event) => setFilter('type', event.target.value, ANY_TYPE)}>{categories.map((item) => <option key={item}>{item}</option>)}</select><ChevronDown size={15} /></label>
        <label className="select-field"><span className="sr-only">Filter by available size</span><select value={size} onChange={(event) => setFilter('size', event.target.value, ANY_SIZE)}>{sizes.map((item) => <option key={item}>{item}</option>)}</select><ChevronDown size={15} /></label>
        <label className="select-field"><span className="sr-only">Filter by color</span><select value={color} onChange={(event) => setFilter('color', event.target.value, ANY_COLOR)}>{colors.map((item) => <option key={item} value={item}>{item === ANY_COLOR ? item : titleCase(item)}</option>)}</select><ChevronDown size={15} /></label>
        <button type="button" className={inStockOnly ? 'stock-toggle is-active' : 'stock-toggle'} aria-pressed={inStockOnly} onClick={() => setFilter('stock', inStockOnly ? '' : 'in', '')}>
          <span className="stock-toggle-box">{inStockOnly && <Check size={11} />}</span>All sizes in stock
        </button>
        <label className="select-field sort-field"><span className="sr-only">Sort products</span><select value={sort} onChange={(event) => setFilter('sort', event.target.value, 'featured')}><option value="featured">Featured</option><option value="price-low">Price: low to high</option><option value="price-high">Price: high to low</option></select><ChevronDown size={15} /></label>
      </div>
      {activeFilters.length > 0 && <div className="filter-chips" aria-label="Active filters">
        {activeFilters.map((filter) => <button key={filter.key} type="button" className="filter-chip" onClick={() => setFilter(filter.key, '', filter.fallback)}>{filter.label}<X size={11} /></button>)}
        <button type="button" className="text-link filter-clear" onClick={clearAll}>Clear all</button>
      </div>}
      {loading || error ? <CatalogueState loading={loading} error={error} /> : <>
        <div className="catalogue-count"><span>{visibleProducts.length} {visibleProducts.length === 1 ? 'PIECE' : 'PIECES'}{activeFilters.length > 0 && ` OF ${products.length}`}</span><span>MADE FOR YOUR CAMPUS DAYS</span></div>
        {visibleProducts.length ? <div className="product-grid catalogue-grid">{visibleProducts.map((product, index) => <ProductCard key={product.product_id} product={product} index={index} />)}</div> : <div className="empty-state"><Sparkles size={22} /><p>No pieces match those filters. Try widening your search.</p><button className="text-link" onClick={clearAll}>Clear filters <ArrowRight size={15} /></button></div>}
      </>}
    </main>
  )
}

function ProductPage({ products, loading, error }: { products: Product[]; loading: boolean; error: string }) {
  const { productId } = useParams()
  const product = products.find((item) => item.product_id === productId)
  const [size, setSize] = useState('')
  const [added, setAdded] = useState(false)

  if (loading || error) return <main className="product-detail-page"><Link className="text-link" to="/products"><ArrowLeft size={15} /> Back to the collection</Link><CatalogueState loading={loading} error={error} /></main>
  if (!product) return <main className="product-detail-page"><Link className="text-link" to="/products"><ArrowLeft size={15} /> Back to the collection</Link><p className="detail-missing">This piece isn’t in the catalogue.</p></main>

  const sizes = product.inventory ?? []
  return (
    <main className="product-detail-page">
      <Link className="text-link back-link" to="/products"><ArrowLeft size={15} /> Back to the collection</Link>
      <div className="product-detail">
        <div className="detail-image"><ProductImage product={product} priority /></div>
        <div className="detail-copy"><span className="eyebrow">CAMPUS CUSTOMS / {product.garment_type.toUpperCase()}</span><h1>{product.name}</h1><p className="detail-price">${product.price.toFixed(2)}</p><p className="detail-description">{product.description}</p>
          {product.colors.length > 0 && <div className="color-line"><span>COLOR</span>{product.colors.join(' / ')}</div>}
          {sizes.length > 0 && <fieldset className="size-picker"><legend>SELECT A SIZE</legend><div>{sizes.map((item) => <button key={item.size} aria-label={`${item.size}, ${item.quantity} in stock`} className={size === item.size ? 'size-option selected' : 'size-option'} disabled={item.quantity < 1} onClick={() => { setSize(item.size); setAdded(false) }}><span>{item.size}</span><small>{item.quantity}</small></button>)}</div><span className="size-note">Numbers show units available by size</span></fieldset>}
          {/* A greyed-out button with no explanation reads as broken, so the label itself says
              what is missing until a size is chosen. */}
          <button className={added ? 'button button-dark add-button is-added' : 'button button-dark add-button'} disabled={sizes.length > 0 && (!size || !sizes.find((item) => item.size === size)?.quantity)} onClick={() => setAdded(true)}>{added ? <><Check size={17} /> Added to your bag</> : sizes.length > 0 && !size ? <><ShoppingBag size={17} /> Select a size to continue</> : <><ShoppingBag size={17} /> Add to bag</>}</button>
          <p className="detail-footnote">A little piece of campus, made to go places.</p>
        </div>
      </div>
    </main>
  )
}

function AboutPage() {
  return <main className="about-page"><span className="eyebrow">OUR CORNER OF NEW HAVEN</span><h1>Campus is more<br />than a <em>place.</em></h1><div className="about-columns"><p className="about-lede">It’s a thousand small rituals. The walk across Old Campus. The first cold game. The sweatshirt that makes a new place feel like yours.</p><div><p>Campus Customs is a local-minded take on Yale spiritwear: familiar favorites, thoughtful details, and room for every kind of Bulldog to make the look their own.</p><p>We believe the best campus gear belongs to real campus life. It’s for the long afternoons, the loud Saturdays, and everything in between.</p><Link className="button button-dark" to="/products">Meet the collection <ArrowRight size={16} /></Link></div></div><div className="about-signoff"><span>MADE WITH CAMPUS IN MIND</span><span className="signoff-mark">CC</span></div></main>
}

type AuthResponse = {
  message: string
  user: { id: number; name: string; email: string; first_name: string | null; last_name: string | null }
}

function AccountPage({ create = false }: { create?: boolean }) {
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const title = create ? 'Make yourself at home.' : 'Good to see you again.'

  async function submitAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSuccess('')
    const form = event.currentTarget
    const values = new FormData(form)
    const password = String(values.get('password') ?? '')
    const confirmPassword = String(values.get('confirm_password') ?? '')

    if (create && password !== confirmPassword) {
      setError('Your passwords do not match.')
      return
    }

    const payload = create
      ? {
          first_name: String(values.get('first_name') ?? ''),
          last_name: String(values.get('last_name') ?? ''),
          email: String(values.get('email') ?? ''),
          password,
          confirm_password: confirmPassword,
        }
      : { email: String(values.get('email') ?? ''), password }

    setSubmitting(true)
    try {
      const response = await fetch(`${API_BASE}/api/auth/${create ? 'register' : 'login'}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const result = await response.json() as AuthResponse | { detail?: string | { msg: string }[] }
      if (!response.ok) {
        const detail = (result as { detail?: string | { msg: string }[] }).detail
        const message = Array.isArray(detail) ? detail.map((item) => item.msg).join(' ') : detail
        throw new Error(typeof message === 'string' ? message : 'We could not complete that request.')
      }

      const authenticated = result as AuthResponse
      const firstName = authenticated.user.first_name || authenticated.user.name
      setSuccess(create ? `Welcome, ${firstName}. Your account is ready.` : `Welcome back, ${firstName}. You’re signed in.`)
      window.dispatchEvent(new Event('campus-auth-changed'))
      form.reset()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'The account service could not be reached.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="account-page">
      <div className="account-mark">CC</div>
      <span className="eyebrow">CAMPUS CUSTOMS / YOUR ACCOUNT</span>
      <h1>{title}</h1>
      <p>{create ? 'Join us for the next chapter.' : 'Pick up right where you left off.'}</p>
      <form className="account-form" onSubmit={submitAccount}>
        {create && <>
          <label>FIRST NAME<input name="first_name" autoComplete="given-name" required maxLength={80} placeholder="First name" /></label>
          <label>LAST NAME<input name="last_name" autoComplete="family-name" required maxLength={80} placeholder="Last name" /></label>
        </>}
        <label>EMAIL ADDRESS<input name="email" autoComplete="email" type="email" required maxLength={254} placeholder="you@example.com" /></label>
        <label>PASSWORD<input name="password" autoComplete={create ? 'new-password' : 'current-password'} type="password" required minLength={create ? 8 : 1} maxLength={128} placeholder={create ? 'At least 8 characters' : 'Your password'} /></label>
        {create && <label>CONFIRM PASSWORD<input name="confirm_password" autoComplete="new-password" type="password" required minLength={8} maxLength={128} placeholder="Enter your password again" /></label>}
        {error && <p className="account-feedback error-feedback" role="alert">{error}</p>}
        {success && <p className="account-feedback success-feedback" role="status">{success}</p>}
        <button className="button button-dark" type="submit" disabled={submitting}>{submitting ? 'Please wait…' : success && !create ? <><Check size={17} /> Signed in</> : success ? <><Check size={17} /> Account created</> : create ? 'Create account' : 'Log in'} <ArrowRight size={16} /></button>
      </form>
      <div className="account-switch">{create ? 'Already a member?' : 'New around here?'} <Link to={create ? '/login' : '/create-account'}>{create ? 'Log in' : 'Create account'} <ArrowUpRight size={14} /></Link></div>
      <p className="account-demo-note">Your password is stored as a salted hash, never as readable text.</p>
    </main>
  )
}

type ChatProduct = {
  product_id: string
  name: string
  garment_type: string
  description: string
  price: number
  image_url: string
  product_url: string
  available_sizes: { size: string; quantity: number }[]
  total_stock: number
}
type ChatMessage = { role: 'assistant' | 'user'; text: string; products?: ChatProduct[]; kind?: 'error' }
type ChatApiResponse = { message: string; products: ChatProduct[] }
type StoredChatMessage = { role: 'assistant' | 'user'; content: string; products: ChatProduct[]; created_at: string }

// Slightly longer than the backend's own agent timeout, so a server-side 504 surfaces its
// specific message instead of being masked by the browser giving up first.
const REQUEST_TIMEOUT_MS = 65000
const ERROR_BY_STATUS: Record<number, string> = {
  429: 'You are sending messages a little too quickly. Give it a few seconds and try again.',
  502: 'The assistant hit a problem answering that. Please try again.',
  503: 'The assistant is not configured right now. Please let the Campus Customs team know.',
  504: 'That took longer than expected. Please try that question again.',
}

function ChatResultProductCard({ product, onNavigate }: { product: ChatProduct; onNavigate: () => void }) {
  const availableSizes = product.available_sizes.filter((item) => item.quantity > 0).map((item) => item.size)

  return <Link className="chat-product" to={product.product_url} onClick={onNavigate}>
    <img src={`${API_BASE}${product.image_url}`} alt={product.name} loading="eager" />
    <span className="chat-product-copy"><strong>{product.name}</strong><small>{product.garment_type} · ${product.price.toFixed(2)}</small><small className="chat-product-description">{product.description}</small><small>{product.total_stock} in stock · Sizes: {availableSizes.join(', ') || 'currently unavailable'}</small></span>
    <ArrowUpRight size={14} />
  </Link>
}

function ChatWidget() {
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [pending, setPending] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [loggedIn, setLoggedIn] = useState(false)
  const [lastMessage, setLastMessage] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([{ role: 'assistant', text: 'Hey there. Looking for something specific?' }])
  const endRef = useRef<HTMLDivElement>(null)
  const newestProductsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let active = true
    async function loadStoredConversation() {
      setHistoryLoading(true)
      try {
        const userResponse = await fetch(`${API_BASE}/api/auth/me`, { credentials: 'include' })
        if (!userResponse.ok) {
          if (active) setLoggedIn(false)
          return
        }
        if (active) setLoggedIn(true)
        const historyResponse = await fetch(`${API_BASE}/api/chat/history`, { credentials: 'include' })
        if (!historyResponse.ok) return
        const history = await historyResponse.json() as { messages: StoredChatMessage[] }
        if (active && history.messages.length) {
          setMessages(history.messages.map((item) => ({ role: item.role, text: item.content, products: item.products })))
        }
      } catch {
        if (active) setLoggedIn(false)
      } finally {
        if (active) setHistoryLoading(false)
      }
    }

    void loadStoredConversation()
    const reloadAfterAuthentication = () => { void loadStoredConversation() }
    window.addEventListener('campus-auth-changed', reloadAfterAuthentication)
    return () => {
      active = false
      window.removeEventListener('campus-auth-changed', reloadAfterAuthentication)
    }
  }, [])

  useEffect(() => {
    if (messages[messages.length - 1]?.products?.length) {
      newestProductsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } else {
      endRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, open, pending])

  // A ref, not the `pending` state, guards submission: state updates are async, so two fast
  // submits could both read `pending === false` and fire duplicate paid agent calls.
  const inFlight = useRef(false)

  async function submitMessage(text: string, { isRetry = false } = {}) {
    if (!text || inFlight.current || historyLoading) return
    inFlight.current = true
    setPending(true)
    setMessages((current) => {
      const withoutErrors = current.filter((message) => message.kind !== 'error')
      return isRetry ? withoutErrors : [...withoutErrors, { role: 'user', text }]
    })
    setLastMessage(text)

    const productMatch = location.pathname.match(/^\/products\/([^/]+)$/)
    const history = messages
      .filter((message) => message.kind !== 'error')
      .slice(-12)
      .map(({ role, text: content }) => ({ role, content }))

    const controller = new AbortController()
    const timer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          message: text,
          history,
          page_context: {
            current_path: location.pathname,
            product_id: productMatch ? decodeURIComponent(productMatch[1]) : null,
          },
        }),
      })
      if (!response.ok) {
        const detail = await response.json().then((body: { detail?: string }) => body.detail).catch(() => undefined)
        throw new Error(detail || ERROR_BY_STATUS[response.status] || 'The assistant could not respond right now.')
      }
      const answer = await response.json() as ChatApiResponse
      setMessages((current) => [...current, { role: 'assistant', text: answer.message, products: answer.products }])
    } catch (requestError) {
      const aborted = requestError instanceof DOMException && requestError.name === 'AbortError'
      const text = aborted
        ? 'That took longer than expected. The assistant may still be busy — try again in a moment.'
        : requestError instanceof TypeError
          ? 'We could not reach the Campus Customs assistant. Check your connection and try again.'
          : requestError instanceof Error ? requestError.message : 'The assistant could not respond right now.'
      setMessages((current) => [...current, { role: 'assistant', text, kind: 'error' }])
    } finally {
      window.clearTimeout(timer)
      inFlight.current = false
      setPending(false)
    }
  }

  function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const text = input.trim()
    if (!text) return
    setInput('')
    void submitMessage(text)
  }

  return <>
    {open && <section className="chat-panel" aria-label="Campus Customs chat"><header className="chat-header"><span className="chat-avatar"><Sparkles size={17} /></span><div><strong>Campus Customs</strong><small>{loggedIn ? 'YOUR SAVED CONVERSATION' : 'YOUR CAMPUS SIDEKICK'}</small></div><button className="icon-button" aria-label="Close chat" onClick={() => setOpen(false)}><X size={18} /></button></header><div className="chat-messages" aria-busy={pending || historyLoading}>{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`chat-turn ${message.role}`} ref={message.products?.length ? newestProductsRef : undefined}>{message.kind === 'error' ? <div className="chat-message chat-error" role="alert"><span className="chat-error-head"><AlertCircle size={13} /> Message not sent</span>{message.text}{lastMessage && <button type="button" className="chat-retry" onClick={() => void submitMessage(lastMessage, { isRetry: true })} disabled={pending}><RotateCcw size={12} /> Try again</button>}</div> : <div className={`chat-message ${message.role}`}>{message.text}</div>}{message.products && message.products.length > 0 && <div className="chat-products">{message.products.map((product) => <ChatResultProductCard key={product.product_id} product={product} onNavigate={() => setOpen(false)} />)}</div>}</div>)}{(pending || historyLoading) && <div className="chat-message assistant chat-pending" role="status" aria-live="polite"><span className="chat-typing" aria-hidden="true"><i /><i /><i /></span>{historyLoading ? 'Loading your conversation…' : 'Checking the collection…'}</div>}<div ref={endRef} /></div><form className="chat-form" onSubmit={sendMessage}><input aria-label="Message Campus Customs" value={input} onChange={(event) => setInput(event.target.value)} placeholder={pending ? 'Waiting for a reply…' : 'Ask about the collection…'} disabled={pending || historyLoading} /><button aria-label="Send message" disabled={!input.trim() || pending || historyLoading}>{pending ? <span className="chat-send-spinner" /> : <Send size={16} />}</button></form><div className="chat-footer">{loggedIn ? 'Your conversation is saved to your account' : 'Guest conversations are not saved'}</div></section>}
    <button className={open ? 'chat-toggle is-open' : 'chat-toggle'} aria-label={open ? 'Close Campus Customs chat' : 'Open Campus Customs chat'} onClick={() => setOpen(!open)}>{open ? <X size={21} /> : <><MessageCircle size={19} /><span>Need a hand?</span></>}</button>
  </>
}

function Footer() {
  return <footer className="site-footer"><Link className="footer-wordmark" to="/">CAMPUS<br />CUSTOMS<span>®</span></Link><div className="footer-links"><Link to="/products">Shop</Link><Link to="/about">Our story</Link><a href="mailto:hello@campuscustoms.example">Get in touch</a></div><span className="footer-credit">NEW HAVEN, CONNECTICUT<br />MADE FOR THE MOMENT</span></footer>
}

function Storefront() {
  const { products, loading, error } = useProducts()
  const navigate = useNavigate()

  useEffect(() => { window.scrollTo({ top: 0, behavior: 'instant' }) }, [navigate])

  return (
    <div className="storefront-shell"><Header /><Routes>
      <Route path="/" element={<HomePage products={products} loading={loading} error={error} />} />
      <Route path="/products" element={<ProductsPage products={products} loading={loading} error={error} />} />
      <Route path="/products/:productId" element={<ProductPage products={products} loading={loading} error={error} />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/login" element={<AccountPage />} />
      <Route path="/create-account" element={<AccountPage create />} />
      <Route path="*" element={<main className="not-found"><span className="eyebrow">PAGE NOT FOUND</span><h1>Lost on campus?</h1><Link className="button button-dark" to="/">Head home <ArrowRight size={16} /></Link></main>} />
    </Routes><Footer /><ChatWidget /></div>
  )
}

export default function App() {
  return <BrowserRouter><Storefront /></BrowserRouter>
}
