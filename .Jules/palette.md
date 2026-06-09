## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-06-09 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (like `<pre>` blocks with `overflow-x: auto` used for code or JSON formatting) are completely inaccessible to keyboard users because they cannot be scrolled without a mouse if they are not focusable.
**Action:** Always add `tabindex="0"` to make scrollable containers focusable, ensure they have proper ARIA labeling (like `aria-labelledby`) to announce their purpose, and add `:focus-visible` styles so keyboard users know when they have focused the element and can use arrow keys to scroll.
