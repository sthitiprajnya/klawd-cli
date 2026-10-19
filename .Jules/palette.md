## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Aria-live on Async Containers
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (e.g., job lists, skill loading) without `aria-live` attributes are effectively invisible to screen readers when content changes, creating an accessibility barrier.
**Action:** Always include the `aria-live="polite"` attribute on dynamic containers (like `job-list` or `skills-container`) to ensure screen readers announce content updates to visually impaired users without interrupting their current task.
