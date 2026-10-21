## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Keyboard Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (e.g., `overflow: auto`) and dynamic content updates must be made accessible to keyboard and screen reader users.
**Action:** Use `tabindex="0"` with appropriate `aria-labelledby` attributes to ensure users can focus and scroll through content like `<pre>` blocks, and add `aria-live="polite"` to dynamically updating containers like `#jobs-container` so screen readers announce changes.
