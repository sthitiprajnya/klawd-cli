## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2025-01-01 - Scrollable Region Accessibility
**Learning:** Elements with scrollable content (like <pre> with overflow: auto) are inaccessible to keyboard-only users if they cannot receive focus.
**Action:** Always add tabindex="0" and an appropriate aria-label to scrollable containers so users can tab to them and scroll using arrow keys.
