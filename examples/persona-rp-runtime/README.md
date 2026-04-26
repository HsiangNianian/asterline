# persona-rp-runtime

Persona roleplay example for Asterline.

This example shows:

- an explicit AI persona system for group-style chat
- passive dialogue memory plus active persona switching
- fictional voiceplay without hiding that replies are AI-generated

## Run

```bash
uv run --package persona-rp-runtime python -m asterline --config examples/persona-rp-runtime/config.terminal.toml
```

## Try

- `/personas`
- `/persona noir-detective`
- `/say describe this rainy city`
- `ai answer like the current persona`
