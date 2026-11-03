## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Asynchronous Content Announcements
**Learning:** The application heavily relies on asynchronous updates to populate its primary containers. These updates are visually rendered but completely silent to screen readers without ARIA live regions.
**Action:** All dynamic data containers (like `jobs-container`, `skills-container`, and `provenance-container`) must include `aria-live="polite"` by default to ensure visually impaired users are notified of real-time state changes.
