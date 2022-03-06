#
# Two processes incrementing a counter in parallel
#
# In this example we use the shared_lock=True parameter.
# UltraDict uses the atomics package internally for shared locking.
#
# This way of shared locking is save accross independent
# processes but it is slower than using the other built-in alternative:
# `multiprocessing.RLock()`.

import sys
sys.path.insert(0, '..')

from UltraDict import UltraDict

import multiprocessing

count = 100000

def run(name, target, x):
    # Connect to the existing ultra dict by its name
    d = UltraDict(name=name, shared_lock=True)
    for i in range(target): 
        # Adding 1 to the counter is unfortunately not an atomic operation in Python,
        # but UltraDict's shared lock comes to our resuce: We can simply reuse it.
        with d.lock:
            # Under the lock, we can safely read, modify and
            # write back any values in the shared dict
            d['counter'] += 1
            #print("counter: ", d['counter'], i, x)

if __name__ == '__main__':

    # No name provided, create a new dict with random name
    ultra = UltraDict(buffer_size=10_000, shared_lock=True, full_dump_size=10_000)
    ultra['some-key'] = 'some value'
    ultra['counter'] = 0

    # Our children will use the name to attach to the existing dict
    name = ultra.name

    #print(ultra)

    ctx = multiprocessing.get_context("spawn")

    p1 = ctx.Process(target=run, name="Process 1", args=[name, count//2, 1])
    p2 = ctx.Process(target=run, name="Process 2", args=[name, count//2, 2])

    # These processes should write more or less at the same time
    p1.start()
    p2.start()

    print ("Started 2 processes..")

    p1.join()
    p2.join()

    print ("Joined 2 processes")

    ultra.print_status()
    print(ultra)

    print("Counter: ", ultra['counter'], ' == ', count)