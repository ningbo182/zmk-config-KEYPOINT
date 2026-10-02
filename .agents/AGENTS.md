# ZMK Trackpoint and Layer Tuning Rules

When working on pointer sensitivity, scrolling speeds, or layer timeouts in this repository, always adhere to the following principles:

## 1. Trackpoint Sensitivity and Effort (TP_SCURVE_MID & TP_MIN_MULT)
* The s-curve acceleration midpoint `TP_SCURVE_MID` in `trackpoint_0x15.c` controls physical effort. 
* Shifting `TP_SCURVE_MID` to a lower value (e.g. `9.0f` or `12.0f` instead of the default `25.0f`) makes exponential acceleration trigger under lighter pressure, reducing finger strain.
* The precision zone minimum multiplier `TP_MIN_MULT` (configured via `CONFIG_TRACKPOINT_MIN_MULT_PERCENT`, default `35%` / `0.35f`) provides sub-linear deceleration specifically for micro-movements (deflections $\le$ 2 counts). A dual-zone knee curve ramps from `TP_MIN_MULT` at rest up to `1.0x` at 2 counts, and then accelerates from `1.0x` up to `TP_MAX_MULT` for normal and high-speed pushes. This drops the single-pixel crawl speed to ~40 px/s for text selection while preventing normal cruising deflections (3–8 counts) from feeling heavy or sluggish.

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
* **Timeout Reset on Clicks (`zmk,input-processor-temp-layer-ext`)**: Stock ZMK's `temp-layer` counts down to layer deactivation without resetting its timer when mouse buttons are clicked, causing the mouse layer to drop mid-click or mid-drag. Using the extended input processor `zmk,input-processor-temp-layer-ext` with an `arm-only` instance connected to `&mkp` via `mkp_arm_listener` refreshes the timeout on every click event, and holds the layer open indefinitely while any mouse button remains pressed.

## 5. ThinkPad-Style Motion Smoothing and Cadence
* **EMA Low-Pass Filtering**: Raw strain gauge readings contain physiological hand tremor (8-12Hz) and integer stepping quantization. Applying an EMA filter (`CONFIG_TRACKPOINT_SMOOTH_ALPHA`, default `65` / `0.65f`) transforms discrete integer steps into a continuous, fluid analog motion identical to classic IBM/Lenovo TrackPoints.
* **Cadence Gate**: Do not gate mouse reports with `>= 10ms` thresholds when the hardware interrupt runs at ~100Hz (~10ms). Millisecond kernel timer jitter causes alternating frames to block and clump into 20ms double-packet bursts, creating 50Hz micro-judder. Use a `>= 7ms` gate to allow every 10ms hardware packet through without delay while still protecting the BLE HID queue.
* **Stroke Isolation**: When the trackpoint is idle for `>30ms` (user lifts or pauses), reset filtered deltas and fractional residuals to `0` so the next stroke starts cleanly and symmetrically without carrying forward biased fractions from previous moves.
