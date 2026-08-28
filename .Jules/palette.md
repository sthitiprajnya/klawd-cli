## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-08-28 - Scrollable Region Accessibility
**Learning:** Elements with scrollable regions (like `<pre>` blocks with `overflow-x: auto`) cannot be scrolled by keyboard-only users unless they are explicitly focusable.
**Action:** Add `tabindex="0"` and an appropriate accessible name (e.g., via `aria-labelledby`) to scrollable regions to ensure keyboard accessibility.
