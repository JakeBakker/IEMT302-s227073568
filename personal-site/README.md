# Personal Professional Website

A clean, responsive, accessible single‑page site with dark mode. Built with plain HTML, CSS, and JS.

## Quick start

- Open `index.html` in a browser, or serve the folder locally:

```bash
python3 -m http.server --directory personal-site 8000
```

Then visit http://localhost:8000

## Customize

- Update your info in `index.html`:
  - Page title, description, and Open Graph meta tags
  - Name, role, bio, and social links
  - Experience, projects, and skills content
  - Résumé button link (use an external URL or add a file and link to it)
- Colors and layout in `styles.css`
- Behavior (theme toggle, mobile menu) in `script.js`
- Replace `favicon.svg` if desired

## Deploy

Any static hosting works:

- GitHub Pages
  - Push the `personal-site/` folder to your repo
  - In repo settings, set Pages to deploy from branch `main`, folder `/personal-site`
- Netlify / Vercel
  - Create a new project pointing to the repo; build command: none, output dir: `personal-site`
- Static bucket (S3, GCS)
  - Upload files with public read access

## Accessibility & performance

- Semantic HTML, accessible contrast, visible focus styles
- Respects `prefers-color-scheme` and `prefers-reduced-motion`
- Minimal JS; no frameworks