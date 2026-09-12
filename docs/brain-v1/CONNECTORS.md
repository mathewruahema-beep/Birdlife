# Connectors

The skills in this plugin assume these connectors. They are account-level in Cowork, not
bundled with the plugin, so each person installing it needs them connected under their own
credentials with their own permissions.

## Approved in the project instruction block

| System | Connector | Write? | Notes |
|---|---|---|---|
| Salesforce | `Salesforce_Production` | Yes, data only | Configuration needs the Metadata API, which this cannot reach |
| WordPress | REST + Gravity Forms | Limited | See `birdlife-wordpress` for the read-key write gap |
| Asana | `Asana` | Yes | IT Operations Project Plan is the main board |
| Office 365 | `Microsoft_365` | User level only | **No Entra, Exchange admin, Intune or Defender** |
| Cloudflare | `Cloudflare_Developer_Platform` | Partial | Real edge controls sit outside the MCP |
| Zoom | `Zoom_for_Claude` | Read | |
| Miro | `Miro` | Yes | |

## Connected but outside the approved list

Flagged in ADR 0006, awaiting a governance decision.

| System | Why it matters |
|---|---|
| NetSuite | Production financial data. Added Aug 2026. |
| Stripe | **Live payments.** Every write is a real financial event. |
| Gmail, Google Drive, Google Calendar | Includes a personal account holding BirdLife work documents |
| Atlassian, Canva, Granola, Zapier, Microsoft Learn, Spotify | Lower risk utilities |
| AWS, Azure | Desktop bridge only |

## Not connected, and the gap this creates

**Microsoft Entra, Exchange admin, Intune, Defender.** This is the single biggest gap.
Roughly a third of helpdesk tickets need it. A read-only MCP exists at
`C:\azureintegration` (app `d8125f4d`); the write tier is built but waits on a separate app
registration and admin consent.

Until that lands, every identity write is prepare-and-hand-over. Skills must say so rather
than implying success. See ADR 0002.

## Never connect

Bitwarden.
