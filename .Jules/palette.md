## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (like `<pre>` with `overflow: auto`) are inaccessible to keyboard users unless explicitly made focusable, and dynamically updating UI elements (like job lists) are missed by screen readers.
**Action:** Always add `tabindex="0"` and `aria-labelledby` to scrollable regions to ensure keyboard focusability, and use `aria-live="polite"` on dynamically updating containers so screen readers announce changes.
