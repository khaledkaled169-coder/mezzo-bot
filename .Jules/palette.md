## 2026-07-16 - Onboarding Command State Routing
**Learning:** Re-triggering the initial contact-sharing onboarding prompt when a fully registered user clicks or types `/start` creates unnecessary friction and confuses returning users who expect immediate access to their menu or account features.
**Action:** Always check existing registration and account state in `/start` handlers to seamlessly route fully registered users directly to main navigation and partially registered users to their next required step.
