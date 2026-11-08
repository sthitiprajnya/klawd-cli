## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-08 - Accessible Dynamic Containers
**Learning:** The dashboard uses asynchronous JS fetching and WebSocket streams to constantly update UI containers (jobs, skills, provenance), but these updates were invisible to screen readers without ARIA live regions.
**Action:** Always add `aria-live="polite"` to dynamic data containers in this design system so screen reader users are notified of real-time updates.
