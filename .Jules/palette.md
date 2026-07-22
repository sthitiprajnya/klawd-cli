## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-12-04 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` blocks with `overflow-x: auto`) are inaccessible to keyboard users because they cannot scroll them without a mouse if the element isn't focusable.
**Action:** Always add `tabindex="0"` and an appropriate ARIA label (e.g., `aria-labelledby`) to scrollable containers to ensure keyboard accessibility and screen reader support.
