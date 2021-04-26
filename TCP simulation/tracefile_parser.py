import sys


def parse_trace_file(trace_file, src_node, dest_node, duration):
    # hardcode run time of tcp to be 100s
    num_samples = 0
    packet_sent = 0.0
    packet_dropped = 0.0
    bytes_received = 0
    total_delay = 0
    packet_enqueue_time = {}

    for line in open(trace_file):
        # trace file format http://nile.wpi.edu/NS/analysis.html
        event, time, from_node, to_node, pkt_type, pkt_size, flags, fid, src_addr, dst_addr, seq_num, pkd_id = line.split()
        if pkt_type == "tcp" and event == "r" and to_node == dest_node and src_addr.startswith(src_node) and dst_addr.startswith(dest_node):
            bytes_received += int(pkt_size)
            num_samples += 1
            delay = float(time) - packet_enqueue_time[pkd_id]
            total_delay += delay
        if pkt_type == "tcp" and event == "+" and from_node == src_node and src_addr.startswith(src_node) and dst_addr.startswith(dest_node):
            packet_enqueue_time[pkd_id] = float(time)

        if pkt_type == "tcp" and event == "+" and from_node == src_node:
            packet_sent += 1
        if pkt_type == "tcp" and event == "d" and src_addr.startswith(src_node):
            packet_dropped += 1

    # Throughput (= the average amount data received by the receiver per unit time,
    # regardless of whether the data is retransmission or not)
    # unit mbps
    throughput = (bytes_received * 8) / duration / 1000000
    # https://ns2ultimate.tumblr.com/post/5240359082/post-processing-ns2-result-using-ns2-trace-ex3
    # end to end delay =
    # Since packets are created from the src address, until the packets are destroyed at the destination address
    eedelay = total_delay / num_samples
    # packets from src node dropped / total packets sent from src node
    drop_rate = packet_dropped / packet_sent
    return throughput, drop_rate, eedelay


if __name__ == "__main__":
    filename = sys.argv[1]
    src_node = sys.argv[2]
    dest_node = sys.argv[3]
    duration = float(sys.argv[4])
    throughput, drop_rate, delay = parse_trace_file(filename, src_node, dest_node, duration)
    print("{},{},{}".format(throughput, drop_rate, delay))

