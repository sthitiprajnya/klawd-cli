## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions
**Learning:** Elements that have `overflow: auto` or `overflow-x: auto` (like `<pre>` blocks) can create scrollable regions. If these regions contain content that needs to be scrolled to be fully seen, they must be accessible via keyboard for users who cannot use a mouse. By default, they are not focusable.
**Action:** Always add `tabindex="0"` to scrollable containers and pair them with proper labeling (e.g., `aria-labelledby` referencing a visible title) and visible focus styles (`:focus-visible`) so keyboard and screen reader users can navigate and interact with them effectively.
