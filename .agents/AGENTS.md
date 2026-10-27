# ZMK Trackpoint and Layer Tuning Rules

When working on pointer sensitivity, scrolling speeds, or layer timeouts in this repository, always adhere to the following principles:

## 1. Trackpoint Sensitivity and Effort (TP_SCURVE_MID & TP_MIN_MULT)
* The s-curve acceleration midpoint `TP_SCURVE_MID` in `trackpoint_0x15.c` controls physical effort. 
* Shifting `TP_SCURVE_MID` to a lower value (e.g. `9.0f` or `12.0f` instead of the default `25.0f`) makes exponential acceleration trigger under lighter pressure, reducing finger strain.
* The precision zone minimum multiplier `TP_MIN_MULT` (configured via `CONFIG_TRACKPOINT_MIN_MULT_PERCENT`, default `35%` / `0.35f`) provides sub-linear deceleration specifically for micro-movements (deflections $\le$ 2 counts). A dual-zone knee curve ramps from `TP_MIN_MULT` at rest up to `1.0x` at 2 counts, and then accelerates from `1.0x` up to `TP_MAX_MULT` for normal and high-speed pushes. This drops the single-pixel crawl speed to ~40 px/s for text selection while preventing normal cruising deflections (3–8 counts) from feeling heavy or sluggish.

## 2. Scroll Divisor Scaling
* The trackpoint reports at a high frequency (around 100Hz). 
* Do not use small divisors (like `10` or less) for both slow and fast scroll speeds simultaneously. Since scroll event tick counts are proportional to coordinate deltas, small divisors will cause scrolling to accelerate uncontrollably fast.
* High constant divisors (e.g., `40` or `50` for both `SLOW` and `FAST`) make scrolling feel heavy, sluggish, and unresponsive, requiring ~200ms of sustained pressure just to register a single scroll tick.
* **Progressive Quadratic Curve**: Setting `CONFIG_TRACKPOINT_SCROLL_DIVISOR_SLOW=22` and `CONFIG_TRACKPOINT_SCROLL_DIVISOR_FAST=12` with quadratic interpolation (`t^2`) provides the optimal balance: light finger touches start scrolling effortlessly in ~50ms, cruising speed is comfortable and stable, and firmer pushes accelerate cleanly without losing control.

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

## 6. TrackPoint Driver Stability, Anti-Recoil, and Axis Isolation
* **I2C Interrupt Packet Drain Loop**: Under BLE transmissions or work queue latency, multiple packets can buffer in the TrackPoint 0x15 module. Always drain up to 5 packets or until the motion GPIO INT line returns to inactive (HIGH / 0). Otherwise, an asserted edge interrupt pin can remain asserted, stalling pointer updates.
* **Anti-Recoil / Negative Drift Suppression**: When stopping after a firm push (`dist >= 6.0`), mechanical rebound of the strain gauge module outputs small opposite-direction counts (`dist <= 2.0`, `dot < 0`). If detected within 150ms of a firm push, suppress these opposite micro-counts to 0 so the cursor stops dead on target without backward jitter.
* **Dominant Axis Locking in Scroll Mode**: When scrolling with the trackpoint, human finger pressure tends to induce slight diagonal wobble. Apply dominant axis filtering (`abs_dy * 2 > abs_dx * 3` isolates vertical scrolling and zeroes out horizontal drift; vice-versa for horizontal scrolling) to keep webpage/document scrolling locked on the intended axis.

## 7. Power Management, Display Behavior, and Zero Wake Lag
* **Event-Driven Work Queues (No Infinite Polling)**: Never leave delayable work loops polling continuously (e.g. 5ms/10ms loops in `trackpad_led.c` and `custom_led.c`). When LEDs fade to 0, stop rescheduling work. Use event listeners (`zmk_activity_state_changed`, `zmk_position_state_changed`, and motion wakes) to restart work only when needed. This drops idle current from ~15mA down to ~25–30 µA.
* **Always-On E-Ink / Memory LCD Display (`CONFIG_ZMK_SLEEP=n`)**:
  * The LPM009M360A is a Memory-in-Pixel (MIP) reflective LCD, commonly treated as an "E-ink" screen because of its paper-like appearance and micro-amp static draw.
  * Unlike true electrophoretic e-ink, a Memory LCD requires a tiny retention voltage ($V_{DD}$) on `EXT_POWER` to maintain its internal SRAM cells.
  * If deep sleep (`CONFIG_ZMK_SLEEP=y`) is enabled, ZMK disables `EXT_POWER` after the timeout, causing the display to fade to black and cutting power to the TrackPoint module (preventing touch wakeup).
  * To achieve an **always-on display (never black) and zero wake lag**, set `CONFIG_ZMK_SLEEP=n`. System ON tickless idle keeps the Memory LCD on indefinitely, keeps the BLE split link active, and allows the TrackPoint and keys to respond instantly on the very first touch with months of standby battery.
* **ZMK Studio on Split Peripherals**:
  * ZMK Studio only operates on the central half to manage keymaps; peripherals do not store keymaps.
  * Always set `CONFIG_ZMK_STUDIO=n` on the peripheral half. Enabling Studio RPC threads on the peripheral triggers known power management lockups and HardFaults during low-power transitions.
* **Background Display Timers**:
  * Periodic widget/image switch work items (such as `img_switch_work` in `peripheral_status.c`) must be gated with `zmk_activity_get_state() == ZMK_ACTIVITY_ACTIVE` and cancelled during idle/sleep to avoid waking the CPU or pushing SPI transactions to unpowered displays.
* **EXT_POWER Sequencing**:
  * Always declare `init-delay-ms = <50>;` on `EXT_POWER` nodes so power rails and display controllers have time to stabilize before SPI/I2C communication commences.
