# The task (same words for both runs)

In invoice.py, add a 10% discount for orders whose total before VAT is over 500 pounds.
The discount applies before VAT. Add tests for it, and run python3 -m unittest until it passes.

## Run 1: one loop (from the first copy)
```
claude -p "In invoice.py, add a 10% discount for orders whose total before VAT is over 500 pounds. The discount applies before VAT. Add tests for it, and run python3 -m unittest until it passes. Do not use sub-agents." --permission-mode acceptEdits --allowedTools "Bash(python3:*)" --output-format json > ~/one-loop.json
```

## Run 2: one loop plus one reviewer (from the second copy)
```
claude -p "In invoice.py, add a 10% discount for orders whose total before VAT is over 500 pounds. The discount applies before VAT. Add tests for it, and run python3 -m unittest until it passes. When the tests pass, send the change to the aios-agents:code-reviewer agent with a brief that names the files and what the change must do, then fix any real finding and run the tests again." --permission-mode acceptEdits --allowedTools "Bash(python3:*)" Agent --output-format json > ~/with-reviewer.json
```

## Compare
```
aios-agent compare ~/one-loop.json ~/with-reviewer.json
```

Then write one line: what did the reviewer find that the first run missed? If the answer
is "nothing", the reviewer did not earn its place for a change this size.
