## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-05-18 - Asynchronous Data Container Announcements
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (e.g., job lists, skill loading) are often missed by screen readers because the DOM changes happen without page reloads or focus changes, leaving visually impaired users unaware of updates.
**Action:** Always add the `aria-live="polite"` attribute to containers that receive asynchronous content updates so screen readers announce the changes naturally.
