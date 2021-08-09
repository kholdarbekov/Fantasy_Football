#!/usr/bin/env bash
SECONDS=0
export DJANGO_SETTINGS_MODULE=soccer.settings.production
PROJECT_PATH=/home/soccer
REPOSITORY_PATH=${PROJECT_PATH}
LOG_FILE=${PROJECT_PATH}/logs/clear_sessions.log
error_counter=0

echoerr() { echo "$@" 1>&2; }

cd ${PROJECT_PATH} || exit
mkdir -p logs

echo "=== Clearing up Outdated User Sessions ===" > ${LOG_FILE}
date >> ${LOG_FILE}

source venv/bin/activate
cd ${REPOSITORY_PATH} || exit
python manage.py clearsessions >> "${LOG_FILE}" 2>&1
function_exit_code=$?
if [[ $function_exit_code -ne 0 ]]; then
   {
       echoerr "Clearing sessions failed with exit code($function_exit_code)."
       error_counter=$((error_counter + 1))
   } >> "${LOG_FILE}" 2>&1
fi
duration=$SECONDS
echo "------------------------------------------" >> ${LOG_FILE}
echo "The operation took $((duration / 60)) minutes and $((duration % 60)) seconds." >> ${LOG_FILE}
exit $error_counter
or_counter