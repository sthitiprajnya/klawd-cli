## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Dynamic and Scrollable Regions
**Learning:** Dynamic content loaded asynchronously needs `aria-live="polite"` for screen readers to announce updates. Additionally, `<pre>` tags (or any element) with `overflow-x: auto` are scrollable but inaccessible to keyboard-only users by default.
**Action:** Always add `tabindex="0"` and an appropriate `aria-labelledby` linking to a visible header to ensure keyboard and screen reader accessibility for scrollable regions, as well as `aria-live="polite"` to dynamically updated containers.
