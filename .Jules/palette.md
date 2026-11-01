## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Asynchronous Dynamic UI Updates Accessibility
**Learning:** Dynamic UI containers in this app (like the job list and system intelligence) are updated asynchronously via JavaScript, which hides the new content from screen readers.
**Action:** Add `aria-live="polite"` to dynamic containers so screen readers announce content updates smoothly without interrupting the user.
