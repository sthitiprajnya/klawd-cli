## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (e.g., `overflow: auto` or `overflow-x: auto`) like `<pre>` blocks must be focusable using `tabindex="0"` and have visible focus styles to be accessible for keyboard users.
**Action:** Always add `tabindex="0"`, an appropriate ARIA label (`aria-labelledby` or `aria-label`), and visible focus styles to dynamically generated or static scrollable regions.
