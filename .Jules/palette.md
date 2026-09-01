## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like <pre> blocks with overflow-x: auto) are inaccessible to keyboard-only users because they cannot scroll the content if the element isn't focusable.
**Action:** Always make scrollable regions focusable by adding tabindex="0", ensure they have native browser focus outlines, and provide proper ARIA labeling via aria-labelledby linking to their heading.
