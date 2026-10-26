## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Dynamic Updates
**Learning:** When content is updated asynchronously via JavaScript (like live job lists or loaded skills), screen readers won't announce the new content to visually impaired users by default, leaving them unaware of state changes.
**Action:** Always add the `aria-live="polite"` attribute to dynamic UI containers so screen readers are notified to announce the updates smoothly without interrupting the user.
