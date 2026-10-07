## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Accessible Dynamic Content Updates
**Learning:** When UI containers (like job queues or skill lists) are updated asynchronously via JavaScript or WebSockets, screen readers will not announce the new content by default, leaving visually impaired users unaware of status changes.
**Action:** Always add the `aria-live="polite"` attribute to dynamic containers that update asynchronously to ensure screen readers announce the changes without interrupting the user.
