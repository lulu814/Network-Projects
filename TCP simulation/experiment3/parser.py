import sys


def parse_trace_file(trace_file, src_node, dest_node, duration, protocol):
    # hardcode run time of tcp to be 100s
    time_series_length = int(duration)
    num_samples = [0] * time_series_length
    bytes_received = [0] * time_series_length
    total_delay = [0] * time_series_length
    packet_enqueue_time = {}

    throughput = []
    eedelay = []
    for line in open(trace_file):
        # trace file format http://nile.wpi.edu/NS/analysis.html
        event, time, from_node, to_node, pkt_type, pkt_size, flags, fid, src_addr, dst_addr, seq_num, pkd_id = line.split()
        index = int(float(time))
        if index >= time_series_length:
            break
        if pkt_type == protocol and event == "r" and to_node == dest_node and src_addr.startswith(src_node) and dst_addr.startswith(dest_node):
            bytes_received[index] += int(pkt_size)
            num_samples[index] += 1
            delay = float(time) - packet_enqueue_time[pkd_id]
            total_delay[index] += delay
        if pkt_type == protocol and event == "+" and from_node == src_node and src_addr.startswith(src_node) and dst_addr.startswith(dest_node):
            packet_enqueue_time[pkd_id] = float(time)

    acc_bytes_received = 0
    acc_delay = 0
    acc_num_samples = 0
    for i in range(len(num_samples)):
        if num_samples[i] != 0:
            throughput.append(bytes_received[i] * 8.0 / 1000000)
            eedelay.append(total_delay[i] / num_samples[i])
        else:
            throughput.append(0)
            eedelay.append(0)

    return throughput, eedelay


if __name__ == "__main__":
    filename = sys.argv[1]
    src_node = sys.argv[2]
    dest_node = sys.argv[3]
    duration = float(sys.argv[4])
    protocol = sys.argv[5]
    throughput, delay = parse_trace_file(filename, src_node, dest_node, duration, protocol)
    print(" ".join(map(str, throughput)) + "," + " ".join(map(str, delay)))
