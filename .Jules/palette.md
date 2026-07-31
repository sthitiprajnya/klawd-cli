## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Dynamic Content Updates and Semantic HTML
**Learning:** Dynamic UI containers updated asynchronously via JavaScript must use `aria-live` attributes to ensure screen readers properly announce content updates. Also, using semantic HTML elements improves document structure and accessibility for assistive technologies.
**Action:** Add `aria-live="polite"` to dynamic containers and use `<main>`, `<header>`, and `<section>` instead of generic `<div>` wrappers.
