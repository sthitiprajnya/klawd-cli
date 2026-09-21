## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Focusable Scrollable Regions
**Learning:** Elements with scrollable regions (e.g., `overflow: auto` or `overflow-x: auto` on `<pre>` tags) are not accessible to keyboard users by default because they cannot be focused to scroll.
**Action:** Ensure scrollable elements have `tabindex="0"`, a visible focus style, and proper ARIA labeling (like `aria-labelledby`) so keyboard users can navigate and scroll them.
