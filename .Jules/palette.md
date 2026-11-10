## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Dynamic Container Updates
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (e.g., job lists, skill loading) do not announce their updates to screen readers by default.
**Action:** Always include the `aria-live="polite"` attribute on asynchronous dynamic containers to ensure content updates are announced to visually impaired users.
