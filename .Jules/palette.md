## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-05-24 - Semantic Structure and Keyboard Access for Scrollable Elements
**Learning:** Elements with scrollable regions (like <pre> tags with overflow: auto) trap content from keyboard users unless made explicitly focusable. Additionally, asynchronous lists like job queues need aria-live to announce changes.
**Action:** Always ensure overflow regions have tabindex="0" and aria-labelledby, use aria-live="polite" for dynamic lists, and structure the page with semantic HTML (<main>, <header>) for proper document outlines.
