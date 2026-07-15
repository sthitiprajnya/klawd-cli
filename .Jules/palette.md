## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-07-15 - Semantic Elements and Accessible Dynamic Content
**Learning:** Using generic `<div>` tags for layout misses an opportunity to provide semantic structure to assistive technologies. Furthermore, when content updates dynamically (like a job queue or skills list fetching via JS), screen readers may not announce the changes, and scrollable regions (like `<pre>` for code output) cannot be accessed via keyboard if they lack `tabindex="0"`.
**Action:** Replace structural `<div>`s with semantic elements like `<main>`, `<header>`, and `<section>`. Add `aria-live="polite"` to containers that update asynchronously, and apply `tabindex="0"` with corresponding `aria-labelledby` labels to elements with `overflow: auto` (like scrollable `<pre>`) so keyboard users can navigate and read them.
