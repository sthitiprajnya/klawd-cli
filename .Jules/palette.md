## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-11-11 - Add aria-live for Dynamic Content
**Learning:** Dynamic UI containers updated asynchronously via JavaScript must include the aria-live="polite" attribute so screen readers announce content updates.
**Action:** Always verify if asynchronous UI updates have aria-live="polite".
