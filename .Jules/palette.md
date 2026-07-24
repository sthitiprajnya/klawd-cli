## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Keyboard Accessible Scrollable Regions
**Learning:** Elements with scrollable content (like `overflow-x: auto` on `<pre>` tags) must be focusable so keyboard users can scroll them.
**Action:** Always add `tabindex="0"` and an `aria-labelledby` attribute pointing to a descriptive heading to make scrollable regions accessible to keyboard and screen reader users.
