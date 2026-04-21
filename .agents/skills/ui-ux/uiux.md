# AGENTS.md

## Project goal
This project is being refactored from a generic PDF Q&A interface into a dual-mode product:
- Study Mode
- Academic Mode

The goal is to improve UI/UX and feature organization without rewriting the backend.

## UI stack rules
- Use shadcn/ui as the default UI component system.
- Prefer reusable components over raw page-level custom markup.
- Prefer accessible, composable primitives.
- Keep styling consistent with Tailwind utility patterns already used in the app.
- Avoid creating one-off custom buttons, cards, tabs, dialogs, and inputs unless necessary.

## Design direction
- The app must feel modern, clean, and product-structured.
- Do not keep all features in one undifferentiated workspace.
- Split the product into two top-level modes:
  - Study Mode
  - Academic Mode

## Product behavior rules
### Study Mode
Optimize for:
- speed
- focus
- lightweight interaction
- flashcards
- quiz/test generation
- quick Q&A

### Academic Mode
Optimize for:
- trust
- structure
- evidence visibility
- literature review workflows
- argument building
- document-grounded outputs

## UX rules
- Use explicit action labels, not abstract labels.
- Every major screen should have one obvious primary action.
- Empty states must teach the user what to do next.
- Reduce cognitive overload by guiding the user through:
  1. select/upload documents
  2. choose task
  3. generate output
  4. inspect evidence/citations when relevant

## Component rules
Create and reuse components such as:
- mode switcher
- document sidebar
- task cards
- prompt composer
- output viewer
- evidence panel
- flashcard viewer
- quiz player
- empty state panel

## Refactor strategy
- Refactor incrementally.
- Reuse existing backend flows where possible.
- Prefer improving structure and UI clarity over rebuilding working logic.
- Keep current features functional while reorganizing screens.

## Implementation preference
When proposing or building new UI sections, prefer shadcn/ui-compatible patterns and structured component layouts over ad hoc page markup.