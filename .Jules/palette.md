## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-09-20 - Accessible Dynamic Content Updates
**Learning:** Dynamic UI containers updated asynchronously via JavaScript are often invisible to screen readers, leaving visually impaired users unaware of status changes.
**Action:** Always use aria-live="polite" on containers that receive asynchronous updates to ensure screen readers properly announce content changes.
