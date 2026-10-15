## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Dynamic Container Screen Reader Accessibility
**Learning:** Dynamic UI containers that are updated asynchronously via JavaScript (like loading states for jobs or skills) must notify screen readers when their content changes, otherwise visually impaired users won't know the update occurred.
**Action:** Always include the `aria-live="polite"` attribute on asynchronous data containers (like `job-list` or `pre` blocks) to ensure screen readers announce content updates gracefully.
