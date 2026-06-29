## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Accessible dynamic scrollable containers
**Learning:** Dynamic elements updated asynchronously via JS and scrollable containers (like pre) require explicit ARIA roles and tab indexing.
**Action:** Always add aria-live="polite" to asynchronous containers, and use tabindex="0" alongside aria-labelledby for visually scrollable elements to ensure they are fully navigable by keyboard and screen readers.
