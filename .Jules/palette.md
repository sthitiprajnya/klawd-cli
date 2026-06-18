## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` tags with `overflow-x: auto`) must be focusable using `tabindex="0"` so keyboard users can navigate to them and scroll them using arrow keys. They must also have visible focus styles (like `:focus-visible`) and proper ARIA labeling to be accessible.
**Action:** Always verify scrollable regions are accessible by keyboard users and screen readers, not just mouse users.
