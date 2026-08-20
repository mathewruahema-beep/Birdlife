// WordPress REST client with a localStorage stale-while-revalidate cache and
// a demo-data fallback for when the live API is unreachable (network policy,
// offline, or CORS misconfiguration).
//
// Only core wp/v2 endpoints are used. The site's "ACF to REST API" plugin is
// known-vulnerable and its endpoints must not be depended on here.

import { CONFIG } from './config.js';
import { DEMO_POSTS, DEMO_EVENTS, DEMO_CATEGORIES } from './demo-data.js';

const CACHE_PREFIX = 'blc:';
const CACHE_TTL_MS = 15 * 60 * 1000;
const FETCH_TIMEOUT_MS = 12 * 1000;

export const state = { demoActive: CONFIG.demoMode === 'on' };

function cacheGet(key) {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch { return null; }
}

function cacheSet(key, data) {
  try {
    localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({ t: Date.now(), data }));
  } catch { /* storage full or unavailable — cache is best-effort */ }
}

async function fetchJson(url) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(url, { signal: ctrl.signal, headers: { Accept: 'application/json' } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

// Cached GET: fresh cache → return it; else network → cache it; on failure a
// stale cache still wins over nothing.
async function cachedGet(pathAndQuery) {
  const cached = cacheGet(pathAndQuery);
  if (cached && Date.now() - cached.t < CACHE_TTL_MS) return cached.data;
  try {
    const data = await fetchJson(CONFIG.apiBase + pathAndQuery);
    cacheSet(pathAndQuery, data);
    return data;
  } catch (err) {
    if (cached) return cached.data;
    throw err;
  }
}

function normalisePost(p) {
  const media = p._embedded?.['wp:featuredmedia']?.[0];
  const terms = (p._embedded?.['wp:term'] ?? []).flat().filter(t => t?.taxonomy === 'category');
  return {
    id: p.id,
    date: p.date,
    link: p.link,
    title: p.title?.rendered ?? '',
    excerpt: p.excerpt?.rendered ?? '',
    content: p.content?.rendered ?? '',
    image: media?.media_details?.sizes?.medium_large?.source_url
        ?? media?.media_details?.sizes?.large?.source_url
        ?? media?.source_url ?? null,
    categories: terms.map(t => t.name),
  };
}

export async function getPosts({ page = 1, search = '', category = null } = {}) {
  if (CONFIG.demoMode === 'on') return demoPosts({ search, category });
  const q = new URLSearchParams({ per_page: String(CONFIG.postsPerPage), page: String(page), _embed: '1' });
  if (search) q.set('search', search);
  if (category) q.set('categories', String(category));
  try {
    const posts = await cachedGet(`/wp/v2/posts?${q}`);
    state.demoActive = false;
    return posts.map(normalisePost);
  } catch (err) {
    if (CONFIG.demoMode === 'auto') {
      state.demoActive = true;
      return demoPosts({ search, category });
    }
    throw err;
  }
}

export async function getPost(id) {
  if (state.demoActive || CONFIG.demoMode === 'on') {
    return DEMO_POSTS.find(p => p.id === Number(id)) ?? null;
  }
  try {
    const p = await cachedGet(`/wp/v2/posts/${Number(id)}?_embed=1`);
    return normalisePost(p);
  } catch {
    return DEMO_POSTS.find(p => p.id === Number(id)) ?? null;
  }
}

export async function getCategories() {
  if (CONFIG.demoMode === 'on') return DEMO_CATEGORIES;
  try {
    const cats = await cachedGet('/wp/v2/categories?per_page=20&orderby=count&order=desc&hide_empty=true');
    return cats.map(c => ({ id: c.id, name: c.name }));
  } catch {
    return state.demoActive ? DEMO_CATEGORIES : [];
  }
}

// Events: WordPress has no core events endpoint; the common ones are tried in
// order and null means "no events API" — the view then links to the website.
export async function getEvents() {
  if (CONFIG.demoMode === 'on' || state.demoActive) return DEMO_EVENTS;
  const candidates = [
    { path: '/tribe/events/v1/events?per_page=12', pick: d => d.events, map: e => ({
        id: e.id, title: e.title, date: e.start_date, venue: e.venue?.venue ?? '', link: e.url, excerpt: e.excerpt ?? '' }) },
    { path: '/wp/v2/events?per_page=12&_embed=1', pick: d => d, map: e => ({
        id: e.id, title: e.title?.rendered ?? '', date: e.date, venue: '', link: e.link, excerpt: e.excerpt?.rendered ?? '' }) },
  ];
  for (const c of candidates) {
    try {
      const data = await cachedGet(c.path);
      const items = c.pick(data);
      if (Array.isArray(items)) return items.map(c.map);
    } catch { /* try the next shape */ }
  }
  return null;
}

function demoPosts({ search, category }) {
  let posts = DEMO_POSTS;
  if (search) {
    const s = search.toLowerCase();
    posts = posts.filter(p => (p.title + p.excerpt).toLowerCase().includes(s));
  }
  if (category) {
    const cat = DEMO_CATEGORIES.find(c => c.id === category)?.name;
    posts = posts.filter(p => p.categories.includes(cat));
  }
  return posts;
}

// Member API — only ever through the deployed Worker proxy, never direct to
// WooCommerce. Returns null when the proxy isn't configured yet.
export async function getMemberStatus() {
  if (!CONFIG.memberApiBase) return null;
  return fetchJson(`${CONFIG.memberApiBase}/api/member/status`);
}
