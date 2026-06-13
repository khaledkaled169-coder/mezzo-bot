## 2025-06-13 - Telegram Tap-to-Copy & Return Flow
**Learning:** Using monospace formatting (backticks) in Telegram bots for IDs and phone numbers creates an "invisible" UX win by enabling tap-to-copy functionality. Additionally, returning users should always bypass onboarding if their identity (phone/ID) is already known.
**Action:** Always wrap financial or identification details in monospace and check registration state in the `/start` handler to skip onboarding.
