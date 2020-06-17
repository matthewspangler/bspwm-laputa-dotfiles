
#! /bin/bash
#
# Lemonbar configuration by Cosmophile
# _                            _                _
#| | ___ _ __ ___   ___  _ __ | |__   __ _ _ __| |
#| |/ _ \ '_ ` _ \ / _ \| '_ \| '_ \ / _` | '__| |
#| |  __/ | | | | | (_) | | | | |_) | (_| | |  |_|
#|_|\___|_| |_| |_|\___/|_| |_|_.__/ \__,_|_|  (_)
#

#This prevents loading more than 1 lemonbar at a time.
if xdo id -a "$PANEL_WM" > /dev/null ; then
	    printf "%s\n" "The panel is already running." >&2
	        exit 1
	fi

	trap 'trap - TERM; kill 0' INT TERM QUIT EXIT

# Import the colors
. "${HOME}/.cache/wal/colors.sh"

# Define the clock
Clock() {
        DATETIME=$(date "+%a %b %d, %T")

        echo -n "$DATETIME"
}

Workspace() {
	
}

# Print the clock

while true; do
        echo "%{r}$(Clock)"
        sleep 1
done
