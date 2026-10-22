#!/usr/bin/env bash
# Runs the remaining compute-heavy phases unattended, after the parametric study finishes.
#   bash pipeline_rest.sh   (from work/src)
set -u
LOG=../results
until grep -q "parametric_fan.csv\|Traceback" $LOG/parametric_run.log; do sleep 30; done
echo "[$(date +%H:%M)] parametric done" >> $LOG/pipeline.log
python -u verify.py > $LOG/verify_run.log 2>&1
echo "[$(date +%H:%M)] verification v2 done" >> $LOG/pipeline.log
python -u sensitivity.py > $LOG/sensitivity_run.log 2>&1
echo "[$(date +%H:%M)] sensitivity (key designs) done" >> $LOG/pipeline.log
../../.venv/Scripts/python.exe -u optimize.py extended --pop 24 --gens 20 --algorithm NSGA-III > $LOG/opt_extended_run.log 2>&1
echo "[$(date +%H:%M)] extended optimisation done" >> $LOG/pipeline.log
