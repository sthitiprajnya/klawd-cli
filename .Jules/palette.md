## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-07-10 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` with `overflow-x: auto`) are inaccessible to keyboard users unless they can receive focus, preventing them from scrolling the content.
**Action:** Always make scrollable elements focusable using `tabindex="0"`, provide visible focus styles (like `:focus-visible`), and ensure proper ARIA labeling (e.g., `aria-labelledby`) for screen readers.
