# set rate
set tcp_variant [lindex $argv 0]
set rate [lindex $argv 1]
set tracefilename [lindex $argv 2]
set s [lindex $argv 3]
set duration [lindex $argv 4]

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

set start_time [random_num 5]
set end_time [expr $start_time + $duration]
set cbr_end_time [expr $end_time + 1]
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
set tcp [new Agent/$tcp_variant]
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set window_ 100

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP
$ftp set random_ $s

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
$ns at $start_time "$ftp start"
$ns at $end_time "$ftp stop"
$ns at $cbr_end_time "$cbr stop"


#Call the finish procedure after 1 seconds of simulation time
$ns at $finish_time "finish"

#Run the simulation
global defaultRNG
$defaultRNG seed $s
$ns run
