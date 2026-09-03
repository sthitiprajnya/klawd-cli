## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Focusable Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` blocks with `overflow: auto`) cannot be scrolled by keyboard users unless they are natively focusable.
**Action:** Always add `tabindex="0"` and an appropriate `aria-labelledby` or `aria-label` to elements with scrollable regions to ensure accessibility.
