## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-10-17 - Accessible Dynamic Data Containers
**Learning:** The dashboard dynamically populates data (jobs, skills, provenance) via JavaScript async fetch operations. Without proper ARIA attributes, screen readers are unaware of these critical updates, leading to an inaccessible experience for visually impaired users.
**Action:** Always add the `aria-live="polite"` attribute to UI containers that are asynchronously updated with content so screen readers can announce changes seamlessly without interrupting the user.
