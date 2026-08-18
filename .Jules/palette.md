## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Dynamic Scrollable Regions
**Learning:** Dynamic UI containers updated asynchronously (e.g., job lists, skill loading) must use `aria-live` attributes (like `aria-live="polite"`) so screen readers announce content updates. Furthermore, elements with scrollable regions (e.g., `<pre>` with `overflow: auto`) must be focusable using `tabindex="0"` and have proper ARIA labeling (e.g., `aria-labelledby`) so keyboard users can access and scroll them.
**Action:** Always add `aria-live` to dynamic containers. Always add `tabindex="0"` and an `aria-labelledby` referencing a visible heading to scrollable regions.
