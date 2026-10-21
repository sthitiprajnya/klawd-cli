## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Asynchronous Content Accessibility
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (e.g., job lists, skill loading) are completely invisible to screen readers unless explicitly marked.
**Action:** Always include the aria-live="polite" attribute on asynchronous data containers to ensure screen readers announce content updates to visually impaired users.
