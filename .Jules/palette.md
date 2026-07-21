## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like overflow-x: auto on pre tags) are not accessible to keyboard users unless they can receive focus. Without focus, users navigating via keyboard cannot scroll the content.
**Action:** Always add tabindex="0" and an appropriate aria-labelledby or aria-label to scrollable containers to ensure keyboard accessibility.
