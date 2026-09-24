## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-12-10 - Accessible Scrollable Regions
**Learning:** Scrollable blocks (like <pre> with overflow-x: auto) hide content from keyboard users if they cannot receive focus.
**Action:** Ensure scrollable elements have tabindex="0" and an accessible name (e.g. aria-labelledby) so keyboard-only users can focus and scroll them.
