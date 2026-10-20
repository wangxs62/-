# 4.1 smoke test record
Environment: FFmpeg/FFprobe available, OpenCV 4.13.0, numpy installed.
Synthetic test: 3s test source, first 1.5s solid red, next 1.5s solid blue. `scripts/analyze_video.py` detected a possible cut around 1.4-1.5s plus two possible static/freeze candidates (expected conservative false positives for legitimate still shots). Dense suspect frames emitted.
Editing test: `scripts/edit_video.py` dry-run produced no output; `--approve` rendered two clip selections (0-1.0s and 1.6-2.7s) as a ~2.1s silent MP4. Verify final encoded duration separately.
This tests software plumbing, not semantic anomaly recognition or accuracy on production footage. Real-world benchmark dataset and calibrated sensitivity remain to be developed.
