---
name: birdlife-canva
description: Operator knowledge for BirdLife Australia's Canva account — the flagship brand kit and campaign kits, brand template autofill, and safe use for ICT and campaign collateral. Use for tasks involving design, branded documents, social assets, campaign creative, posters, or exporting designs. Trigger on "Canva", "brand kit", "design", "poster", "social tile", "template", "Aussie Bird Count creative", or a request for branded visual collateral.
---

# BirdLife Australia — Canva

## Brand kits — verified live

| Brand kit | ID |
|---|---|
| **BirdLife Australia flagship brand kit** | `kAFMW4XTNVg` |
| OnTrack | `kAF4r4guJpk` |
| Nature laws & Threatened Bird Images | `kAGC1NIBhTg` |
| Aussie Bird Count 2024 | `kAGDw5RhCcg` |
| Aussie Bird Count 2025 | `kAGwruHQrE8` |
| **2026 Aussie Bird Count** | `kAHQJhs-PZ4` |
| Advocacy Images | `kAGqevn8Nb8` |

**Always start from `kAFMW4XTNVg` (flagship) unless the work is campaign-specific.** For Aussie Bird Count work use `kAHQJhs-PZ4` (2026); the 2024 and 2025 kits are archives — note that 2026 currently shares a thumbnail with 2025, so confirm you are in the right one before producing anything public.

Entra holds **2 duplicate Canva enterprise-app registrations** — consolidate in the app access review.

## Context: Aussie Bird Count matters

ABC is BirdLife's flagship public campaign. The 2026 registration flow runs on Gravity Forms (form ID 15) at aussiebirdcount.org.au, with T&Cs closing Wed 29 Oct 2026. It handles **guardian details for minors and consent capture under the Privacy Act 1988 and the Australian Privacy Principles**. Any creative that drives registration should link to the live registration page, not a preview URL — the Gravity Forms preview URL `?gf_page=preview&id=15` bypasses server-side validation by design and has already caused a false test failure.

## Available tooling

`mcp__Canva__*` covers a lot:
- **Brand templates:** `search-brand-templates`, `get-brand-template-dataset`, **`create-design-from-brand-template`** (autofill), `create-brand-template-draft`, `publish-brand-template`
- **Generation:** `generate-design`, `generate-design-structured`, `create-design-from-candidate`, `import-design-from-url`
- **Editing:** `edit-design`, `resize-design`, `merge-designs`, `copy-design`, `read-design`
- **Assets and files:** `upload-asset-from-url`, `get-assets`, folders, `export-design`, `get-export-formats`
- **Review:** `list-comments`, `comment-on-design`, `reply-to-comment`, `request-outline-review`

**Autofill from a brand template is the highest-value pattern**: `get-brand-template-dataset` tells you the fields, then `create-design-from-brand-template` populates them. That is how you produce twenty branded assets consistently instead of twenty near-misses.

## Operating rules
1. **Search existing designs and brand templates before creating anything new.** BirdLife has seven brand kits and years of campaign assets.
2. Brand consistency is a real constraint for a national conservation charity. Use a brand kit; do not hand-pick colours.
3. **Never place supporter names, donor amounts, member data or staff security detail in a Canva design.** Canva designs get shared by link.
4. Confirm the correct campaign year before producing anything public. The 2025 and 2026 ABC kits look identical at thumbnail size.
5. Export and deliver the file as well as sharing the Canva link, so the asset survives access changes.
