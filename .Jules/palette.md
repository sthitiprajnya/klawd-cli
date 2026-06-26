## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions
**Learning:** Elements with scrollable content regions (e.g., `overflow: auto` or `overflow-x: auto` like `<pre>`) cannot be reached by keyboard users by default, making the off-screen content inaccessible.
**Action:** Always add `tabindex="0"` to make the scrollable container focusable, use `aria-labelledby` linking to a visible heading for screen readers, and provide a clear `:focus-visible` styling indicator.
