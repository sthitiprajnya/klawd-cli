## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-06-16 - Focusable Scroll Regions and Dynamic Announcements
**Learning:** Elements with scrollable regions (like `overflow: auto` or `overflow-x: auto`) must be focusable using `tabindex="0"` with clear focus styles (e.g. `:focus-visible`) and proper ARIA labeling (e.g. `aria-labelledby`) so keyboard users can navigate and scroll them. Also, dynamic UI containers updated asynchronously via JS must use `aria-live` attributes (like `aria-live="polite"`) to ensure screen readers announce the updates.
**Action:** When adding scrollbars (`overflow`) to content, always make the container keyboard-focusable. When dynamically injecting content into the DOM via fetch calls, use `aria-live` on the container to announce the changes to assistive tech.
