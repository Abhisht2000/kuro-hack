# Auto Counter & Mouse Mover

A small desktop utility that increments a counter forever and can move the mouse vertically until you press **Stop**.

## Run it

```bash
python3 -m pip install -r requirements.txt
python3 autocounter.py
```

On macOS, grant your terminal or Python app **Accessibility** access in **System Settings → Privacy & Security → Accessibility** so it can move the cursor.

For safety, PyAutoGUI's failsafe is enabled: moving the cursor into any screen corner stops the automation.
