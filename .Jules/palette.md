## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions & Dynamic Updates
**Learning:** Elements with `overflow: auto` (like `<pre>` blocks) are inaccessible to keyboard users without `tabindex="0"`. Additionally, dynamically updated data containers must use `aria-live="polite"` so screen readers announce changes.
**Action:** Always add `tabindex="0"` and an `aria-labelledby` reference to scrollable text blocks, and apply `aria-live` to containers updated via JavaScript polls.
