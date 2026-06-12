## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-06-12 - Aria-Live for Asynchronous Dynamic Containers
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (like the job lists, skill loading, and provenance containers) must inform screen readers about content updates. If not, screen reader users might not know when background data has loaded.
**Action:** Always use `aria-live="polite"` on containers whose content is updated dynamically so that assistive technologies announce the new content to users politely without interrupting their current tasks.
