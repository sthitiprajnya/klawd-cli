## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-21 - Accessible Dynamic & Scrollable Regions
**Learning:** Dynamically updating UI containers and scrollable code blocks go unnoticed or cannot be accessed by keyboard-only users and screen readers.
**Action:** Always add aria-live="polite" to async UI containers and ensure scrollable regions have tabindex="0" with appropriate aria-labelledby tags for full keyboard and screen reader accessibility. Also use semantic tags like <main> and <header> for better document structure.
