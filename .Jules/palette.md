## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-03-24 - Keyboard Accessibility of Scrollable Code Blocks
**Learning:** In this application, raw data is often displayed using <pre> blocks with overflow-x: auto. These scrollable regions are inaccessible to keyboard users because <pre> tags are not natively focusable.
**Action:** Always add tabindex="0" and an aria-labelledby attribute (pointing to the nearest heading) to any scrollable <pre> elements in the dashboard to ensure keyboard users can scroll the content and screen readers can identify it.
