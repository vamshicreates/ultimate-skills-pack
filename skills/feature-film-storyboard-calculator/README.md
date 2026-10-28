# Feature Film Storyboard Cost Calculator

A developer demo for estimating the credits and spend needed to storyboard a feature film.

## Files
- `index.html` — standalone interactive demo landing page. No build step or backend required.
- `SKILL.md` — reusable implementation skill/spec for a coding agent or developer.

## Run locally
Open `index.html` in a browser, or serve the folder locally:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Deploy demo
### GitHub Pages
1. Create a GitHub repository and upload `index.html`, `SKILL.md`, and `README.md`.
2. In repository Settings → Pages, choose the branch and root folder.
3. Save and open the generated Pages URL.

### Vercel
Import the repository into Vercel. The project is static and needs no build command; set the output directory to the repository root.

## Pricing configuration
In `index.html`, update the `CONFIG` object to change plan credits, subscription prices, top-up size/price, or per-image credit cost.

## Calculation model
- Images = scenes × attempts per scene
- Storyboard credits = images × 15
- Formatter credits = ceil(word count / 250), when enabled
- Total credits = storyboard credits + formatter credits
- Top-ups = ceil(max(0, total credits − plan credits) / 500)
- Total spend = subscription price + top-ups × ₹1,500

## Demo assumptions
The current estimator treats the formatter as one full pass through the supplied screenplay word count. Repeated text requests, failed calls, taxes, payment fees, or other product-specific usage are not modeled. Pricing values are based on the supplied screenshots and should be validated before production use.
