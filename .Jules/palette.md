## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions & Dynamic Content
**Learning:** When using `<pre>` tags or other elements with `overflow: auto` for scrollable content, screen reader users cannot access the hidden text without explicitly making it focusable. Additionally, dynamic content injected via JS needs `aria-live` to be announced.
**Action:** Always add `tabindex="0"` and an `aria-labelledby` linking to an existing header for scrollable text blocks, and `aria-live="polite"` for asynchronous UI containers like job lists or API responses.
