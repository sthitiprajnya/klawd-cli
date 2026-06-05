## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-06-05 - [Accessibility] Screen reader and Keyboard support for Dashboard Containers
**Learning:** The dashboard has dynamically loaded containers for 'Active Job Queue' and 'System Intelligence'. The text within `<pre>` elements requires horizontal scrolling, making it inaccessible for keyboard users without a focus indicator. Also, without `aria-live="polite"`, updates to jobs and skills won't be announced properly to screen readers.
**Action:** Always add `tabindex="0"` and an explicit `:focus-visible` outline for interactive/scrollable containers (e.g., `<pre>` with `overflow-x: auto`). Also ensure containers holding dynamic text (e.g., jobs list or skills payload) utilize `aria-live="polite"` and are explicitly labeled using `aria-labelledby` linked to their headings to guarantee screen readers announce updates efficiently.
