## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Keyboard Accessibility for Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` blocks with `overflow-x: auto`) must be explicitly focusable (via `tabindex="0"`) and labeled (e.g., `aria-labelledby`) so keyboard-only users can focus and scroll them.
**Action:** Always add `tabindex="0"` and ARIA labels to containers with `overflow: auto` or `overflow-x: auto` to ensure they are accessible.
