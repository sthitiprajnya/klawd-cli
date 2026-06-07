## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2025-02-12 - Keyboard Navigable Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` with `overflow-x: auto`) must be focusable using `tabindex="0"` and have visible focus styles (like `:focus-visible`) and proper ARIA labeling to be accessible for keyboard users. Furthermore, dynamic UI containers updated asynchronously must use `aria-live` attributes to ensure screen readers properly announce content updates.
**Action:** Always add `tabindex="0"`, `:focus-visible` styling, and descriptive ARIA labels to scrollable areas, and use `aria-live` for regions updated asynchronously by JavaScript.
