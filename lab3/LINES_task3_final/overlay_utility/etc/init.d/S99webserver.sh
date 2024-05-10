#!/bin/sh

PIDFILE="/var/run/webserver.pid"

start() {
	echo "Starting webserver..."
	cd /webserver
	start-stop-daemon -b -S -q -m -p "$PIDFILE" \
                --exec /usr/bin/python /webserver/webserver.py
	status=$?
	if [ "$status" -eq 0 ]; then
		echo "OK"
	else
		echo "FAIL"
	fi
	return "$status"
}

stop() {
	printf "Stopping webserver: "
	start-stop-daemon -K -q -p "$PIDFILE"
	status=$?                              
	if [ "$status" -eq 0 ]; then
		rm -f "$PIDFILE"    
		echo "OK"           
	else                    
		echo "FAIL"
	fi                 
	return "$status"   
} 

case "$1" in
	start)
		start
		;;
	stop)
		stop
		;;
	restart|reload)
		stop
		sleep 1
		start
		;;
	*)
		echo "Usage: $0 {start|stop|restart}"
		exit 1
esac

