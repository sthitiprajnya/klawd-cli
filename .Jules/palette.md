## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-05-24 - Accessible Scrollable Regions and Dynamic Containers
**Learning:** Scrollable regions must have tabindex="0" and aria-labelledby for keyboard accessibility. Dynamic containers need aria-live="polite" for screen readers.
**Action:** Use these attributes natively for better UX and a11y.
