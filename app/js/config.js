// Central configuration. Everything environment-specific lives here so the
// static bundle can move between hosts (Cloudflare Pages, WP Engine subdir)
// without code changes.

export const CONFIG = {
  siteBase: 'https://birdlife.org.au',
  apiBase: 'https://birdlife.org.au/wp-json',

  // Deployed member-proxy Worker (worker/member-proxy.js). Leave empty until
  // it exists — the Membership view then shows join/renew links only.
  // NEVER put WooCommerce or Salesforce credentials in this file: this bundle
  // is public. All keys live in Worker secrets.
  memberApiBase: '',

  postsPerPage: 10,

  // 'auto'  — use live API, fall back to bundled sample content if unreachable
  // 'on'    — always sample content (development)
  // 'off'   — live only, show an error state if unreachable
  demoMode: 'auto',

  // Public membership tiers. Prices must be confirmed with Supporter Care
  // before launch — the public site has previously shown superseded prices.
  // Financial Hardship and Free tiers are deliberately absent: they are
  // Supporter Care / Board controlled and not publicly listed.
  membershipTiers: [
    {
      name: 'Individual',
      price: 84,
      period: 'year',
      blurb: 'Full membership for one person.',
      features: ['Australian Birdlife magazine', 'Member events and activities', 'Voting rights'],
    },
    {
      name: 'Concession',
      price: 65,
      period: 'year',
      blurb: 'Concession card holders — honour system.',
      features: ['All Individual benefits', 'Concession pricing, no verification required'],
    },
    {
      name: 'Family',
      price: 132,
      period: 'year',
      blurb: 'One primary member plus up to six family members.',
      features: ['All Individual benefits', 'Covers 2–7 people at one address'],
    },
  ],
  joinUrl: 'https://birdlife.org.au/get-involved/membership/',

  // Staff quick links. URLs only — no data, no credentials.
  staff: {
    dashboardUrl: 'https://claude.ai/code/artifact/3aa92e1f-c8d7-4a91-95ad-c6dcd5db7606',
    zeusQueueUrl: 'https://birdlifeaustralia.lightning.force.com/lightning/o/Case/list',
    asanaProjectUrl: 'https://app.asana.com/0/1211042432693678/list',
    repoUrl: 'https://github.com/mathewruahema-beep/birdlife',
  },
};
