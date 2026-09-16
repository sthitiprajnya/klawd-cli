## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-09-16 - Dynamic Content Accessibility
**Learning:** Dynamic UI containers updated asynchronously via JavaScript fail to announce content updates to screen reader users if missing ARIA live regions.
**Action:** Always add aria-live="polite" to dynamic containers (like job lists or skill loading areas) so that screen readers announce content changes when they occur.
