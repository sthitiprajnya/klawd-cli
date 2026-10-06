## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Dynamic UI Containers Accessibility
**Learning:** The application updates data dynamically via WebSocket and REST, causing screen readers to miss updates in empty containers.
**Action:** Add the aria-live="polite" attribute to dynamic containers to ensure screen readers announce updates to visually impaired users.
