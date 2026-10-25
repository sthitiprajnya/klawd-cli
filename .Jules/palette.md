## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-12-01 - Accessible Asynchronous UI Updates
**Learning:** Dynamic UI containers that fetch and render content asynchronously are silent to screen readers by default.
**Action:** Always include the aria-live="polite" attribute on asynchronous data containers to ensure screen readers gracefully announce incoming content.
