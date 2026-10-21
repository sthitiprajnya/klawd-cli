## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Semantic HTML and Dynamic Updates
**Learning:** Dynamic containers updated asynchronously without aria-live are silent to screen readers, and scrollable regions without tabindex="0" and aria-labelledby are inaccessible via keyboard.
**Action:** Always use aria-live="polite" on dynamic containers and add tabindex="0" with proper ARIA labeling to elements with overflow: auto to ensure they are focusable and readable.
