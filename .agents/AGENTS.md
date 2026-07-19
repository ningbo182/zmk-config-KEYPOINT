# ZMK Trackpoint and Layer Tuning Rules

When working on pointer sensitivity, scrolling speeds, or layer timeouts in this repository, always adhere to the following principles:

## 1. Trackpoint Sensitivity and Effort (TP_SCURVE_MID)
* The s-curve acceleration midpoint `TP_SCURVE_MID` in `trackpoint_0x15.c` controls physical effort. 
* Shifting `TP_SCURVE_MID` to a lower value (e.g. `9.0f` instead of the default `25.0f`) makes exponential acceleration trigger under lighter pressure, reducing finger strain.

## 2. Scroll Divisor Scaling
* The trackpoint reports at a high frequency (around 100Hz). 
* Do not use small divisors (like `10` or less) for both slow and fast scroll speeds simultaneously. Since scroll event tick counts are proportional to coordinate deltas, small divisors will cause scrolling to accelerate uncontrollably fast.
* To achieve a steady, linear scroll speed, keep both divisors equal to a larger constant value (e.g., `50`).

## 3. Scroll Deadzone and Lossless Accumulation
* Regular pointer movement has no deadzone, allowing light touches to accumulate losslessly and move the cursor smoothly.
* For scrolling to feel similarly smooth and responsive (rather than "stuttery" or like pushing a heavy box), keep `CONFIG_TRACKPOINT_SCROLL_DEADZONE` set to `0`. This allows tiny inputs (`1` or `2` raw delta) to be accumulated losslessly into the scroll residue buffer.

## 4. Temporary Layer Exclusions and Layer-Taps
* ZMK's `zip_temp_layer` automatically deactivates the mouse layer upon keypress unless the pressed key's position is listed in `excluded-positions`.
* **Click keys**: Mouse buttons (like left, right, or middle click) must remain in the `excluded-positions` list to prevent the layer from deactivating under the user's finger mid-hold or during rapid clicks.
* **Dual-role keys**: If a key needs to act as a layer-tap (e.g., Left Space holding to switch to `NAVIGATION` and tapping to send `SPACE`) while the mouse layer is active, it must **not** be in the `excluded-positions` list, and its behavior must be mapped identically (e.g. `&lt_c NAVIG SPACE`) on both QWERTY and MOUSE layers. This allows ZMK to process the hold-tap immediately.
