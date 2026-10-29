## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-05-24 - Accessible Dynamic Containers
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (like job lists or skill data) remain silent to screen readers, causing visually impaired users to miss real-time updates.
**Action:** Always add aria-live="polite" to dynamic content containers to ensure screen readers announce asynchronous updates without interrupting the user.
