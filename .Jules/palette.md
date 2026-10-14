## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Accessible Dynamic Containers
**Learning:** When dynamically updating UI containers with asynchronous data (like job lists or skills context via JavaScript), screen readers may fail to announce the new content to visually impaired users, leading to a confusing experience.
**Action:** Always add the `aria-live="polite"` attribute to dynamically populated containers to ensure screen readers gracefully announce content updates without interrupting the user's current flow.
