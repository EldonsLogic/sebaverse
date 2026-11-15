#!/bin/sh
# Authored Sebaverse synthetic F2 image only. Never emulate privilege switching.
printf '%s\n' 'Sebaverse F2: gosu is unavailable; start the test image as postgres.' >&2
exit 126
