## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Dynamic Container Accessibility
**Learning:** This app heavily relies on asynchronous data fetching to populate UI containers like job queues and skills after the initial page load. Screen readers will ignore these updates silently if the containers are not properly annotated.
**Action:** Always add `aria-live="polite"` to dynamic UI containers (e.g., `#jobs-container`, `#skills-container`) to ensure content updates are announced to visually impaired users.
