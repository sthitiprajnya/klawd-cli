## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2026-07-30 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (e.g., `overflow: auto` or `overflow-x: auto`) must be focusable to be accessible for keyboard users, as they otherwise cannot scroll the content using arrow keys.
**Action:** Always add `tabindex="0"` to scrollable regions and pair them with an accessible label (e.g., using `aria-labelledby`) to ensure keyboard accessibility and provide context for screen readers.
