## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Dynamic and Scrollable Content
**Learning:** Elements that load dynamic content asynchronously (like lists or queues) need `aria-live="polite"` so screen readers announce updates. Furthermore, regions with scrollable content (like `<pre>` tags with `overflow-x: auto`) must be explicitly focusable via `tabindex="0"`, have a visible focus state (like `:focus-visible`), and be properly labeled (via `aria-labelledby`) so that keyboard and screen reader users can access and navigate them.
**Action:** Always add `aria-live` to dynamic containers, and ensure scrollable elements use `tabindex="0"`, `:focus-visible` styling, and appropriate ARIA labels for full accessibility.
