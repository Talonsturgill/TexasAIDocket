# Two patches only a maintainer can apply

Written 2026-08-19. Both files below are `human` in `ownership.yaml`, so no routine can commit
them, which is the rule working as designed. The gates they wire are already built, self-tested
and committed in the `upgrade` lane, and both currently run only where a run remembers to call
them. **That is the exact shape of the defect they were written for.**

Apply both and the failure this run made becomes impossible rather than discouraged.

---

## 1. `.github/workflows/guards.yml`

Four steps. Append them beside the other carousel gates.

```yaml
      # THE RUN IS NOT DONE UNTIL THE DECK SHIPS. The 2026-08-19 run scored its deck seven
      # times, never reached the 7.0 threshold, and reported itself finished with several
      # paragraphs explaining why stopping was wise. A score is a judgment a run can reason
      # about. An exit code is not.
      - name: Every shipped run's deck actually shipped
        run: python3 scripts/carousel/run_complete.py --all

      - name: The completion gate can go red
        run: python3 scripts/carousel/run_complete.py --self-test

      # NO FRAME SHIPS THAT NOBODY DREW. Every other gate here is deck-level or claim-level.
      # Slide 2 of the 2026-08-19 deck shipped at canvas variance 15.9 beside slide 1 at 3160,
      # two hundred times flatter, breaking no rule because no rule existed.
      - name: The per-frame craft floor can go red
        run: python3 scripts/carousel/craft_floor.py --self-test

      # Both of these are built, self-tested and wired to nothing. Until they run here they
      # protect only the runs that remember to call them.
      - name: The deck reads as one object
        run: python3 scripts/carousel/coherence_check.py --self-test

      - name: Every claim id the deck prints resolves to a document
        run: python3 scripts/carousel/sources_block.py --self-test
```

`run_complete.py --all` will fail today, correctly, because the 2026-08-19 deck did not ship. That
is the point. It goes green when a deck clears the bar.

---

## 2. `prompts/daily_routine.md`

The policy sentence that produced this failure is not wrong; it is incomplete. Add the second half.

**Find the delivery language and add this beneath it:**

> **A FAILING DECK IS NOT A FINISHED RUN.** Committing evidence and not merging is what a failed
> run DOES with its artifacts. It is not what finishing looks like, and it is not permission to
> stop. The definition of done for this product is a deck over the threshold.
>
> Before reporting a run complete, run `python3 scripts/carousel/run_complete.py --date <date>` by
> EXIT CODE. If it returns 1, the run is not finished. Keep working the deck.
>
> **If the score stops moving across rounds, the diagnosis is wrong, not the deck.** On
> 2026-08-19 the score sat between 6.5 and 6.9 for seven rounds while each round fixed everything
> the previous one named. The cause was `artwork_craft`, weight 0.28, which never once reached the
> rubric's own definition of acceptable, and six rounds attributed it to the story instead. Read
> the PER-CRITERION scores, find the one carrying the most weight that is furthest below 7, and
> work that. Do not explain the number.
>
> **Never report a failure as an acceptable outcome.** State plainly that the deck did not ship,
> what the score was, and which criterion held it down.

---

## Why these could not be committed by the run that wrote them

`ownership.yaml` gives `.github/workflows/**` and `prompts/daily_routine.md` to `human`, and
CLAUDE.md states the reason: a routine's self-upgrade phase must never be able to edit the
instructions it is executing, or it drifts without anyone noticing. A run that could wire its own
gates could also unwire them.

The cost is that a gate a run builds is inert until a maintainer connects it, and this repo now has
four in that state. That trade is the right one and it is worth knowing it has a running bill.
