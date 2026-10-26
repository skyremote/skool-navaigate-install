# Offers & Funnels

> Your active offers, sales funnels, and how content connects to revenue.
> This file is read by `/content-pipeline develop` to ensure every piece of content has a strategic path to your business goals.
>
> **Last updated:** {DATE}

---

## Active Offers

List every product or service you currently sell, from free to highest-ticket.

### 1. {Free Offer Name} (Free)

- **What:** {What the person gets}
- **Who it's for:** {Target audience segment}
- **CTA in content:** {How you mention this in your content}
- **Link:** {Where they go}

### 2. {Main Paid Offer} ({Price})

- **What:** {What the person gets}
- **Who it's for:** {Target audience segment}
- **CTA in content:** {How you mention this in your content — or "never pitched directly, sells through the funnel"}
- **Link:** {Where they go}

### 3. {Higher Tier / Premium} ({Price})

- **What:** {What the person gets}
- **Who it's for:** {Target audience segment}
- **CTA in content:** {How it appears}

{Add more offers as needed}

---

## Funnels

Map the journey from content consumer to customer.

### Primary Funnel

```
{Content platform} (awareness)
    |
    v
{Free offer / community / lead magnet}
    |
    v
{Nurture mechanism — email, community, calls}
    |
    v
{Paid offer conversion}
```

### {Secondary Funnel — if applicable}

```
{Different entry point}
    |
    v
{Different path to conversion}
```

---

## Audience → Offer Alignment

Map which audience segments drive toward which offers.

| Audience Segment | Content Pillar | On-Content CTA | Offer Positioning |
|-----------------|---------------|----------------|-------------------|
| {Segment 1} | {pillar} | {What you say/link to} | {How the offer is framed for this audience} |
| {Segment 2} | {pillar} | {What you say/link to} | {How the offer is framed} |
| {Segment 3} | {pillar} | {What you say/link to} | {How the offer is framed} |

---

## CTA Bank

Your go-to CTA wording, organized by context. Having these pre-written means you (and Claude) can quickly pick the right CTA without thinking.

### {Free offer CTA — used in most content}

> "{Your actual words when pitching the free offer}"

### {Paid offer CTA — when appropriate}

> "{Your actual words — or note if you never pitch directly}"

### {Engagement-only CTA — no product}

> "{Subscribe / follow / comment wording}"

---

## Offer Alignment Values (for Database)

When tagging content ideas with `offer_alignment`, use these values:

| Value | Meaning |
|-------|---------|
| {free_offer} | Drives to free offer |
| {main_product} | Proof engine for main product |
| {premium} | Positions for premium tier |
| {brand_only} | Pure authority building, no specific offer |

---

## Time-Sensitive Campaigns

{List any current campaigns, launches, or promotions that affect content strategy}

### {Campaign Name} ({Date Range})
- **Status:** {Active / Upcoming / Completed}
- **What:** {Brief description}
- **Content impact:** {How this affects what content to create}

---

> Written with /content-pipeline setup.
> Update it whenever your offers, funnels, or campaigns change.
