## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-08-31 - Keyboard Accessibility for Scrollable Regions
**Learning:** Elements with CSS `overflow: auto` or `overflow-x: auto` (like `<pre>` blocks for code or logs) can trap content for keyboard-only users if they are not inherently focusable.
**Action:** Always add `tabindex="0"` and an appropriate `aria-labelledby` to scrollable regions to ensure keyboard accessibility.
