## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-10-10 - Accessible Dynamic Containers
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (e.g., job lists, skill loading) lack accessibility context for screen readers.
**Action:** Always add `aria-live="polite"` to container elements that are asynchronously populated via JS fetch or WebSockets.
