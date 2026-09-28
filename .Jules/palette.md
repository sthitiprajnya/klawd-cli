## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-09-28 - Screen Reader Support for Async Updates
**Learning:** Dynamic UI containers in this app (like job lists and skills) are updated asynchronously via JavaScript, which leaves screen reader users unaware of real-time status changes and data loading unless explicitly announced.
**Action:** Always include the `aria-live="polite"` attribute on containers that receive asynchronous content updates to ensure screen readers announce the changes smoothly to visually impaired users without interrupting their current tasks.
