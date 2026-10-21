## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-05-14 - Scrollable Region Accessibility
**Learning:** Elements with scrollable regions (e.g. `pre` tags with `overflow-x: auto`) are not accessible to keyboard users by default, preventing them from scrolling to read the full code context.
**Action:** Always add `tabindex="0"`, a visible `:focus-visible` outline, and proper ARIA labels (`aria-labelledby`) to any element that may overflow to ensure full keyboard navigation support.
