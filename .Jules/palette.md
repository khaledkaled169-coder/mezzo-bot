## 2026-07-16 - Tap-to-Copy Formatting for Telegram Payment Instructions
**Learning:** Formatting critical transaction parameters (deposit amounts, bank account numbers, phone numbers) using inline monospace code blocks (`account`) in Telegram bot messages allows users to tap on the value to instantly copy it to their clipboard, reducing human transfer errors.
**Action:** When displaying payment, deposit, or account details in Telegram bot interfaces, wrap phone numbers, account numbers, and exact deposit amounts in backticks and pass `parse_mode="Markdown"`.
