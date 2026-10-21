## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-07-04 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` blocks with `overflow-x: auto`) must be focusable using `tabindex="0"` and have proper ARIA labeling (e.g., `aria-label`) to be accessible for keyboard users. Dynamic UI containers updated asynchronously must use `aria-live="polite"` to ensure screen readers announce content updates.
**Action:** Always ensure scrollable code blocks or data containers have focus styles, `tabindex="0"`, and appropriate ARIA attributes.
