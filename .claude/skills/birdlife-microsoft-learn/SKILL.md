---
name: birdlife-microsoft-learn
description: Operator knowledge for using the Microsoft Learn documentation connector to ground Azure, Entra, Intune, Defender, Graph, Power Automate, Logic Apps and Business Central work in current official documentation rather than recalled detail. Use before writing any Graph query, PowerShell hardening script, Conditional Access design, Logic App, Power Automate flow, or Business Central assessment. Trigger on "Microsoft docs", "Graph API", "PowerShell", "Azure how do I", "Entra documentation", "Business Central", or whenever a Microsoft configuration detail needs to be exact.
---

# Microsoft Learn — grounding connector

This is a documentation connector, not a system of record. It has no BirdLife data. Its value is that Microsoft configuration detail changes constantly and BirdLife's security work depends on getting exact API names, cmdlets, policy structures and deprecation dates right.

**It is authless and free to call. There is no reason to guess a Microsoft detail when this is available.**

## When to call it — non-negotiable cases

Ground in the docs before doing any of these:

- **Microsoft Graph queries** for user, device, sign-in, Conditional Access or licence data. The Entra remediation work runs on Graph, and the EH-to-Entra Logic App uses `$filter=mail eq '…'` plus `PATCH employeeId` — exact syntax matters.
- **Conditional Access policy design.** BirdLife's standard is report-only for 7-14 days with a documented rollback. Grant controls change (the "Approved client app" grant retired Mar 2026 and must become "App protection policy"). Verify the current control names.
- **PowerShell hardening scripts.** The M365 Hardening Automated PowerShell Guide creates CA policies via Graph PowerShell. Module cmdlets rename between versions.
- **Intune** compliance policies, configuration profiles, security baselines, ASR rules, BitLocker and Windows Update rings. BirdLife has **zero** ASR rules, BitLocker policies, update rings and assigned baselines — all four will be built from documentation.
- **Defender** — Secure Score actions, Tamper Protection, LSA Protection, Safe Links, Safe Attachments, anti-phishing presets. All currently off or absent.
- **Logic Apps and Power Automate** — the EH-to-Entra sync (`logic-emphero-entra-sync`) and the designed starter/leaver provisioning flows.
- **Key Vault** — managed identity access patterns and secret expiry metadata. The current Logic App fails to persist a rotated refresh token back to Key Vault; the fix comes from documentation.
- **Dynamics 365 Business Central** — licensing tiers, extension development, migration tooling. The BC business case cites Team Member ~$8-10, Essentials $80, Premium $110 per user per month with a claimed >$100k/yr saving. **That is an unquoted vendor-side claim.** Verify tier definitions and current pricing before repeating it.
- **Deprecation and end-of-support dates.** ADAL retired Sep 2025; the legacy MFA/SSPR policy migration was due 30 Sep 2025 and is overdue; Windows 10 hit EOL 14 Oct 2025; Intune's Android Device Administrator model hit EOL Dec 2024. BirdLife is behind on all four, so dates get quoted often and must be right.

## How to use the three tools

1. **`microsoft_docs_search`** — start here. Up to 10 chunks, ~500 tokens each, with title, URL and excerpt. Gives breadth.
2. **`microsoft_code_sample_search`** — when you need working code. Up to 20 samples. Optional `language` filter. Use for Graph PowerShell, Bicep, ARM, KQL, Power Automate expressions.
3. **`microsoft_docs_fetch`** — full page as markdown. Use when search results are partial, or when you need prerequisites, a full tutorial, or troubleshooting steps.

Search gives breadth. Code sample search gives working examples. Fetch gives depth.

## Operating rules
1. **Cite the URL** whenever a Microsoft configuration detail lands in a runbook, script or document. BirdLife's guides already carry stale internal dates; sourcing prevents that recurring.
2. **Never assert a cmdlet, Graph endpoint, policy control name or deprecation date from memory** when this connector is one call away.
3. Where documentation and an existing BirdLife guide disagree, say so explicitly. The Azure Security Programme Technical Implementation Guide v2.0 carries acknowledged stale internal dates.
4. Documentation describes what Microsoft supports. It does not describe what BirdLife has licensed. **Entra P1 only, no P2** means PIM, risk-based Conditional Access and automated Access Reviews are documented but unavailable. Check the licence before recommending a feature.
