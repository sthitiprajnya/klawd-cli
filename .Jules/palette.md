## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-06-30 - Accessible Scrollable Regions and Dynamic Updates
**Learning:** Elements with `overflow: auto` or `overflow-x: auto` (like `<pre>` blocks displaying code or JSON) are not keyboard focusable by default, rendering their scrollable content inaccessible to keyboard users. Also, asynchronously updated content containers (like a jobs list or live status fields) won't be announced by screen readers unless marked appropriately.
**Action:** Always ensure scrollable containers have `tabindex="0"` and an `aria-labelledby` attribute pointing to a descriptive heading. Use `aria-live="polite"` on containers whose content is updated dynamically via JS.
