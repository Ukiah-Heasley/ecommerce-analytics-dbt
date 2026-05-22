# Dashboard style conventions

These are the rules baked into every page. Re-read before adding a chart.

## Palette — UC Berkeley
- **Primary accent:** `#003262` Berkeley Blue — the *one* color that draws the eye
- **Neutral context:** `#46535E` Pacific (slate) — everything that isn't the focal series
- **Secondary accent:** `#FDB515` California Gold — only when two series truly need to differ
- **Page background:** `#FAF5E6` soft cream-gold (a Berkeley-warm tint, not pure white)
- **Sign-bearing colors** (reserved, never categorical):
  - Positive: `#00A598` Lap Lane (teal)
  - Negative: `#EE1F60` Rose Garden
  - Warning: `#C4820E` Medalist (dark gold)
- Defined once in [evidence.config.yaml](evidence.config.yaml). Charts pick up the palette automatically.

## Titles
- **Insight-driven**, not descriptive. Title states the takeaway.
  - ✓ "Net revenue up 22% vs prior week"
  - ✗ "Net revenue by day"
- Subtitle (optional) carries methodology / units / time window.

## Chart selection — hard rules
- No pie / donut charts. Use horizontal bar.
- No dual-axis charts. Use two aligned charts or index to a common baseline.
- No 3D anything.
- Bar charts start at zero. Always.
- More than 4–5 series → small multiples, or highlight one and grey the rest.

## Decluttering
- Light or no gridlines. No chart borders, no plot-area borders, no legend borders.
- Remove the y-axis if bars are directly labeled.
- Remove the legend if lines/bars are directly labeled.
- Match decimal precision to what matters (revenue in millions doesn't need cents).

## Annotations
- Add a target line / prior-period reference where it sharpens the read.
- Annotate outliers and milestones with brief text.
- Source attribution is fine but small.

## Narrative structure per page
1. **Setup** — one sentence of context the reader needs.
2. **Tension** — the chart(s) that surface the problem or surprise.
3. **Resolution** — the insight and what to do about it.

## Accessibility
- 12 px minimum on text. Use the default sizing from the theme unless you have a reason.
- Never encode meaning in color alone — pair with labels or position.
- WCAG AA contrast for everything readable.

## When in doubt
If you can't state the chart's insight in one sentence, the chart isn't ready.
