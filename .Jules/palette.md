# Palette's Journal - Mezzo Bot UX Learnings

## 2025-05-14 - Tap-to-Copy for Financial Details
**Learning:** In Telegram bot interfaces, users frequently need to copy account numbers, phone numbers, or specific amounts for manual bank transfers or mobile payments. Using monospace formatting (backticks) makes these fields "tap-to-copy," significantly reducing friction and potential errors.
**Action:** Always wrap financial identifiers and amounts in backticks (`` ` ``) and ensure `parse_mode="Markdown"` or `parse_mode="HTML"` is enabled in the response.

## 2025-05-14 - Context-Aware Onboarding Bypass
**Learning:** For bots with multi-step registration (e.g., phone number then service ID), returning users who trigger `/start` shouldn't be forced to restart the entire flow. Checking the database for existing registration state allows for "resuming" or skipping onboarding.
**Action:** In `/start` handlers, check the database for existing user records and redirect them to their specific pending step or the main menu accordingly.
