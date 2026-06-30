## 2026-06-16 - [Tap-to-Copy for Payments]
**Learning:** Telegram users on mobile benefit significantly from "tap-to-copy" functionality for long numeric strings like bank account numbers or payment amounts. Monospace formatting (backticks) in Markdown V1/V2 enables this native feature.
**Action:** Always wrap account numbers, phone numbers, and exact financial amounts in backticks and ensure `parse_mode="Markdown"` is set.

## 2026-06-16 - [Markdown Safety with Dynamic Data]
**Learning:** Telegram Markdown V1 parsing fails if dynamic user data contains special characters like underscores or asterisks. Monospace blocks also render backslashes literally, making standard escaping unsuitable.
**Action:** Use a dedicated `esc()` helper for standard text and a `clean_mono()` helper (which removes internal backticks) for data inside monospace blocks.
