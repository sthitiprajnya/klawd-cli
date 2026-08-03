## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` tags with `overflow: auto`) are inaccessible to keyboard-only users because they cannot be focused, preventing them from scrolling the content using arrow keys.
**Action:** Always make scrollable containers focusable by adding `tabindex="0"` and ensure they have an accessible name using `aria-labelledby` pointing to their descriptive heading.
