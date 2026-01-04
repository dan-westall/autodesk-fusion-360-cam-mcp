# Task Management Guidelines

**Version:** 1.0  
**Last Updated:** January 4, 2026  
**Owner:** Development Team  
**Purpose:** Establish consistent practices for managing task lists in spec documents

## Overview

This steering file defines rules for managing task lists in specification documents to prevent breaking code references and maintain traceability between code and specs.

## Core Rules

### Never Modify Existing Task Numbers
- **NEVER** renumber existing tasks
- **NEVER** insert new tasks between existing task numbers
- **NEVER** change task IDs that may be referenced in code comments

### Always Add New Tasks at the Bottom
- **ALWAYS** add new tasks at the end of the task list
- **ALWAYS** use the next sequential number for new task groups
- **ALWAYS** use sub-task numbering (e.g., 14.1, 14.2) for related tasks within a group

## Rationale

Code often references task numbers in comments for traceability:
```python
# Setup-Toolpath Relationship Functions (Task 10.1)
# Bidirectional Relationship Helper Functions (Task 10.3)
```

Changing task numbers breaks these references and creates confusion about which task the code implements.

## Examples

### Correct: Adding New Tasks at Bottom
```markdown
- [x] 13. Final Checkpoint
  - Ensure all tests pass

- [ ] 14. New Feature Implementation (NEW)
  - 14.1: Research API
  - 14.2: Implement functions
  - 14.3: Add endpoints
```

### Incorrect: Inserting Tasks in Middle
```markdown
- [x] 1. API Research
- [ ] 1.4 New Research Task (WRONG - inserted in middle)
- [x] 2. Basic Infrastructure
- [ ] 2.0 New Setup Task (WRONG - inserted before 2.1)
```

## When Requirements Change

When new requirements are added to a spec:

1. **Keep existing tasks unchanged** - Don't modify completed or in-progress tasks
2. **Add new task group at bottom** - Use next available number (e.g., Task 14, 15, etc.)
3. **Reference new requirements** - Link new tasks to new requirement numbers
4. **Update Notes section** - Document which new tasks address which new requirements

## Task Numbering Convention

- **Major tasks**: Sequential integers (1, 2, 3, ... 14, 15)
- **Sub-tasks**: Decimal notation (14.1, 14.2, 14.3)
- **Optional tasks**: Marked with asterisk (14.5*)

## Change Log

- **v1.0** (January 4, 2026): Initial creation based on lesson learned from CAM setup management spec updates
