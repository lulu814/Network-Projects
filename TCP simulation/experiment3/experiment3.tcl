# set rate
set tcp_variant [lindex $argv 0]
set queuing_algorithms [lindex $argv 1]
set tracefilename [lindex $argv 2]
set s [lindex $argv 3]
set cbr_start_time [lindex $argv 4]
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

set random_time [random_num 5]
set finish_time [expr $duration + 1]

#Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms $queuing_algorithms
$ns duplex-link $n5 $n2 10Mb 10ms $queuing_algorithms
$ns duplex-link $n2 $n3 10Mb 10ms $queuing_algorithms
$ns duplex-link $n3 $n4 10Mb 10ms $queuing_algorithms
$ns duplex-link $n3 $n6 10Mb 10ms $queuing_algorithms

#Set buffer size for each link
$ns queue-limit $n1 $n2 10
$ns queue-limit $n5 $n2 10
$ns queue-limit $n2 $n3 10
$ns queue-limit $n3 $n4 10
$ns queue-limit $n3 $n6 10

#Setup a TCP connection
set tcp [new Agent/TCP/$tcp_variant]
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
#$tcp set window_ 100

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP
$ftp set random_ $s

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set rate_ 8Mb
$cbr set random_ $s

#Schedule events for the CBR and tcp agents
$ns at $cbr_start_time "$cbr start"
$ns at 0 "$ftp start"
$ns at $duration "$ftp stop"
$ns at $duration "$cbr stop"


#Call the finish procedure after 1 seconds of simulation time
$ns at $finish_time "finish"

#Run the simulation
global defaultRNG
$defaultRNG seed $s
$ns run
