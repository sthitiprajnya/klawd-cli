## 2026-05-25 - Provide Context for Visually Truncated Text
**Learning:** Visually truncating text with ellipses (e.g., in task lists) makes the UI look cleaner, but blindly truncating without providing a way to read the full text creates a poor user experience and accessibility issue.
**Action:** Always pair visual text truncation with an accessible `title` attribute or tooltip containing the full text, ensuring that users can access the complete information on hover or focus.
