## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-21 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (e.g., `<pre>` blocks with `overflow-x: auto`) are inaccessible to keyboard-only users because they cannot be focused to scroll using arrow keys. Additionally, dynamically updated containers fail to notify screen readers of content changes.
**Action:** Always add `tabindex="0"` and an appropriate `aria-labelledby` attribute to scrollable regions to ensure keyboard accessibility and context for screen readers. Use `aria-live="polite"` on dynamically updated containers (like job lists or skill logs) so screen readers announce changes.
