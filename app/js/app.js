// BirdLife Companion — hash-routed single page app. No framework, no build.

import { CONFIG } from './config.js';
import { state, getPosts, getPost, getCategories, getEvents, getMemberStatus } from './api.js';

const view = document.getElementById('view');

// ---------------------------------------------------------------- utilities

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
));

// WP "rendered" HTML is from our own site but still gets sanitised: scripts,
// embeds and event handlers are stripped before it touches the DOM.
function sanitizeHtml(html) {
  const doc = new DOMParser().parseFromString(html ?? '', 'text/html');
  doc.querySelectorAll('script, style, iframe, object, embed, form, link, meta').forEach(el => el.remove());
  doc.querySelectorAll('*').forEach(el => {
    for (const attr of [...el.attributes]) {
      const name = attr.name.toLowerCase();
      const val = attr.value.trim().toLowerCase();
      if (name.startsWith('on') || ((name === 'href' || name === 'src') && val.startsWith('javascript:'))) {
        el.removeAttribute(attr.name);
      }
    }
  });
  return doc.body.innerHTML;
}

const stripTags = (html) => sanitizeHtml(html).replace(/<[^>]+>/g, '').trim();

const fmtDate = (iso) => {
  const d = new Date(iso);
  return isNaN(d) ? '' : d.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
};

function updateBadges() {
  document.getElementById('offline-badge').hidden = navigator.onLine;
  document.getElementById('demo-badge').hidden = !state.demoActive;
}

function skeletons(n = 3) {
  view.innerHTML = Array.from({ length: n }, () => '<div class="skeleton"></div>').join('');
}

function errorState(message, retryHash) {
  view.innerHTML = `
    <div class="state">
      <p>${esc(message)}</p>
      <a class="btn secondary" href="${esc(retryHash)}" onclick="location.reload()">Try again</a>
    </div>`;
}

// ------------------------------------------------------------------- router

const routes = [
  { re: /^#\/news$/, render: renderNews, tab: 'news' },
  { re: /^#\/article\/(\d+)$/, render: (m) => renderArticle(m[1]), tab: 'news' },
  { re: /^#\/events$/, render: renderEvents, tab: 'events' },
  { re: /^#\/membership$/, render: renderMembership, tab: 'membership' },
  { re: /^#\/staff$/, render: renderStaff, tab: 'staff' },
];

async function route() {
  const hash = location.hash || '#/news';
  const match = routes.map(r => ({ r, m: hash.match(r.re) })).find(x => x.m);
  if (!match) { location.hash = '#/news'; return; }

  document.querySelectorAll('.tab').forEach(t =>
    t.classList.toggle('active', t.dataset.tab === match.r.tab));

  try {
    await match.r.render(match.m);
  } catch (err) {
    errorState(`Couldn't load this view (${err.message ?? err}).`, hash);
  }
  updateBadges();
  view.focus({ preventScroll: true });
  window.scrollTo(0, 0);
}

// -------------------------------------------------------------------- views

let newsFilter = { search: '', category: null };

async function renderNews() {
  skeletons();
  const [posts, cats] = await Promise.all([getPosts(newsFilter), getCategories()]);

  const chips = cats.slice(0, 8).map(c => `
    <button class="chip" data-cat="${c.id}" aria-pressed="${newsFilter.category === c.id}">${esc(c.name)}</button>
  `).join('');

  const cards = posts.map(p => `
    <a class="card post-card" href="#/article/${p.id}">
      ${p.image ? `<img class="hero" src="${esc(p.image)}" alt="" loading="lazy">` : ''}
      <div class="post-body">
        <div class="post-meta">${esc(p.categories[0] ?? 'News')} · ${fmtDate(p.date)}</div>
        <h2>${sanitizeHtml(p.title)}</h2>
        <p class="post-excerpt">${esc(stripTags(p.excerpt).slice(0, 160))}…</p>
      </div>
    </a>
  `).join('');

  view.innerHTML = `
    <h1>News</h1>
    <div class="toolbar">
      <input type="search" id="news-search" placeholder="Search news…" value="${esc(newsFilter.search)}" aria-label="Search news">
    </div>
    ${chips ? `<div class="chips" role="group" aria-label="Filter by category">${chips}</div>` : ''}
    ${cards || '<div class="state"><p>No articles found.</p></div>'}
    <p class="small muted">Content from <a href="${CONFIG.siteBase}" target="_blank" rel="noopener">birdlife.org.au</a>.</p>
  `;

  document.getElementById('news-search').addEventListener('change', (e) => {
    newsFilter.search = e.target.value.trim();
    renderNews();
  });
  view.querySelectorAll('.chip').forEach(chip => chip.addEventListener('click', () => {
    const id = Number(chip.dataset.cat);
    newsFilter.category = newsFilter.category === id ? null : id;
    renderNews();
  }));
}

async function renderArticle(id) {
  skeletons(2);
  const p = await getPost(id);
  if (!p) { errorState('Article not found.', '#/news'); return; }
  view.innerHTML = `
    <a class="backlink" href="#/news">← All news</a>
    ${p.image ? `<div class="article-hero"><img src="${esc(p.image)}" alt=""></div>` : ''}
    <div class="post-meta">${esc(p.categories[0] ?? 'News')} · ${fmtDate(p.date)}</div>
    <h1>${sanitizeHtml(p.title)}</h1>
    <div class="article-content">${sanitizeHtml(p.content)}</div>
    <div class="btn-row">
      <a class="btn secondary" href="${esc(p.link)}" target="_blank" rel="noopener">View on birdlife.org.au</a>
    </div>
  `;
}

async function renderEvents() {
  skeletons();
  const events = await getEvents();

  if (!events) {
    view.innerHTML = `
      <h1>Events</h1>
      <div class="card">
        <p>The website doesn't expose an events API yet, so events can't be listed in-app.</p>
        <p class="small muted">If The Events Calendar (or similar) is enabled on the site, this view lights up automatically.</p>
        <div class="btn-row">
          <a class="btn" href="${CONFIG.siteBase}/events/" target="_blank" rel="noopener">Browse events on the website</a>
        </div>
      </div>`;
    return;
  }

  view.innerHTML = `
    <h1>Events</h1>
    ${events.map(e => `
      <div class="card">
        <div class="post-meta">${fmtDate(e.date)}${e.venue ? ` · ${esc(e.venue)}` : ''}</div>
        <h2>${sanitizeHtml(e.title)}</h2>
        <p class="post-excerpt">${esc(stripTags(e.excerpt))}</p>
        <div class="btn-row"><a class="btn secondary" href="${esc(e.link)}" target="_blank" rel="noopener">Details</a></div>
      </div>
    `).join('')}
  `;
}

async function renderMembership() {
  const tiers = CONFIG.membershipTiers.map(t => `
    <div class="card tier">
      <h2>${esc(t.name)}</h2>
      <div class="price">$${t.price} <span>/ ${esc(t.period)}</span></div>
      <p class="small muted">${esc(t.blurb)}</p>
      <ul>${t.features.map(f => `<li>${esc(f)}</li>`).join('')}</ul>
      <a class="btn" href="${esc(CONFIG.joinUrl)}" target="_blank" rel="noopener">Join / renew</a>
    </div>
  `).join('');

  view.innerHTML = `
    <h1>Membership</h1>
    <div class="card" id="member-status-card">
      <h2>My membership</h2>
      <p class="muted" id="member-status-body">Checking…</p>
    </div>
    <div class="tier-grid">${tiers}</div>
    <p class="small muted">Other membership types (hardship, honorary) are arranged through
      <a href="${CONFIG.siteBase}/contact/" target="_blank" rel="noopener">Supporter Care</a>.
      Joining and payment happen securely on birdlife.org.au.</p>
  `;

  const body = document.getElementById('member-status-body');
  if (!CONFIG.memberApiBase) {
    body.innerHTML = `Member sign-in is coming soon. Until then, manage your membership
      <a href="${CONFIG.siteBase}/my-account/" target="_blank" rel="noopener">on the website</a>.`;
    return;
  }
  try {
    const s = await getMemberStatus();
    body.innerHTML = s?.active
      ? `<span class="pill ok">Active</span> ${esc(s.tier)} — renews ${fmtDate(s.renewsOn)}`
      : `<span class="pill warn">No active membership found</span>`;
  } catch {
    body.textContent = 'Could not reach the membership service. Try again later.';
  }
}

async function renderStaff() {
  // Visiting #/staff reveals the tab on this device from then on. Links only —
  // every destination enforces its own sign-in; nothing sensitive lives here.
  localStorage.setItem('blc:staff', '1');
  document.getElementById('staff-tab').hidden = false;

  const s = CONFIG.staff;
  view.innerHTML = `
    <h1>Staff — ICT</h1>
    <div class="card">
      <ul class="linklist">
        <li><a href="${esc(s.dashboardUrl)}" target="_blank" rel="noopener">
          ICT Operations Dashboard<span class="sub">Refreshed weekdays 08:00 AEST · Ask Zeus + Asana</span></a></li>
        <li><a href="${esc(s.zeusQueueUrl)}" target="_blank" rel="noopener">
          Ask Zeus case queue<span class="sub">Salesforce — filter list views to record type “Ask Zeus”</span></a></li>
        <li><a href="${esc(s.asanaProjectUrl)}" target="_blank" rel="noopener">
          IT Operations Project Plan<span class="sub">Asana</span></a></li>
        <li><a href="${esc(s.repoUrl)}" target="_blank" rel="noopener">
          Ops repository<span class="sub">Dashboard source, runbook and this app</span></a></li>
      </ul>
    </div>
    <div class="card">
      <h2>Morning health checks</h2>
      <p class="small muted">The weekday routine flags: open cases with no Type, New cases past
      first touch (2 business days), cases open &gt;30 days, Asana tasks Blocked &gt;14 days,
      overdue, sectionless or unassigned. Full thresholds are in the repository README.</p>
    </div>
    <p class="small muted">This tab only holds links — each destination has its own sign-in.
    It appears on this device because you've visited <code>#/staff</code>; clear site data to hide it.</p>
  `;
}

// -------------------------------------------------------------------- boot

if (localStorage.getItem('blc:staff') === '1') {
  document.getElementById('staff-tab').hidden = false;
}

window.addEventListener('hashchange', route);
window.addEventListener('online', updateBadges);
window.addEventListener('offline', updateBadges);
route();

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => { /* app works without it */ });
}
