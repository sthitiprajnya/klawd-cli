## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2026-09-02 - Keyboard Accessible Scrollable Regions
**Learning:** Elements with scrollable content like pre blocks with overflow-x are inaccessible to keyboard users unless explicitly made focusable.
**Action:** Always apply tabindex="0" to scrollable containers and pair them with an accessible name via aria-labelledby to ensure they can be reached and scrolled via keyboard.
