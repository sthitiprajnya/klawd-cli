## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Dynamic Scrollable Containers
**Learning:** Elements with scrollable regions (e.g., `<pre>` blocks with `overflow: auto`) are not natively focusable by keyboard, making their content inaccessible to keyboard users unless they use a mouse. Furthermore, if these containers update dynamically via JavaScript, screen readers won't announce the new content automatically.
**Action:** Always add `tabindex="0"`, a visible focus style (`:focus-visible`), and proper ARIA labeling (`aria-labelledby`) to scrollable containers. Additionally, apply `aria-live="polite"` to containers that update asynchronously to ensure screen readers announce updates.
