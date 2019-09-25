import random
import json
import time

# fast-running simulation for long runs to find true mean block time

savefile = "BTGDAA_mean_progress.json"
logfile = "BTGDAA_mean_output.txt"
reporting_interval = 100000
run_length = 1000000000
if reporting_interval > run_length: reporting_interval = run_length

def BTGDAA(chain,tip): # Simulated BTG DAA after 2018, Aug 1 (v0.15.1)
    # chain[n] = list of blocks in form:
    #           [timestamp, target, solvetime]
    # tip - end point of the 45 blocks to use
    # returns the new diff target calculated at tip
    # new diff = adj * T * harmonic mean(N diffs) / LWMA(N solvetimes)
    # adj is a constant adjustment factor to hit the target solvetime
    # Target block solvetime, T, for BTG is 600 seconds
    # harmonic mean (45 diffs) = 45 / (sum of inverses of 45 diffs)
    # LWMA is the linearly weighted moving average of 45 prior solvetimes;
    # most recent weighted by 45, prior by 44, etc.

    sum_of_inv_diffs = 0 # harmonic mean denominator - sum of inverses of diffs
    t = 0 # linearly weighted sum of solvetimes for LWMA calculation
    j = 0
    for i in range(tip-45,tip):
        solvetime = chain[i][1]
        j += 1
        if solvetime < 3600:
            t += j * solvetime
        else: # catch aberrant long solvetime > 6*T and squelch to 6*T
            t += j * 3600
        sum_of_inv_diffs += (1/chain[i][0])

    if t < 2694: # = (N * (.9979751) * T) // 10
        # catch aberrant low linearly weighted sum of solvetimes
        t = 2694

    # LWMA(N solvetimes) = t / weighting = (t / 45*23)
    # harmonic_mean = 45/sum_of_inv_diffs
    # new target = adj * T * harmonic mean(N diffs) / LWMA(N solvetimes)
    # new_target = .99797509636 * 600 * (45/sum_of_inv_diffs) * (45*23/t)
    new_target = 27888414/(sum_of_inv_diffs*t)
    return new_target

prng = random.Random()
BTG_target = 603
BTG_diff = 1/600
BTG = []
BTG_tip = 0
BTG_blocks = 0
BTG_time = 0
prev_time = 0
first_time = True
main_remaining = run_length
elapsed = 0


try: # load from savefile
    with open(savefile,"r") as input_file:
            data = json.load(input_file)
    BTG_blocks = data[0]
    BTG_time = data[1]
    elapsed = data[2]
    BTG = data[3]
    main_remaining = run_length - BTG_blocks
    print("Loaded from file " + savefile)
    done = BTG_blocks/run_length
    print("\n" + str(BTG_blocks) + " " +
        str((BTG_time)/(BTG_blocks))
        )
    print(int(elapsed),"seconds elapsed, approx",
                int(elapsed/done-elapsed),"to go (",round((elapsed/done-elapsed)/60,1),
                "minutes or %.2f" % ((elapsed/done-elapsed)/(60*60)),
                "hours or %.2f" % ((elapsed/done-elapsed)/(24*60*60)),"days.)\n")
    print("Resuming:\n")
except: # if no savefile, initialize
    for seeding in range (45):
        BTG_time += BTG_target
        BTG.append([BTG_target,BTG_target])
        BTG_tip += 1
    prev_time = BTG_time
    # run in for full normal variance to set in
    for blocks in range (955):
        #find one BTG block
        found = False
        still_mining = True
        while still_mining: # looking for a block
            BTG_time +=1 # a second passes
            if prng.random() < BTG_diff: # did we find a block?
                # found a block!
                still_mining = False 
                BTG_target = BTGDAA(BTG,BTG_tip)
                BTG.append([BTG_target,BTG_time-prev_time])
                BTG_tip += 1
                BTG_diff = 1/BTG_target
                prev_time = BTG_time
    BTG = BTG[955:1000] # truncate to last 45 blocks
    BTG_blocks = 0
    BTG_time = 0
    elapsed = 0
    print("Initialized\nBeginning:\n")
BTG_tip = 45
prev_time = BTG_time


# begin data collection
while main_remaining:
    start = time.time()
    sub_remaining = reporting_interval
    while sub_remaining:
        still_mining = True
        #find one BTG block
        while still_mining: # looking for a block
            BTG_time +=1 # a second passes
            if prng.random() < BTG_diff: # did we find a block?
                # found block!
                still_mining = False 
                BTG_target = BTGDAA(BTG,BTG_tip)
                BTG.append([BTG_target,BTG_time-prev_time])
                BTG_tip += 1
                BTG_diff = 1/BTG_target
                prev_time = BTG_time
        main_remaining -= 1
        sub_remaining -= 1
    # truncate to last 45 blocks
    BTG_blocks += (BTG_tip-45)
    BTG = BTG[BTG_tip-45:BTG_tip] 
    BTG_tip = 45
    stop = time.time()
    elapsed += stop - start
    done = BTG_blocks/run_length
    print(str(BTG_blocks)+" " +
        str((BTG_time)/(BTG_blocks))
        )
    print(int(elapsed),"seconds elapsed, approx",
                int(elapsed/done-elapsed),"to go (",round((elapsed/done-elapsed)/60,1),
                "minutes or %.2f" % ((elapsed/done-elapsed)/(60*60)),
                "hours or %.2f" % ((elapsed/done-elapsed)/(24*60*60)),"days.)\n")
    with open(savefile,"w") as output_file:
        data = (BTG_blocks, BTG_time, elapsed, BTG)
        json.dump(data, output_file)

logtxt = open(logfile,"w")
logtxt.write("Blocks BTCmean BTGmean\n")
logtxt.write(str(BTG_blocks)+" " +
            str((BTG_time)/(BTG_blocks)) + "\n" + 
            str(data)
            )

print("end")