#!/bin/bash
set -e
LOGFILE=/var/log/newfies/gunicorn_newfies_dialer.log
LOGDIR=$(dirname $LOGFILE)

# The number of workers is number of worker processes that will serve requests.
# You can set it as low as 1 if you’re on a small VPS.
# A popular formula is 1 + 2 * number_of_cpus on the machine (the logic being,
# half of the processess will be waiting for I/O, such as database).
NUM_WORKERS=1

# user/group to run as
USER=newfies_dialer
GROUP=newfies_dialer

cd /usr/share/virtualenvs/newfies-dialer
source bin/activate
cd /usr/share/newfies

test -d $LOGDIR || mkdir -p $LOGDIR

#Execute unicorn
exec gunicorn_django -b 127.0.0.1:8123 -w $NUM_WORKERS --timeout=300 \
    --user=$USER --group=$GROUP --log-level=debug \
    --log-file=$LOGFILE 2>>$LOGFILE
