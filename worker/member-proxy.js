/**
 * BirdLife Companion — member API proxy (Cloudflare Worker).
 *
 * Purpose: the PWA is a public static bundle and must never hold WooCommerce
 * or Salesforce credentials. This Worker is the only place API keys live, as
 * Worker secrets:
 *
 *   wrangler secret put WC_CONSUMER_KEY
 *   wrangler secret put WC_CONSUMER_SECRET
 *
 * (Precedent for why this matters: live WooCommerce keys were previously
 * found embedded in routine prompts and had to be rotated — see the repo
 * README, "Credential exposure". Keys go in secrets, nowhere else.)
 *
 * STATUS: STUB. Deliberately not wired to live data yet, because member
 * lookups need an authentication story first (who is asking, and how do we
 * know?). The intended design, to be confirmed with Nina/Mathew before build:
 *
 *   1. Member signs in with their WordPress account via OAuth/OIDC
 *      (miniOrange OIDC is already in the stack) — the Worker validates the
 *      token, never sees the password.
 *   2. Worker calls WooCommerce REST (wc/v3, server-side keys) for the
 *      member's subscription: tier, status, next renewal date.
 *   3. Response is trimmed to the minimum the app needs — no addresses,
 *      no payment details, no order history.
 *
 * Salesforce remains the system of record for membership status; if the
 * WooCommerce answer and Salesforce disagree, Salesforce wins.
 */

const ALLOWED_ORIGINS = [
  'https://birdlife.org.au',
  // Add the deployed app origin(s) here, e.g. 'https://companion.birdlife.org.au'
];

function corsHeaders(request) {
  const origin = request.headers.get('Origin') ?? '';
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Vary': 'Origin',
  };
}

function json(request, status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders(request) },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(request) });
    }

    if (url.pathname === '/api/health') {
      return json(request, 200, { ok: true, service: 'birdlife-companion-member-proxy' });
    }

    if (url.pathname === '/api/member/status') {
      // Not implemented until the sign-in flow above is agreed and built.
      // Returning 501 (not fake data) so the app's error path is honest.
      return json(request, 501, {
        error: 'not_implemented',
        message: 'Member sign-in is not live yet. Manage your membership at birdlife.org.au/my-account/.',
      });
    }

    return json(request, 404, { error: 'not_found' });
  },
};
