## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Dynamic Containers
**Learning:** Screen readers do not automatically announce when content within a container changes dynamically via JavaScript, which makes async updates invisible to visually impaired users.
**Action:** Always add `aria-live="polite"` to dynamically updating UI containers (like job lists or data panels) to ensure screen readers announce the new content to users.
