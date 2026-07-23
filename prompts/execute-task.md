# CHAWKIDAAR TASK EXECUTION PROMPT TEMPLATE

You are operating under the Chawkidaar Autonomous Engineering Platform.

==================================================
TASK ASSIGNMENT
==================================================

Task ID: [TASK_ID]
Task Title: [TASK_TITLE]

Read and review:
- Epic: [EPIC_NAME_OR_NUMBER]
- Feature: [FEATURE_NAME_OR_NUMBER]
- Task: [TASK_ID]
- Relevant ADRs in docs/adr/

==================================================
OBJECTIVE
==================================================

Complete ONLY Task [TASK_ID].
Do NOT implement future tasks or unrequested scope.

==================================================
REQUIREMENTS
==================================================

1. Follow repository architecture strictly.
2. Produce clean, typed, maintainable code.
3. Write unit tests covering valid, invalid, and edge cases.
4. Verify formatting (`ruff`) and test passing (`pytest`).
5. Document architectural decisions in `docs/adr/` if new decisions are made.

==================================================
STOP CONDITION
==================================================

Upon completing Task [TASK_ID], STOP execution and submit task deliverables for Architect Review.
