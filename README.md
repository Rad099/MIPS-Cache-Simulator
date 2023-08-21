# MIPS-Cache-Simulator

This program simulates a MIPS Processor with fully functional Cache simulation and register display. Below is a quick guide on how to use the program's features.

## Introduction to the Simulator

The MIPS Simulator is written in Python. The program takes a file full of hex instructions and converts them to their respective binary and assembly representations. The program then manipulates a register table based on the instructions. It also simulates memory load/store, branches/jumps, as well as a PC counter. A Cache Class was later added for additional functionality. The cache system works by tracking memory reads and writes and stores their respective tags in a special stucture. It then writes into a cache log to display hits and misses, as well as LRU placements and removals. After a program is complete, it gives the accurate hit/miss ratio and the overall effectiveness of the cache. 

## Running mode

The simulator offers 2 modes before executing the hex program. 

* An instruction-by-instruciton mode to monitor every change to the register table and cache log.
* A full sweep run that does not display the register table until the end of the simulation. This is useful for quick assessment of a program's results.

(Note: If you are in the instruction-by-instruction mode, you can change it to full sweep mode at any time).

## Cache Configuration

There are 4 types of Cache architecture to choose from:

* 1-way 8-set block-size: 64 bytes
* 1-way 4-set block-size: 32 bytes
* 4-way Fully-Associative block-size: 32 bytes
* 4-way 2-sets block-size: 64 bytes


## Results

After a program is done executing, the user is given the option to either:

* Display the register table as a well as any memory written or changed.
* Display a summary of cache performance.

