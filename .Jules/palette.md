## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (e.g., `overflow: auto`) must be focusable using `tabindex="0"` and have proper ARIA labeling (e.g., `aria-labelledby`) to be accessible for keyboard users. Dynamic UI containers updated asynchronously must use `aria-live="polite"` so screen readers announce content updates.
**Action:** Use semantic HTML (`<main>`, `<header>`), add `tabindex="0"` and `aria-labelledby` to scrollable regions like `<pre>`, and add `aria-live="polite"` to dynamically updated containers.
