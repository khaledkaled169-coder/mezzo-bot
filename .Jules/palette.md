# Palette's Journal - Mezzo Bot UX Enhancements

## 2026-06-16 - Tap-to-Copy Implementation
**Learning:** Monospace formatting in Telegram (backticks) enables 'tap-to-copy' functionality, which is critical for financial apps where users need to copy account numbers, phone numbers, and amounts exactly.
**Action:** Use `clean_mono()` to sanitize dynamic data inside backticks and `esc()` for Markdown V1 safety elsewhere.

## 2026-06-16 - Handling Falsy Values in Python Helpers
**Learning:** In Python, `if not text:` will evaluate to true for numeric `0`, which can lead to bugs in UX helpers (e.g., returning an empty string instead of "0").
**Action:** Always use explicit `is None` checks when a value can be a number to ensure "0" is correctly processed and displayed in the UI.
