## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-21 - Accessible Scrollable Regions & Dynamic Content
**Learning:** Elements with scrollable content trap keyboard users unless explicitly focusable, and dynamic UI containers are ignored by screen readers without ARIA live regions.
**Action:** Always add tabindex="0" with aria-labelledby to scrollable containers, and use aria-live="polite" on dynamically updated elements.
