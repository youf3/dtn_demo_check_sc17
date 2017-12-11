server= #serverip

iperf3 -c $server -p 5001 -t1s

if [ $? == 0 ] ; then

    sleep 1
    duration=120
    current_time=`date -u +%y%m%d_%H%M%S`

    folder_dayname=`date -u +%y%m%d`
    folder_secname=`date -u +%H%M%S`

    pathdir="dtn_log/"$folder_dayname"/"$folder_secname
    mkdir -p $pathdir

    tmux new-session -d -s "8_iperf3_sessions" "iperf3 -c $server -p 5001 -Z -t${duration}s -b12G -f g -A0,0 -w500M ; sleep 1 ; tmux capture-pane -t 8_iperf3_sessions.0 -p -S -5 > c1.log"
    tmux set-option remain-on-exit on

    tmux split-window -v -t 0 "iperf3 -c $server -p 5002 -Z -t${duration}s -b12G -f g -A1,2 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.1 -S -5 > c2.log"
    tmux split-window -v -t 0 "iperf3 -c $server -p 5003 -Z -t${duration}s -b12G -f g -A2,4 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.2 -S -5 > c3.log"
    tmux split-window -v -t 0 "iperf3 -c $server -p 5004 -Z -t${duration}s -b12G -f g -A3,6 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.3 -S -5 > c4.log"
    tmux select-layout even-vertical 

    tmux split-window -h -t 0 "iperf3 -c $server -p 5005 -Z -t${duration}s -b12G -f g -A4,8 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.4 -S -5 > c5.log"
    tmux split-window -h -t 1 "iperf3 -c $server -p 5006 -Z -t${duration}s -b12G -f g -A5,10 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.5 -S -5 > c6.log"
    tmux split-window -h -t 2 "iperf3 -c $server -p 5007 -Z -t${duration}s -b12G -f g -A6,12 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.6 -S -5 > c7.log"
    tmux split-window -h -t 3 "iperf3 -c $server -p 5008 -Z -t${duration}s -b12G -f g -A7,14 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.7 -S -5 > c8.log ; sleep 1 ; tmux detach"
 
    tmux attach -t "8_iperf3_sessions"

    tmux kill-session -t "8_iperf3_sessions"

    sum=0
    for i in $(tail -n 5 c*.log |grep sender |awk {'print $7'});do 
         sum=$(echo "print ${sum} + ${i}" | python ) 
    done
    echo "$current_time $sum Gbits/sec" >> dtn_log/sending.log

    tmux new-session -d -s "8_iperf3_sessions" "iperf3 -c $server -p 5001 -Z -t${duration}s -b12G -f g -R -A0,0 -w500M ; sleep 1 ; tmux capture-pane -t 8_iperf3_sessions.0 -p -S -5 > r1.log"
    tmux set-option remain-on-exit on

    tmux split-window -v -t 0 "iperf3 -c $server -p 5002 -Z -t${duration}s -b12G -f g -R -A1,2 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.1 -S -5 > r2.log"
    tmux split-window -v -t 0 "iperf3 -c $server -p 5003 -Z -t${duration}s -b12G -f g -R -A2,4 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.2 -S -5 > r3.log"
    tmux split-window -v -t 0 "iperf3 -c $server -p 5004 -Z -t${duration}s -b12G -f g -R -A3,6 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.3 -S -5 > r4.log"
    tmux select-layout even-vertical

    tmux split-window -h -t 0 "iperf3 -c $server -p 5005 -Z -t${duration}s -b12G -f g -R -A4,8 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.4 -S -5 > r5.log"
    tmux split-window -h -t 1 "iperf3 -c $server -p 5006 -Z -t${duration}s -b12G -f g -R -A5,10 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.5 -S -5 > r6.log"
    tmux split-window -h -t 2 "iperf3 -c $server -p 5007 -Z -t${duration}s -b12G -f g -R -A6,12 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.6 -S -5 > r7.log"
    tmux split-window -h -t 3 "iperf3 -c $server -p 5008 -Z -t${duration}s -b12G -f g -R -A7,14 -w500M ; sleep 1 ; tmux capture-pane -p -t 8_iperf3_sessions.7 -S -5 > r8.log ; sleep 1; tmux detach"

    tmux attach -t "8_iperf3_sessions"

    tmux kill-session -t "8_iperf3_sessions"

    sum=0
    for i in $(tail -n 5 r*.log |grep receiver |awk {'print $7'});do
         sum=$(echo "print ${sum} + ${i}" | python )
    done
    echo "$current_time $sum Gbits/sec" >> dtn_log/receiving.log

    mv *.log $pathdir
fi
