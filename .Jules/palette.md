## 2026-06-16 - Improving Interaction Efficiency with Monospace Formatting
**Learning:** Monospaced text in Telegram bot messages provides a "tap-to-copy" functionality on both mobile and desktop. This significantly reduces user friction when handling banking details, account numbers, and transaction IDs, as it eliminates the need for manual selection.
**Action:** Always use monospaced formatting (backticks) for sensitive or actionable data like account numbers, phone numbers, and IDs in Telegram-based interfaces.

## 2026-06-16 - Safety with Markdown Parse Mode
**Learning:** Using `parse_mode="Markdown"` requires careful handling of special characters (like `*`, `_`, `[`, `` ` ``) in dynamic user data to prevent API errors. While simple for numeric data, it can be risky for general text.
**Action:** When using Markdown parse mode with user-provided or dynamic strings, ensure these strings are escaped or validated to prevent bot crashes.
