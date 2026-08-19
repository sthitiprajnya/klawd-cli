## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Keyboard Accessible Scrollable Regions
**Learning:** Elements with scrollable content (like `<pre>` blocks with `overflow-x: auto`) are unreachable by keyboard users unless explicitly made focusable. Without focus, keyboard-only users cannot scroll to see hidden content.
**Action:** Always add `tabindex="0"` to scrollable regions and use `aria-labelledby` (linked to a descriptive heading) to ensure screen readers announce the region's purpose when focused.
