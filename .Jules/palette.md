## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (like pre blocks with overflow-x: auto) are inaccessible to keyboard users unless they have tabindex="0" and an aria-labelledby attribute. Additionally, dynamic UI containers updated via JavaScript need aria-live="polite" for screen readers.
**Action:** Always ensure scrollable regions are focusable and correctly labeled, and add aria-live to asynchronously updated containers.
