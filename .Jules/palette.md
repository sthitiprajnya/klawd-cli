## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2026-07-27 - Semantic HTML and Accessible Scrollable Regions
**Learning:** Generic <div> elements and non-focusable scrollable regions (like <pre> with overflow: auto) hide document structure and prevent keyboard users from accessing hidden content. Additionally, dynamic updates without aria-live attributes are ignored by screen readers.
**Action:** Prefer semantic tags (<main>, <header>, <section>), ensure scrollable regions use tabindex="0" with aria-labelledby for focusability and context, and apply aria-live="polite" to dynamically updated containers so assistive technologies announce updates.
