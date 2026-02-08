# AI Development Workflow – 3 Amigos Model

This document describes a practical, repeatable workflow for building applications using a combination of:
- a human idea owner,
- architectural validation,
- and Claude Code (AI implementer).

The goal is to:
- avoid overengineering,
- respect real framework constraints,
- keep a clear and persistent trail of decisions,
- and use AI as a multiplier, not as a leader.

This workflow is intentionally decision-driven, not chat-driven.

---

## 1. Core Concept – 3 Amigos (Without GWT)

This workflow does not use Given/When/Then formalism.
Instead, it uses the 3 Amigos concept as a conversational and decision-making model.

The focus is on:
- shared understanding
- early clarification of constraints
- cutting wrong options early
- making decisions before writing code

---

## 2. Roles and Responsibilities

### Amigo 1 – Product / Owner (Human)

- Has the idea or the problem
- Knows why something is being built
- Provides domain knowledge and priorities
- Defines boundaries, non-goals, and expectations
- Owns trade-offs and makes final decisions

This role is the source of truth for intent and value.

---

### Amigo 2 – Architecture / Reality Check (ChatGPT)

- Does not write code
- Does not implement features
- Validates decisions, not lines of code
- Enforces constraints and long-term thinking
- Identifies:
  - hidden risks
  - framework limitations
  - future technical debt
  - wrong abstractions
- Explicitly cuts options and states what should NOT be done

This role focuses on directional correctness, not implementation details.

---

### Amigo 3 – Implementer (Claude Code)

- Writes code
- Refactors code
- Follows explicit instructions
- Works in compound mode (plan → work → review)
- Produces decision artifacts (PLAN / WORK / REVIEW)
- Does not make product or architectural decisions

Claude Code is treated as an executor, not an author.

---

## 3. Why Claude Code Should Not Lead Architecture

Even with compound engineering, Claude Code:
- gravitates toward generalized solutions
- favors abstraction and best practices
- proposes options instead of eliminating them
- optimizes for elegance over long-term maintainability
- lacks lived experience with technical debt

As a result:
- it is unreliable as an architect
- it is weak at defining boundaries
- it often suggests solutions that are technically correct but practically harmful

Claude Code excels at implementation, not judgment.

---

## 4. Claude Code Constraints (Must Be Explicit)

Claude must always operate under explicitly stated constraints.
If they are not written down, Claude will invent its own.

Typical constraints include:
- the framework has real limitations (e.g. Streamlit rerun model)
- no event-driven UI
- no fine-grained lifecycle control
- session_state must remain minimal
- expensive operations must be cached
- filesystem may be ephemeral
- no background jobs
- no “we’ll fix this later” assumptions

If constraints are not explicit, Claude will violate them.

---

## 5. Brainstorm Phase – Proper Use and Positioning

Claude Code supports a Brainstorm phase, which is useful but dangerous if misused.

### What Brainstorm IS
- a divergent thinking phase
- used to explore alternative approaches
- optimized for breadth, not correctness

### What Brainstorm IS NOT
- decision-making
- scope definition
- architecture ownership
- feature prioritization

### Correct Placement in the Workflow

1. Human idea / problem
2. Human + ChatGPT planning and constraints
3. Claude Brainstorm within fixed boundaries
4. ChatGPT cuts options and selects direction
5. Claude Planning (compound)
6. Claude Implementation and Review

Brainstorm is allowed only inside a clearly defined box.

### Brainstorm Rules for Claude
- stay within defined constraints
- do not expand scope
- do not introduce new features
- do not change architecture assumptions
- explicitly list trade-offs and risks

Brainstorm without human judgment is informational, never authoritative.

---

## 6. Role of Architectural Validation (ChatGPT)

Architectural validation does not mean code review.

ChatGPT:
- does not need repository access
- does not read diffs
- does not review individual lines of code

Instead, it validates:
- overall direction
- decisions that were made
- mental model behind the solution
- respect for constraints
- long-term maintainability risks

We validate HOW decisions are made, not WHAT code was written.

---

## 7. Decision Artifacts as the Source of Truth

Chat sessions are ephemeral.
Documents are persistent.

No critical context should live only inside a chat.

Claude Code must always produce:

PLAN.md  
- intent before coding  
- goal, constraints, proposed changes, out of scope  

WORK.md  
- what was actually done  
- deviations and open questions  

REVIEW.md  
- self-review  
- risks, anti-patterns, technical debt  

These artifacts enable architectural validation without code access.

---

## 8. Sessions vs Documents

Chat sessions may expire or reset.
Documents are the only reliable long-term memory.

Rules:
- never rely on chat alone
- always externalize decisions
- treat documents as canonical input

Canonical documents:
- AI_WORKFLOW.md – how work is done
- PROJECT_BRIEF.md – what is being built
- Feature briefs or decision logs – incremental reasoning

---

## 9. ChatGPT’s Role Across Sessions

ChatGPT is not long-term memory.
ChatGPT is an architectural reviewer and decision partner.

When provided with documents, ChatGPT can:
- reconstruct full context
- validate decisions
- detect risks
- suggest corrections

Continuity is document-based, not session-based.

---

## 9.1 ChatGPT as Documentation Producer

ChatGPT does not only review decisions.
ChatGPT actively helps create and maintain documentation.

ChatGPT may produce:
- Project Briefs
- Feature Briefs
- Decision Logs
- Architectural Notes
- Constraint Definitions
- Risk Assessments

These documents are:
- human-readable
- intentionally stable
- designed to survive across sessions
- treated as canonical project memory

ChatGPT continuity depends on documents, not sessions.

---

## 10. End-to-End Workflow Summary

1. Human has an idea or problem
2. Human + ChatGPT clarify problem, constraints, non-goals
3. Context is written into a Project or Feature Brief
4. Claude Brainstorms within boundaries
5. ChatGPT selects direction
6. Claude plans (compound)
7. Claude implements and reviews
8. Claude produces PLAN / WORK / REVIEW
9. ChatGPT validates decisions
10. Human decides: merge, adjust, rollback

Code is a derived artifact, never the source of truth.

---

## 11. Why This Workflow Works

- prevents premature coding
- prevents AI overengineering
- forces explicit decisions
- creates a persistent reasoning trail
- works across sessions
- scales from small tools to larger systems

AI is used as a tool, not an author.

---

## 12. Core Principle

Architecture is the sum of decisions made.
Code is only the current implementation of those decisions.

If decisions are sound, code can be fixed.
If decisions are wrong, code will always cause problems.

---

End of document.