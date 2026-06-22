## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-06-22 - Accessible Dynamic and Scrollable Content
**Learning:** Elements with scrollable regions (`overflow-x: auto`) cannot be reached via keyboard by default, leaving their content inaccessible if horizontal scrolling is required. Additionally, dynamically updated UI containers fail to alert screen readers when new content arrives.
**Action:** Always make scrollable elements focusable using `tabindex="0"`, provide visible `:focus-visible` styles, and associate them with descriptive headings using `aria-labelledby`. Ensure dynamic containers (like async job lists) use `aria-live="polite"` so updates are announced properly without disrupting the user.
