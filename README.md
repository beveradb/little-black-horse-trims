# Little Black Horse Barefoot Trims

Static website for **Little Black Horse Barefoot Trims** -- Mariah Simmons' barefoot horse hoof trimming business in Columbia, SC.

**Live at:** https://littleblackhorse.com

## Quick Edits

This site auto-deploys on every push to `main`. To make content changes from your phone:

1. Open any file on [GitHub](https://github.com/beveradb/little-black-horse-trims)
2. Tap the pencil icon to edit
3. Make your change and commit
4. The site deploys automatically in ~30 seconds

### Common edits

| What | Where in `index.html` |
|------|----------------------|
| Phone number | Search for `344-3145` (appears in hero + contact) |
| Business name | Search for `Little Black Horse` |
| Owner name | Search for `Mariah Simmons` |
| Service descriptions | Search for `Barefoot Trimming`, `Hoof Building`, `Glue-Ons` |
| About text / philosophy | Search for `about-quote` and `about-text` |
| Location | Search for `Columbia` |
| Facebook page URL | Search for `61569612563299` (the FB page ID) |
| Review text | Search for `review-card` blocks |

### Adding gallery photos

1. Add the image to the `images/` folder
2. Add a new `<div class="gallery-item">` in the gallery section of `index.html`:
   ```html
   <div class="gallery-item"><img src="images/your-photo.jpg" alt="Description" loading="lazy"></div>
   ```
3. Commit and push -- the lightbox picks up new images automatically

## Architecture

Single-page static site. No build step, no dependencies, no framework.

```
index.html          # The entire site (HTML + CSS + JS inline)
images/             # All site images (logo, hero, gallery photos)
  logo.png          # Circular horse-head logo
  hero.jpg          # Hero background (Mariah trimming a horse)
  gallery-*.jpg     # Gallery photos (20 curated from Facebook)
.github/workflows/  # Auto-deploy on push to main
```

## Hosting

- **Cloudflare Pages** project: `little-black-horse-trims`
- **Domain:** `littleblackhorse.com` (DNS managed in Cloudflare)
- **Deploy:** Automatic via GitHub Actions on push to `main`
- **Fallback URL:** https://little-black-horse-trims.pages.dev

## Design

### Aesthetic: "Artisanal Equestrian Editorial"

The design draws from the hand-drawn logo's organic quality -- warm, earthy, and refined without feeling corporate. Think premium equestrian magazine meets rustic craft workshop.

### Typography

- **Headings:** [Cormorant Garamond](https://fonts.google.com/specimen/Cormorant+Garamond) -- elegant, high-contrast serif with editorial character
- **Body:** [Outfit](https://fonts.google.com/specimen/Outfit) -- clean geometric sans-serif that pairs well with the serif headings

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Espresso | `#1c1208` | Dark backgrounds, nav, footer, reviews section |
| Cream | `#faf5ed` | Primary background |
| Ivory | `#f0ebe2` | Cards, secondary backgrounds |
| Leather | `#7a5c3e` | Section labels, accents |
| Gold | `#c4943a` | Primary accent -- CTAs, stars, highlights, "Barefoot Trims" italic |
| Sage | `#5a7050` | Reviews badge |
| Parchment | `#e8e0d4` | Borders, dividers |

### Custom SVG Icons

Three hand-drawn style service icons designed to echo the logo's organic sketch quality:
- **Hoof outline** (barefoot trimming) -- simplified side-view hoof shape
- **Hoof with growth lines** (hoof building) -- upward growth arrows
- **Horseshoe** (glue-ons) -- composite shoe shape with detail dots

### Sections

1. **Hero** -- Cinematic photo overlay with staggered entry animations. Gold italic "Barefoot Trims". Mariah's name and phone number prominent. Dual CTAs.
2. **Services** -- Three-column grid with custom SVG icons. Clean borders, hover states.
3. **About** -- Two-column editorial layout. Left: large pull-quote with gold border. Right: philosophy text + stats (100%, 12 reviews, 287 followers).
4. **Gallery** -- CSS columns masonry layout (4 cols desktop, 2 mobile). 20 curated photos. Click-to-open lightbox with keyboard navigation.
5. **Reviews** -- Dark section with subtle cross pattern. Horizontal scroll carousel of 12 review cards with gold stars, decorative quotes, reply cards. "100% Recommend" badge.
6. **Facebook Updates** -- Facebook Page Plugin (live timeline sidebar) + 3 embedded posts.
7. **Contact** -- Split layout: details (phone, location, price) + CTA card.
8. **Footer** -- Faded logo, copyright, Facebook link.

### Effects

- **Grain texture overlay** -- Subtle SVG noise across the entire page for warmth
- **Scroll-triggered fade-ups** -- IntersectionObserver reveals sections as you scroll
- **Hero staggered animation** -- Logo, tagline, title, contact, CTAs animate in sequence
- **Lightbox** -- Frosted dark overlay, prev/next navigation, keyboard support (arrows + Escape), click-outside-to-close, image counter

## Content Source

All content was extracted from the [Facebook page](https://www.facebook.com/profile.php?id=61569612563299):
- 12 reviews (all 5-star, 100% recommend) spanning November 2024 -- April 2026
- 20 curated gallery photos from 159 downloaded
- About/philosophy text from posts
- Business info (phone, location, category)

Raw Facebook exports are in `facebook-export/` (gitignored).
