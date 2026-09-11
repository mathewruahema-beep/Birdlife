# Patterns: website (WordPress, WooCommerce, WP Engine, Cloudflare)

Seeded 11 Sep 2026 from the skills; doctrine in `birdlife-wordpress` and
`birdlife-cloudflare`.

### "The site is throwing 504s and the cart is timing out"
- **Seen**: Jul 2026 (peak ~9 Jul)
- **Cause**: distributed automated flood of `/cart/?remove_item=…` cycling four product IDs; cart pages are uncacheable so every hit reached PHP and exhausted workers.
- **Fix**: WP Engine Web Rules Deny rule ranked first (URI `^/cart`, query contains `remove_item=`, Referer not `birdlife\.org\.au`). Tier 2, applied by ICT in the WP Engine portal. Not a Cloudflare change.
- **Verify**: 5xx count on `/cart` in WP Engine logs drops; watch for false positives from privacy browsers that strip Referer.
- **Doctrine**: `birdlife-wordpress`, cart-flood incident; `birdlife-cloudflare` (where the durable control should live).

### "A paid WooCommerce order has no Salesforce Opportunity"
- **Seen**: two real paid orders ("Salesforce UUID: None"), Jul 2026; ~10% of sync attempts fail on both envs
- **Cause**: two mechanisms. The miniOrange write-back gap (SF Id not written to post meta), and field-level security missing for the integration user on `npe01__Opportunity__c` fields.
- **Fix**: grant FLS to the integration user on every mapped field before first sync; run the write-back test (MO-05) before trusting a mapping. Tier 3 for FLS (Salesforce admin), Tier 2 for the plugin test.
- **Verify**: the order carries `transaction_id`, `salesforce_Opportunity_ID`, `salesforce_npe01__OppPayment__c_ID` and `mo_sf_sync_line_item_ids`.
- **Doctrine**: `birdlife-wordpress`, integration stack; `birdlife-ict-assistant/references/reference.md`, data-flow fingerprint.

### "Salesforce Case emails never create Asana tasks"
- **Seen**: standing, Aug 2026
- **Cause**: `birdlife.org.au` SPF does not include Salesforce's senders, so Asana's inbound mail treats the message as spoofed.
- **Fix**: not done. SPF include plus Salesforce DKIM, as a reviewed domain-wide change with rollback. Tier 2.
- **Verify**: send a test Case email to the Asana address and see the task appear; check Authentication-Results headers.
- **Doctrine**: `birdlife-cloudflare`, email authentication runbook; `birdlife-asana`, the email rule.
