## 2026-07-16 - Tap-to-Copy Monospace Formatting for Payment Details
**Learning:** In messaging interfaces like Telegram, wrapping financial inputs (account numbers, deposit amounts) in monospace backticks (`0910534013`) enables single-tap copying on mobile devices, reducing user error and friction during bank/mobile transfers.
**Action:** Always wrap payment details, transaction IDs, and clean numeric amounts in backticks and pass `parse_mode="Markdown"` when presenting payment or transfer instructions.
