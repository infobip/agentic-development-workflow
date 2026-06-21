# PATTERNS.md

<!-- Human-curated corrections for the autonomous loop.

     Who writes this?
     You do!

     When do you add an entry?
     When you notice (in ACTIVITY.md, in commits, or in the working tree) that
     fresh agent sessions keep making the same mistake, repeating an
     antipattern, or drifting from project intent.

     What goes here?
     One-line corrections, each tied to a real observed failure. Specific and
     actionable beats general advice. The agent reads this file at the start of
     every iteration and treats entries as binding.

     Examples:
       - "Do not create new utility files. Extend existing helpers in
          src/utils/."
       - "The test database is SQLite. Don't use Postgres-specific syntax."
       - "Always check for an existing migration before generating a new one."
       - "Never call the external billing API in tests; use the recorded
          fixtures in tests/fixtures/billing/."

     Keep entries terse. Every token here is loaded into every session. -->

<!-- Add one bullet per observed failure. Delete a bullet once it's no longer
     needed (e.g., the code or convention changed and the correction is moot). -->

-
