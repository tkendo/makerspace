###########################
#
# Author: Jack Watkin
# Purpose: Ping client to test
#          connectivity 
# ./script <ip address>
##########################

#ensure that an address has been passed
if [[ $# -eq 0 ]]; then
    echo "Usage: ./EMItest.sh <IP Address>"
    exit 1
fi

#use <CTRL-Z> to stop and then kill the job
while true; do
    #ping arduino with atleast 128 bytes of data 10 times per test
    #continue until user halts the job
    ping -q -c 10 -s 64 $1 >> $2 
    tail -4 $2 1>&2  
#    ping -q -c 10 -s 64 192.168.2.43 >> test_out
#    tail -4 test_out
#    ping -q -c 10 -s 64 192.168.2.44 >> test_out
#    tail -4 test_out
#    ping -q -c 10 -s 64 192.168.2.45 >> test_out
#    tail -4 test_out
#    ping -q -c 10 -s 64 192.168.2.46 >> test_out
#    tail -4 test_out
done 
