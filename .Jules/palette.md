## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-21 - Accessible Dynamic Content
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (like job queues) are not announced by screen readers by default.
**Action:** Always add the aria-live="polite" attribute to dynamic containers and prefer semantic HTML tags like main and header over generic div wrappers to improve document structure.
