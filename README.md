---
title: Using True Random Numbers in Python
tags: Python Terminal Random Number Module
author: fygar256
slide: false
---

This is a Python module for extracting true random numbers.

There are two types of random numbers usable by computers: pseudorandom numbers with periodicity, and true random numbers obtained from TRNG. There are also "perfectly random numbers," which can only be handled probabilistically. In other words, perfectly random numbers only exist in the realm of ideas.

In Python 3, the `random` module is mainly used to access random numbers, but this generates pseudorandom numbers, not true random numbers. However, x86_64 can obtain true random numbers from environmental noise using RDSEED, so we will use this. (Normally, RDSEED is used as a random number seed.)

/dev/random reads random numbers byte by byte, but these are not true random numbers. They are "the output of a CSPRNG initialized with entropy." Once initialized with entropy, they are deterministic unless they are periodically re-seeded (up to 10 times per second) with entropy from multiple sources. Therefore, a new seed is obtained each time using RDSEED from a hardware entropy source.

"True random numbers" have a different definition from "perfectly random numbers."

* True random numbers are, in principle, unpredictable and truly disordered random numbers. They are used in contrast to pseudo-random numbers generated arithmetically by computers. Physical random numbers that utilize quantum behavior, such as the decay of radioactive elements, are known. True random numbers. - From Shogakukan's Digital Daijisen.

* Perfectly random numbers refer to sequences of numbers that occur in a completely random order, and are also called ideal random numbers. They can only be handled probabilistically. - Search Labs | AI.

Although the definitions differ, it's acceptable to treat true random numbers as perfectly random numbers and handle them similarly.

Perfectly random numbers exhibit Jungian synchronicity (strange coincidences beyond causality). Physically speaking, this is similar to the EPR paradox becoming EPR correlation. Experiments suggest that Quantum Brain Dynamics interferes with other Quantum Dynamics, and environmental noise is influenced by this, making it difficult or impossible to generate them in the real world. Alternatively, they might be entirely random. Whether true random numbers are perfectly random or not has two answers: yes or no. In Christianity, the Archangel Michael is said to control chance, and this is currently being scientifically investigated.

The method for generating "mathematically perfect random numbers (true random numbers)" is considered fundamentally impossible through mathematics alone (because mathematical algorithms are deterministic), and has not yet been found. However, one day, a genius may appear, encompassing infinity and achieving this.

### Method Description

rand(n) returns a true random number within the range of n*8-bit positive integers.

rand_f(n) practically returns a float-type random number between [0,1], but since the distribution is not continuous like real numbers, it is no longer a true random number.

randomint(k,n) practically returns a random integer between 0 and k-1, but since it performs a modulo calculation, it is no longer a true random number.

```rdseed.c
/*
* rdseed.c — Extracts hardware entropy using the CPU's RDSEED instruction.
* Compilation (FreeBSD/clang, Linux/gcc common):
* cc -O2 -mrdseed -shared -fPIC -o librdseed.so rdseed.c
* Requires an RDSEED-compatible CPU (Intel Broadwell or later / AMD Zen or later).

*/
#include <immintrin.h>
#include <stdint.h>
/* Returns 1 on success, 0 if entropy is not prepared (=retry required). */
int rdseed64(uint64_t *out){
return _rdseed64_step((unsigned long long *)out);
}
```
Compile and create a library
```
cc -O2 -mrdseed -shared -fPIC -o librdseed.so rdseed.c
```
```truerand.py
#!/usr/bin/env python3
#
# truerand.py
# A true random number module that directly subtracts hardware entropy from the CPU's RDSEED instruction.
# It obtains a new entropy source byte by byte, without going through /dev/random(Fortuna).

# Requirements: An RDSEED-compatible CPU and a compiled librdseed.so file in the same directory.

# cc -O2 -mrdseed -shared -fPIC -o librdseed.so rdseed.c
#
import os
import ctypes

# --- Loading the RDSEED stub ---------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_lib = ctypes.CDLL(os.path.join(_here, "librdseed.so"))
_lib.rdseed64.argtypes = [ctypes.POINTER(ctypes.c_uint64)]
_lib.rdseed64.restype = ctypes.c_int

_RDSEED_RETRY = 1000 # RDSEED can temporarily fail, so set a retry limit

def _rdseed64():
"""Gets and returns one 64-bit hardware entropy using RDSEED."""
v = ctypes.c_uint64()
for _ in range(_RDSEED_RETRY):
if _lib.rdseed64(ctypes.byref(v)):
return v.value
raise RuntimeError("RDSEED failed repeatedly (hardware entropy depletion?)")

# Returns RAND_MAX of n bytes
def rand_max(n):
v = 0
for _ in range(n):
v = v*256 + 0xff
return v

# Returns a true random number (positive integer) of n bytes. Each byte is newly obtained from RDSEED.

def rand(n):
r = 0
for _ in range(n):
b = _rdseed64() & 0xff # Subtract from the entropy source each time
r = r*256 + b
return r

# Real random number in the range [0,1] (not strictly a true random number due to division)
def rand_f(n):
return rand(n) / rand_max(n)

# Integer random number between 0 and k-1 (not strictly a true random number due to remainder)
def randomint(k, n):
return rand(n) % k

if __name__ == "__main__":
b = 8
times = 20
print(f"{b*8}-bit positive true integer random number")
for _ in range(times):
print(rand(b), end=" ")
print("\nReal random number in the range [0,1]")
for _ in range(times):
print(rand_f(b), end=" ")
print("\nRandom integer between 0 and 99")
for _ in range(times):
print(randomint(100, b), end=" ")
print("")
```
# Execution result
```
% truerand.py
64-bit positive true integer random number
7593683692756404560 1137002372603596603 15790170822563052133 15398564476323138863 5666431897510622232 14727313056768347926 1591286415691868933 13756589528406737812 14017529931204693033 6126976806754524406 9625760106799710579 10221137030372070039 5789631471258037124 15844850515166960795 16310560720210454887 584665298658331905 11747899575069696907 17623763738758574929 2856509978569915829 7845507258779463291
Real random numbers in the range [0,1]
0.9971038511422857 0.04623809284437578 0.25208883991654213 0.23197559278871627 0.21992506030041897 0.062286248874933114 0.972354488288027 0.9724443108477789 0.6121628351627036 0.9760755436977876 0.2878544810907126 0.6180388833588414 0.8617915343869584 0.38774012248377726 0.7124578572583314 0.20837745592535706 0.8668496736230473 0.5165770706713765 0.40389838880267426 0.5204816417932834
Random integers from 0 to 99
62 75 92 2 90 7 97 96 96 59 23 14 61 55 12 94 88 17 13 53

```
