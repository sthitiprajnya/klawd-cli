## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions & Dynamic Content
**Learning:** Elements with scrollable content (like `overflow-x: auto`) cannot be scrolled by keyboard users by default, and dynamic content updates are missed by screen readers.
**Action:** Add `tabindex="0"` and `aria-labelledby` to scrollable containers for keyboard access, and `aria-live="polite"` to dynamic containers so screen readers announce changes.
