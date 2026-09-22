## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Scrollable regions with overflow-x are inaccessible to keyboard users unless explicitly made focusable, and asynchronously updated UI containers need aria-live attributes to be announced by screen readers.
**Action:** Added tabindex="0" and aria-labelledby to scrollable pre regions, and aria-live="polite" to dynamically updated containers.
