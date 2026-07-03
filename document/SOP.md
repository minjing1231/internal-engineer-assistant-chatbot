# SOP Manual for RAG Knowledge Source

Source: Appendix A from `Take-Home_Assignment_Agentic_AI_Developer.pdf`.

This SOP manual is the knowledge source for retrieval-augmented generation. The chatbot should retrieve from this content before generating answers.

## SOP-ETCH-001: Etcher RF Power Instability - Alarm RF101

Applicable Equipment: Plasma Etcher / Etcher-03

Severity: High

### Symptoms

- RF generator output fluctuates beyond accepted process tolerance.
- Alarm appears during plasma ignition or steady-state plasma step.
- RF power trend shows sudden dip or oscillation.

### Safety Precautions

- Confirm tool is in safe state before opening panels.
- Do not touch RF cables while RF power is enabled.
- Follow lockout/tagout procedure if inspecting RF hardware.

### Troubleshooting Steps

1. Verify RF generator output reading from tool HMI.
2. Check recent RF power trend for sudden drop or oscillation.
3. Inspect RF cable connectors for looseness or visible damage.
4. Check matching network status and reflected power reading.
5. Review last preventive maintenance record for RF module or cable work.
6. Restart RF subsystem only if permitted by local operating procedure.

### Escalation Criteria

- Downtime exceeds 30 minutes.
- RF101 repeats more than twice within 7 days.
- Reflected power remains abnormal after cable and matching network check.
- Visible cable damage or suspected RF generator fault is found.

## SOP-CMP-002: CMP Pad Pressure Low - Alarm CMP205

Applicable Equipment: CMP Tool / CMP-02

Severity: Medium

### Symptoms

- Pad pressure falls below configured operating range.
- Pressure reading is noisy or lower than recipe setpoint.
- Polishing uniformity may be affected.

### Safety Precautions

- Do not place hands near moving platen or carrier head.
- Ensure tool is stopped before inspecting pad or carrier head.

### Troubleshooting Steps

1. Check current pad pressure reading against recipe setpoint.
2. Inspect pressure sensor value for noise or unstable signal.
3. Check hydraulic line for visible leakage.
4. Confirm pad age and whether pad replacement is due.
5. Run pressure calibration or sensor check if available.

### Escalation Criteria

- Pressure remains low after sensor check.
- Hydraulic leak is suspected.
- Same alarm repeats after pad replacement.

## SOP-CVD-003: CVD Gas Flow Deviation - Alarm GAS012

Applicable Equipment: PECVD / CVD-05

Severity: High

### Symptoms

- Measured gas flow deviates from recipe setting.
- Mass flow controller reading is unstable or outside tolerance.
- Process gas supply pressure may be abnormal.

### Safety Precautions

- Treat gas-related alarms as high priority.
- Do not bypass gas interlocks.
- Escalate if toxic, flammable, or unknown gas risk is suspected.

### Troubleshooting Steps

1. Compare MFC actual reading with recipe target.
2. Check gas supply pressure and facility gas status.
3. Review recent MFC calibration record.
4. Perform leak check if procedure allows.
5. Check valve status and gas line restrictions.
6. Hold affected lot until process engineer review if recipe deviation occurred.

### Escalation Criteria

- Any gas safety concern exists.
- Downtime exceeds 20 minutes for high-severity gas alarm.
- MFC drift or leak is suspected.
- Affected lot processed during deviation.

## SOP-LITHO-004: Lithography Wafer Alignment Failure - Alarm ALIGN011

Applicable Equipment: Lithography Scanner / Litho-01

Severity: Low

### Symptoms

- Tool cannot detect wafer alignment mark or notch.
- Alignment camera image may be unclear.
- Wafer orientation or recipe alignment setting may be incorrect.

### Safety Precautions

- Do not manually move wafer stage unless approved.
- Avoid touching optical components without proper procedure.

### Troubleshooting Steps

1. Clean alignment camera viewing window using approved method.
2. Inspect wafer notch/orientation.
3. Check alignment recipe and product setup.
4. Run alignment calibration routine.
5. Retry wafer alignment using test wafer if available.

### Escalation Criteria

- Alignment fails after cleaning and calibration.
- Multiple wafers fail alignment consecutively.
- Camera image remains unclear after cleaning.

## SOP-TEMP-005: Chamber Temperature High - Alarm TEMP008

Applicable Equipment: Etcher / CVD / Furnace Tools

Severity: Medium

### Symptoms

- Chamber temperature exceeds alarm threshold.
- Temperature trend rises above normal profile.
- Cooling water or heater control may be abnormal.

### Safety Precautions

- Do not open hot chamber until temperature is within safe range.
- Use heat-resistant PPE if inspection is required.

### Troubleshooting Steps

1. Check chamber temperature trend.
2. Verify cooling water flow and facility cooling status.
3. Check heater control output.
4. Inspect thermocouple or temperature sensor reading.
5. Allow chamber to stabilize before restart.

### Escalation Criteria

- Temperature remains high after cooling water check.
- Sensor reading is unstable or unrealistic.
- Alarm repeats after restart.

## SOP-VAC-006: Vacuum Pressure High - Alarm VAC033

Applicable Equipment: Vacuum Process Tools / PVD-02

Severity: High

### Symptoms

- Chamber cannot reach required vacuum pressure.
- Pressure remains higher than target after pump-down.
- Leak, pump issue, or door seal issue may be present.

### Safety Precautions

- Do not open chamber until vent sequence is complete.
- Follow vacuum pump safety procedure before inspection.

### Troubleshooting Steps

1. Check chamber door status and door seal condition.
2. Review pump-down curve and base pressure.
3. Check vacuum pump status and alarms.
4. Run leak check if available.
5. Inspect pressure gauge reading for abnormal behaviour.

### Escalation Criteria

- Vacuum cannot recover within 20 minutes.
- Leak check fails.
- Pump alarm is present.
- Production lot is inside chamber.

## SOP-ROBOT-007: Wafer Transfer Error - Alarm ROBOT017

Applicable Equipment: Wafer Handling Robot

Severity: Medium

### Symptoms

- Robot fails to pick, place, or transfer wafer.
- Wafer presence sensor may not detect wafer correctly.
- End-effector alignment may be off.

### Safety Precautions

- Do not reach into transfer area while robot power is enabled.
- Stop automatic transfer before inspection.
- Follow wafer breakage procedure if damage is suspected.

### Troubleshooting Steps

1. Check robot arm home position.
2. Inspect end-effector for contamination or damage.
3. Verify wafer presence sensor status.
4. Run robot dry-cycle without wafer if allowed.
5. Check whether wafer is misaligned in carrier or chamber.

### Escalation Criteria

- Wafer damage is suspected.
- Robot cannot complete dry-cycle.
- Sensor remains abnormal after cleaning.

## SOP-PART-008: Particle Count High - Alarm PART090

Applicable Equipment: Etch / Deposition / PVD Tools

Severity: High

### Symptoms

- Particle count exceeds process control limit.
- Chamber contamination, worn consumables, or ineffective cleaning may be present.
- Affected lot quality may be at risk.

### Safety Precautions

- Hold affected lot until process disposition.
- Do not resume production until particle qualification is completed if required.

### Troubleshooting Steps

1. Check recent chamber cleaning record.
2. Inspect consumables such as shield kit, liner, focus ring, or pad depending on tool type.
3. Run particle qualification wafer.
4. Review recent maintenance activities that may introduce contamination.
5. Compare current particle result with baseline trend.

### Escalation Criteria

- Particle count remains high after cleaning.
- Affected production lot is at risk.
- Repeated particle alarm occurs within 7 days.
