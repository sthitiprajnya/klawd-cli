## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Semantic ARIA Live Regions
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (like job lists or skill loading blocks) are inherently inaccessible to screen readers unless specifically marked. They often appear to update "silently".
**Action:** Always include the `aria-live="polite"` attribute on containers that receive async content updates (e.g., `#jobs-container`, `#skills-container`, `#provenance-container`) to ensure screen readers announce the changes, and swap generic `<div>` tags with semantic landmarks like `<main>` and `<section>` to improve structural navigation.
