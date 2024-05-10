#!/bin/sh
# create a dir if nor exists than mount /dev/mmcblk0p1

PATH="/webserver/fileshare/"
DEVICE="/dev/mmcblk0p3"

routine(){
	/bin/mkdir -p $PATH 
                     
	if /bin/grep -qs '/dev/mmcblk0p3 /webserver/fileshare' /proc/mounts; then
	    echo $DEVICE " is mounted."                  
	else                                                   
	    /bin/mount $DEVICE $PATH
	fi
}

start(){
	routine
	sleep 3
}

stop(){
	routine
}

case "$1" in 
    start)
       start
       ;;
    stop)
       stop
       ;;
    restart)
       start
       stop
       ;;
    status)
       # code to check status of app comes here 
       # example: status program_name
       ;;
    *)
       echo "Usage: $0 {start|stop|status|restart}"
esac

exit 0 


