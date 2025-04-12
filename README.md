# Part 1 - Network loops
## How to run
```bash
sudo python3 Q1_parta.py
```
after opening mininet CLI
```bash
mininet> s1 tcpdump -i any arp or icmp -n -e -w capture.pcap &
```
and then
```bash
mininet> h3 ping -c 1 h1
```
then close the mininet program and look at the pcap file using Wireshark
```bash
mininet> exit
sudo wireshark capture.pcap
```

# Part 2 - NAT
## Running the program
```bash
sudo python3 Q2.py
```


# Part 3 - Distance Vector Routing

## Requirements

- GCC or compatible C compiler
- Linux or Windows (with WSL, MinGW, or similar)

## Compilation and Execution

### To compile
```bash
gcc -o part3 distance_vector.c node0.c node1.c node2.c node3.c -Wall
```
This creates an executable named `dvr`.

### Running the Simulation
You can run the simulation with an optional trace level parameter:
```bash 
./part3
```


## Trace Levels

| Level | Description                                      |
|-------|--------------------------------------------------|
| 0     | Minimal output: Final routing tables and key events |
| 1     | Basic tracing: Packet transmissions and table updates |
| 2     | Detailed tracing: Packet contents and decisions |
| 3     | Full debug: Internal steps and queuing details  |

**Note:** Higher trace levels provide more visibility into the simulation.


For more details, refer to the [Notion document](https://www.notion.so/CN-Assignment-3-1d3dacf332c080178d4bcbf897786b87?pvs=4) for Question 1 and 2.