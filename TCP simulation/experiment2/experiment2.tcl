# set rate
set tcp_variant1 [lindex $argv 0]
set tcp_variant2 [lindex $argv 1]
set rate [lindex $argv 2]
set tracefilename [lindex $argv 3]
set s [lindex $argv 4]
set duration [lindex $argv 5]

#Create a simulator objec
set ns [new Simulator]

#Define different colors for data flows (for NAM)
$ns color 1 Blue
$ns color 2 Red

#Open the trace file (before you start the experiment!)
set tf [open $tracefilename w]
$ns trace-all $tf

#Define a 'finish' procedure
proc finish {} {
        global ns tf nf
	# Close the trace file (after you finish the experiment!)
	$ns flush-trace
	close $tf
	exit 0
}

proc random_num { upper_limit } {
    expr { rand() * $upper_limit }
}

set start_time1 [random_num 5]
set end_time1 [expr $start_time1 + $duration]
set start_time2 [random_num 5]
set end_time2 [expr $start_time2 + $duration]
set cbr_end_time [expr max($end_time1, $end_time2) + 1]
set finish_time [expr $cbr_end_time + 1]

#Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

#Set buffer size for each link
$ns queue-limit $n1 $n2 100
$ns queue-limit $n5 $n2 100
$ns queue-limit $n2 $n3 100
$ns queue-limit $n3 $n4 100
$ns queue-limit $n3 $n6 100

#Setup a TCP connection
set tcp1 [new Agent/TCP/$tcp_variant1]
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set window_ 100

set tcp2 [new Agent/TCP/$tcp_variant2]
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
$tcp2 set window_ 100


#Setup a FTP over TCP connection
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP
$ftp1 set random_ $s

set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP
$ftp2 set random_ $s

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ $rate
$cbr set random_ $s

#Schedule events for the CBR and tcp agents
$ns at 0.0 "$cbr start"
$ns at $start_time1 "$ftp1 start"
$ns at $start_time2 "$ftp2 start"
$ns at $end_time1 "$ftp1 stop"
$ns at $end_time2 "$ftp2 stop"
$ns at $cbr_end_time "$cbr stop"


#Call the finish procedure after 1 seconds of simulation time
$ns at $finish_time "finish"

#Run the simulation
global defaultRNG
$defaultRNG seed $s
$ns run
