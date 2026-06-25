## 2026-06-16 - Tap-to-Copy for Critical Information
**Learning:** Using monospace formatting (backticks) in Telegram Markdown V1 enables "tap-to-copy" functionality in most mobile clients. This is extremely helpful for users who need to copy account numbers, phone numbers, or transaction IDs to other apps (like banking apps) without manual transcription.
**Action:** Always wrap financial details, account numbers, and phone numbers in backticks when using Markdown. Sanitize dynamic content with a helper like `clean_mono` to avoid breaking the block.
