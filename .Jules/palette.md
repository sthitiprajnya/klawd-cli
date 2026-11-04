## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2026-11-04 - Accessible Dynamic Content Updates
**Learning:** When dynamic content updates asynchronously via JavaScript (e.g., job lists, skill loading), screen readers will not announce the updates to visually impaired users unless explicitly instructed, leaving them unaware of the changed content state.
**Action:** Always add the `aria-live="polite"` attribute to dynamic UI containers that receive asynchronous updates. This ensures screen readers announce the new content gracefully without interrupting the user's current actions.
