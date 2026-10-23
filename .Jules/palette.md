## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-03-24 - Missing ARIA Live Regions for Async Polling
**Learning:** The dashboard components (job lists, skill trees) rely heavily on background async updates (WebSocket and setInterval polling), but lack aria-live attributes, meaning screen reader users are unaware of updates.
**Action:** Always add aria-live="polite" to dynamic data containers that are populated via background JS fetches to ensure screen readers announce updates.
