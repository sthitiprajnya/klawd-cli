## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` tags with `overflow-x: auto`) are inaccessible to keyboard-only users if they cannot receive focus, making it impossible to scroll horizontally to read the full content.
**Action:** Always add `tabindex="0"` and appropriate ARIA labels (e.g., `aria-labelledby` linking to a visible heading) to scrollable containers to ensure they can be focused and scrolled via keyboard.
