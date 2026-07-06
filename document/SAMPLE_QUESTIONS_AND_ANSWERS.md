# Sample Questions and FE Answers

This document contains 10 demo questions and expected frontend-style answers for the manufacturing repair assistant.

## 1. Etcher RF Power Instability

**Question**

```text
Etcher-03 triggered RF101 during plasma ignition. What should I check first?
```

**Expected FE Answer**

```text
Action Decision:
- Primary Action: Verify RF generator output reading from tool HMI.
- Escalate: Conditional
- Reason: RF101 is a high-severity RF power instability alarm. Escalation depends on whether the alarm persists, repeats, or hardware fault is suspected.

Issue Summary:
- Equipment: Etcher-03
- Alarm / Symptom: RF101
- Severity: High

Relevant SOP Context:
- SOP section(s) used: Troubleshooting Steps, Safety Precautions, Escalation Criteria

Recommended Checks:
1. Verify RF generator output reading from tool HMI.
2. Check recent RF power trend for sudden drop or oscillation.
3. Inspect RF cable connectors for looseness or visible damage.
4. Check matching network status and reflected power reading.

Likely Causes:
1. Loose RF cable.
2. RF generator drift.

Recovery / Next Steps:
1. Review last preventive maintenance record for RF module or cable work.
2. Restart RF subsystem only if permitted by local operating procedure.
3. Escalate if reflected power remains abnormal or visible cable damage is found.

Safety Precautions:
- Confirm tool is in safe state before opening panels.
- Do not touch RF cables while RF power is enabled.
- Follow lockout/tagout procedure if inspecting RF hardware.

Escalation Criteria:
- Downtime exceeds 30 minutes.
- RF101 repeats more than twice within 7 days.
- Reflected power remains abnormal after cable and matching network check.
- Visible cable damage or suspected RF generator fault is found.

Uncertainty / Missing Information:
- RF trend and reflected power values are not provided in the question.
```

## 2. CMP Pad Pressure Low

**Question**

```text
CMP-02 has low pad pressure. What are the likely causes and recovery steps?
```

**Expected FE Answer**

```text
Action Decision:
- Primary Action: Check current pad pressure reading against recipe setpoint.
- Escalate: Conditional
- Reason: CMP205 is medium severity. Escalation is needed if pressure remains low, hydraulic leakage is suspected, or the alarm repeats after pad replacement.

Issue Summary:
- Equipment: CMP-02
- Alarm / Symptom: Low pad pressure / CMP205
- Severity: Medium

Relevant SOP Context:
- SOP section(s) used: Symptoms, Troubleshooting Steps, Escalation Criteria

Recommended Checks:
1. Check current pad pressure reading against recipe setpoint.
2. Inspect pressure sensor value for noise or unstable signal.
3. Check hydraulic line for visible leakage.
4. Confirm pad age and whether pad replacement is due.
5. Run pressure calibration or sensor check if available.

Likely Causes:
1. Pressure sensor noise.
2. Hydraulic leakage.
3. Pad wear or replacement due.

Recovery / Next Steps:
1. Run pressure calibration or sensor check.
2. Replace or inspect pad if pad age indicates replacement is due.
3. Escalate if pressure remains low or hydraulic leak is suspected.

Safety Precautions:
- Do not place hands near moving platen or carrier head.
- Ensure tool is stopped before inspecting pad or carrier head.

Escalation Criteria:
- Pressure remains low after sensor check.
- Hydraulic leak is suspected.
- Same alarm repeats after pad replacement.

Uncertainty / Missing Information:
- Exact pressure reading and recipe setpoint are not provided.
```

## 3. CVD Gas Flow Deviation

**Question**

```text
CVD-05 triggered GAS012 during deposition. Should I escalate?
```

**Expected FE Answer**

```text
Action Decision:
- Primary Action: Escalate and verify gas flow deviation conditions.
- Escalate: Yes
- Reason: GAS012 is a high-severity gas flow deviation alarm. Gas-related alarms should be treated as high priority, and SOP escalation applies if any gas safety concern, MFC drift, leak suspicion, downtime over 20 minutes, or affected lot exists.

Issue Summary:
- Equipment: CVD-05
- Alarm / Symptom: GAS012
- Severity: High

Relevant SOP Context:
- SOP section(s) used: Safety Precautions, Troubleshooting Steps, Escalation Criteria

Recommended Checks:
1. Compare MFC actual reading with recipe target.
2. Check gas supply pressure and facility gas status.
3. Review recent MFC calibration record.
4. Perform leak check if procedure allows.
5. Check valve status and gas line restrictions.

Likely Causes:
1. MFC calibration drift.
2. Gas supply pressure issue.
3. Leak or gas line restriction.

Recovery / Next Steps:
1. Hold affected lot until process engineer review if recipe deviation occurred.
2. Escalate to process or equipment engineering for MFC/leak investigation.
3. Do not resume until gas safety and process impact are reviewed.

Safety Precautions:
- Treat gas-related alarms as high priority.
- Do not bypass gas interlocks.
- Escalate if toxic, flammable, or unknown gas risk is suspected.

Escalation Criteria:
- Any gas safety concern exists.
- Downtime exceeds 20 minutes for high-severity gas alarm.
- MFC drift or leak is suspected.
- Affected lot processed during deviation.

Uncertainty / Missing Information:
- Actual MFC reading, gas trend, and lot impact are not provided.
```

## 4. Lithography Alignment Failure

**Question**

```text
Litho-01 cannot align wafer properly. What SOP steps should I follow?
```

**Expected FE Answer**

```text
Action Decision:
- Primary Action: Clean the alignment camera viewing window using the approved method.
- Escalate: Conditional
- Reason: ALIGN011 is low severity, but escalation is needed if alignment still fails after cleaning/calibration or multiple wafers fail.

Issue Summary:
- Equipment: Litho-01
- Alarm / Symptom: Wafer alignment failure / ALIGN011
- Severity: Low

Relevant SOP Context:
- SOP section(s) used: Symptoms, Troubleshooting Steps, Escalation Criteria

Recommended Checks:
1. Clean alignment camera viewing window using approved method.
2. Inspect wafer notch/orientation.
3. Check alignment recipe and product setup.
4. Run alignment calibration routine.
5. Retry wafer alignment using test wafer if available.

Likely Causes:
1. Dirty alignment camera.
2. Incorrect wafer orientation.
3. Recipe or product setup issue.

Recovery / Next Steps:
1. Clean camera and verify image clarity.
2. Run alignment calibration.
3. Retry with test wafer if available.

Safety Precautions:
- Do not manually move wafer stage unless approved.
- Avoid touching optical components without proper procedure.

Escalation Criteria:
- Alignment fails after cleaning and calibration.
- Multiple wafers fail alignment consecutively.
- Camera image remains unclear after cleaning.

Uncertainty / Missing Information:
- Camera image status and wafer orientation are not provided.
```

## 5. Unknown Alarm

**Question**

```text
Unknown equipment triggered alarm ABC999. What should I do?
```

**Expected FE Answer**

```text
Cannot find alarm type ABC999. Please verify the exact alarm code and equipment ID from the tool HMI.
```

## 6. Vacuum Pressure High

**Question**

```text
PVD-02 triggered VAC033 during pump-down. What should I check?
```

**Expected FE Answer**

```text
Action Decision:
- Primary Action: Check chamber door status and door seal condition.
- Escalate: Conditional
- Reason: VAC033 is a high-severity vacuum pressure alarm. Escalate if vacuum cannot recover, leak check fails, pump alarm exists, or a production lot is inside.

Issue Summary:
- Equipment: PVD-02
- Alarm / Symptom: VAC033
- Severity: High

Relevant SOP Context:
- SOP section(s) used: Troubleshooting Steps, Safety Precautions, Escalation Criteria

Recommended Checks:
1. Check chamber door status and door seal condition.
2. Review pump-down curve and base pressure.
3. Check vacuum pump status and alarms.
4. Run leak check if available.
5. Inspect pressure gauge reading for abnormal behaviour.

Likely Causes:
1. Door seal leak.
2. Vacuum pump issue.
3. Pressure gauge abnormality.

Recovery / Next Steps:
1. Reseat or inspect door seal if abnormal.
2. Run leak check if available.
3. Escalate if vacuum cannot recover within 20 minutes or pump alarm is present.

Safety Precautions:
- Do not open chamber until vent sequence is complete.
- Follow vacuum pump safety procedure before inspection.

Escalation Criteria:
- Vacuum cannot recover within 20 minutes.
- Leak check fails.
- Pump alarm is present.
- Production lot is inside chamber.

Uncertainty / Missing Information:
- Pump-down curve, leak check result, and lot status are not provided.
```

## 7. Chamber Temperature High

**Question**

```text
Chamber temperature is high with TEMP008. What are the safety precautions?
```

**Expected FE Answer**

```text
Action Decision:
- Primary Action: Do not open the hot chamber until temperature is within safe range.
- Escalate: Conditional
- Reason: TEMP008 is medium severity. Escalate if temperature remains high after cooling water check, sensor reading is unstable, or the alarm repeats after restart.

Issue Summary:
- Equipment: Unknown equipment
- Alarm / Symptom: TEMP008
- Severity: Medium

Relevant SOP Context:
- SOP section(s) used: Safety Precautions, Troubleshooting Steps, Escalation Criteria

Recommended Checks:
1. Check chamber temperature trend.
2. Verify cooling water flow and facility cooling status.
3. Check heater control output.
4. Inspect thermocouple or temperature sensor reading.
5. Allow chamber to stabilize before restart.

Likely Causes:
1. Cooling water flow issue.
2. Heater control abnormality.
3. Temperature sensor or thermocouple issue.

Recovery / Next Steps:
1. Stabilize chamber temperature before restart.
2. Verify cooling water and heater control status.
3. Escalate if temperature remains high or sensor reading is unrealistic.

Safety Precautions:
- Do not open hot chamber until temperature is within safe range.
- Use heat-resistant PPE if inspection is required.

Escalation Criteria:
- Temperature remains high after cooling water check.
- Sensor reading is unstable or unrealistic.
- Alarm repeats after restart.

Uncertainty / Missing Information:
- Specific equipment ID and actual temperature trend are not provided.
```

## 8. Unknown Equipment ID

**Question**

```text
Etcher-0399 triggered RF101 during plasma ignition. What should I check first?
```

**Expected FE Answer**

```text
Cannot find equipment ID Etcher-0399. Do you mean Etcher-03?
```

## 9. Unknown Alarm ID

**Question**

```text
CVD-05 triggered GAS0 during deposition. Should I escalate?
```

**Expected FE Answer**

```text
Cannot find alarm type GAS0. Do you mean GAS012?
```

## 10. Wafer Transfer Error

**Question**

```text
Wafer handling robot triggered ROBOT017 during transfer. What should I check?
```

**Expected FE Answer**

```text
Action Decision:
- Primary Action: Check robot arm home position.
- Escalate: Conditional
- Reason: ROBOT017 is medium severity. Escalate if wafer damage is suspected, robot dry-cycle fails, or sensor remains abnormal after cleaning.

Issue Summary:
- Equipment: Wafer Handling Robot
- Alarm / Symptom: ROBOT017
- Severity: Medium

Relevant SOP Context:
- SOP section(s) used: Symptoms, Troubleshooting Steps, Safety Precautions, Escalation Criteria

Recommended Checks:
1. Check robot arm home position.
2. Inspect end-effector for contamination or damage.
3. Verify wafer presence sensor status.
4. Run robot dry-cycle without wafer if allowed.
5. Check whether wafer is misaligned in carrier or chamber.

Likely Causes:
1. End-effector contamination or damage.
2. Wafer presence sensor issue.
3. Wafer misalignment in carrier or chamber.

Recovery / Next Steps:
1. Stop automatic transfer before inspection.
2. Clean or inspect end-effector and wafer sensor.
3. Run dry-cycle without wafer if allowed.

Safety Precautions:
- Do not reach into transfer area while robot power is enabled.
- Stop automatic transfer before inspection.
- Follow wafer breakage procedure if damage is suspected.

Escalation Criteria:
- Wafer damage is suspected.
- Robot cannot complete dry-cycle.
- Sensor remains abnormal after cleaning.

Uncertainty / Missing Information:
- Wafer damage status and sensor state are not provided.
```
