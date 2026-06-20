## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (like `<pre>` with `overflow-x: auto`) must be focusable using `tabindex="0"`, have visible focus styles (`:focus-visible`), and proper ARIA labeling (`aria-labelledby`) so keyboard users can access and interact with them. Additionally, dynamically updated UI containers should use `aria-live` attributes so screen readers announce content updates.
**Action:** Ensure all scrollable overflow containers have `tabindex="0"`, focus indicators, and semantic labels. Add `aria-live="polite"` to sections updated asynchronously via JavaScript (e.g., job lists, context loading) as done in `index.html`.
