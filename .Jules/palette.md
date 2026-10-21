## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2026-07-06 - Dynamic Container Announcements
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (like the job, skills, and provenance lists) are visually obvious but often missed by screen readers when content is injected via fetch calls and websockets without a page reload.
**Action:** Always add `aria-live="polite"` to dynamically updating content containers so screen readers know to announce content updates automatically.
