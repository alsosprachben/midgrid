# MidGrid Example Pack Exporter

`midgrid_examples.py` exports recorded training examples as compact few-shot material for LLM composition contexts.

The intent is example learning, not rule accumulation. Rules and evaluator codes are labels that make an example intelligible; the primary learning unit is:

```text
exercise prompt -> flawed or incomplete attempt -> diagnosis -> corrected MidGrid -> lesson
```

## Commands

```bash
python3 midgrid_examples.py
python3 midgrid_examples.py --skill species-counterpoint
python3 midgrid_examples.py --species second --format markdown
python3 midgrid_examples.py --exercise-id parallel-perfect-repair-001 --format json
python3 midgrid_examples.py --target-exercise-id first-species-below-001 --format markdown
python3 midgrid_examples.py --target-exercise-id second-species-above-001 --output /tmp/second_species_prompt.md
```

## Filters

- `--skill`: include examples whose exercise has this skill, such as `species-counterpoint`.
- `--species`: include examples for one species, such as `first` or `second`.
- `--exercise-id`: include one recorded exercise as an example.
- `--target-exercise-id`: append an unsolved target exercise after the examples; the target's own recorded solution is excluded by default.
- `--include-target-example`: include the target's recorded solution when intentionally building a review or imitation pack.
- `--exclude-exercise-id`: remove a recorded exercise from the examples; may be repeated.
- `--limit`: emit at most this many examples.
- `--max-lines`: clip each attempt/correction to this many MidGrid lines; use `0` or a negative value to keep full text.
- `--output`: write the rendered pack to a file instead of stdout.

## Markdown Output

Markdown output is meant to paste directly into a model context. Each example contains:

- exercise metadata,
- objective and prompt,
- attempt issue codes,
- a short diagnosis excerpt,
- attempted MidGrid,
- corrected MidGrid,
- corrected result summary,
- distilled lesson.

## JSON Output

JSON output uses schema `midgrid.example_pack.v1`:

```json
{
  "schema": "midgrid.example_pack.v1",
  "examples": [
    {
      "exercise_id": "second-species-above-001",
      "skill": "species-counterpoint",
      "species": "second",
      "lesson": "...",
      "attempt_issue_counts": {"exercise_unfilled_voice": 15},
      "attempt_midgrid": "...",
      "corrected_midgrid": "..."
    }
  ],
  "target_exercise": {
    "exercise_id": "first-species-below-001",
    "seed_midgrid": "..."
  }
}
```

## Recommended Use

Before asking a model to solve a new exercise, export a practice prompt near the task:

```bash
python3 midgrid_examples.py --target-exercise-id second-species-above-001 --format markdown
```

Put the generated pack before the model. The model should imitate the examples first, solve the target second, then use the evaluator and exercise checks as feedback.


## Practice Prompts

Use `--target-exercise-id` to append an unsolved target exercise after the examples:

```bash
python3 midgrid_examples.py --target-exercise-id first-species-below-001 --format markdown
```

By default, the target exercise's own recorded solution is excluded. This keeps the pack useful for practice: the model sees nearby worked examples, then the target seed, success criteria, and evaluator command.

Use `--include-target-example` only when you intentionally want to show the target's prior solution, such as for review or style imitation rather than testing.

Use `--exclude-exercise-id EXERCISE_ID` to remove additional recorded examples from the pack.
