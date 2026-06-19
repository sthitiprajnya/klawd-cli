## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-05-18 - Accessible Scrollable Code Blocks
**Learning:** Found a pattern where dynamically updating `<pre>` blocks with `overflow-x: auto` were inaccessible to keyboard users because they couldn't scroll them. Also, the dynamic updates lacked `aria-live`.
**Action:** When implementing scrollable containers (especially for dynamic logs/code), always ensure they have `tabindex="0"`, a clear `aria-labelledby`, and visible `:focus-visible` styles. Additionally, use `aria-live="polite"` for dynamic content wrappers.
