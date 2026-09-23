## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-08-05 - Keyboard Accessibility for Scrollable Regions
**Learning:** Scrollable containers (like `<pre>` elements with `overflow: auto`) are not natively focusable, meaning keyboard-only users cannot scroll their contents to read overflowing text.
**Action:** Add `tabindex="0"` to scrollable regions and pair them with `aria-labelledby` linking to a visible heading so screen readers announce their purpose when focused.
