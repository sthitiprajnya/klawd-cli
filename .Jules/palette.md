## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-10-08 - Accessible Dynamic UI Containers
**Learning:** Dynamic UI containers updated asynchronously via JavaScript (e.g., job lists, skill loading) must include the `aria-live="polite"` attribute to ensure screen readers announce content updates to visually impaired users.
**Action:** Always add `aria-live="polite"` to containers whose contents are fetched and updated dynamically, such as `#jobs-container`, `#skills-container`, and `#provenance-container`.
