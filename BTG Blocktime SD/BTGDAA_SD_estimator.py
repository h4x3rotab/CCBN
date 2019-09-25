import random
import math
import os
import time

reporting_interval = 10000
run_length = 100000000
log_depth = 256
BTG_theor_mean = 603.078
sim_start = time.time()
filename = "BTGDAA_SD_" + str(BTG_theor_mean) + "."+str(sim_start)+".txt"

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
    for i in range(tip - 45, tip):
        solvetime = chain[i][2]
        j += 1
        if solvetime < 3600:
            t += j * solvetime
        else: # catch aberrant long solvetime > 6*T and squelch to 6*T
            t += j * 3600
        sum_of_inv_diffs += (1/chain[i][1])

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

BTG_theor_mean_list = []
BTG_theor_dev = []
print("\nTheoretical Standard Deviation by Exponential distribution for mean of "
    +str(BTG_theor_mean) +"\n  Logging in "+filename+"\n\nInitializing...\n")
for i in range (log_depth):
    depth = i + 1
    # expected means, based on known block time average:
    BTG_theor_mean_list.append(BTG_theor_mean * (depth))
    # expected SD, based on Exponential Distribution (not accurate for BTG)
    BTG_theor_dev.append(math.sqrt(depth * BTG_theor_mean**2))
    # print("{0:d}, {1:.3f}, {2:.3f}".format(depth, BTG_theor_mean_list[i], BTG_theor_dev[i]))

BTG = [] # simulated blockchain
BTG_tip = 0
BTG_diff = 1/BTG_theor_mean
BTG_time = 0
BTG_mean = BTG_theor_mean # expected value
BTG_solvetime_list = [] # list of total blocktime last n blocks
BTG_var_list = [] # cumulative variance for last n blocks
BTG_dev_list = [] # standard deviation for last n blocks
for i in range (log_depth): # initialize tracking arrays
    BTG_solvetime_list.append(i)
    BTG_var_list.append(0)
    BTG_dev_list.append(0)

BTG_target = round(BTG_theor_mean) 
for seeding in range (45): # need 45 block window before activating DAA
    BTG_time += BTG_target
    BTG.append([BTG_time,BTG_target,BTG_target])
    BTG_tip += 1

# thorough run-in for full normal variance to set in
# 3x 45 block averaging window is probably adequate for simulation, but
# each 45 blocks have a faint echo of the prior 45 blocks, so 10x 45 is
# extra-safe for estimating the true variance & SD
for blocks in range (log_depth + 10*45):
    #find one BTG block
    found = False
    while found == False:
        if prng.random() < BTG_diff:
            found = True
            BTG_target = BTGDAA(BTG,BTG_tip)
            BTG.append([BTG_time, BTG_target, BTG_time - BTG[BTG_tip - 1][0]])
            BTG_tip += 1
            BTG_diff = 1/BTG_target
        BTG_time +=1
BTG_start = BTG_time # capturing current simulated time; only used for calculating
# the mean block time as a sanity check for the sim; should approach BTG_theor_mean

# get initial time lists
for depth in range (log_depth):
    BTG_solvetime_list[depth] = BTG[BTG_tip-1][0] - BTG[BTG_tip-1-(depth+1)][0]

#=====================================
# begin simulation and data collection
#=====================================

for blocks in range (1,run_length+1):
    # find one BTG block
    found = False
    solvetime = 0
    while found == False:
        if prng.random() < BTG_diff:
            # found one!
            found = True
            BTG_target = BTGDAA(BTG,BTG_tip)
            solvetime = BTG_time - BTG[BTG_tip-1][0]
            BTG.append([BTG_time, BTG_target, solvetime])
            BTG_tip += 1
            BTG_diff = 1/BTG_target
        BTG_time +=1
    for depth in range (log_depth-1, 0, -1):
        # set solvetimes to prior for n > 0
        BTG_solvetime_list[depth] = BTG_solvetime_list[depth-1] + solvetime
        # add to cumulative variances for n > 0
        BTG_var_list[depth] += (BTG_theor_mean_list[depth] 
            - BTG_solvetime_list[depth])**2
    BTG_solvetime_list[0] = solvetime # set solvetime to current for n = 0
    BTG_var_list[0] += (BTG_theor_mean_list[0] - BTG_solvetime_list[0])**2
    
    # reporting
    if blocks % reporting_interval == 0 :
        # calc BTG Deviation & differences from standard Exponential
        for depth in range (log_depth-1, 0, -1):
            BTG_dev_list[depth] = math.sqrt(BTG_var_list[depth]/(blocks-1))
        BTG_dev_list[0] = math.sqrt(BTG_var_list[0]/(blocks-1))
        sim_stop=time.time()
        BTG_diff_to_exp_list = []
        for depth in range (log_depth):
            BTG_diff_to_exp_list.append(BTG_dev_list[depth]-BTG_theor_dev[depth])
        
        # output
        logtxt = open(filename,"w")
        logtxt.write("Variances calculated using BTG Mean: "
            + str(BTG_theor_mean) + "\nBlocks Simulated: " + str(blocks)
            + "\nActual BTG mean block time in this run: " 
            + str((BTG_time-BTG_start)/(blocks))+"\n\n"
            )
        logtxt.write("Start: {} Stop: {} Elapsed: {}\n\n".format
            (sim_start, sim_stop, sim_stop-sim_start)
            )
        logtxt.write("Exponential Distribution versus actual Standard Deviation at Depth D\n\n  D, ExpSD, BTGSD, dExpvAct\n")
        for depth in range (log_depth):
            logtxt.write("{:>3}, {:f}, {:f}, {:f}\n".format(
                depth + 1,
                BTG_theor_dev[depth],
                BTG_dev_list[depth],
                BTG_diff_to_exp_list[depth]
                ))        
        print (str(blocks) + " of " + str(run_length) + 
            " blocks simulated, current mean block time " +
            str((BTG_time-BTG_start)/(blocks))
            )
        now = time.time()
        done = blocks/run_length
        elapsed = now - sim_start
        print ("{:.0f} seconds elapsed, approx {:.0f} to go ({:.1f} minutes or {:.2f} hours or {:.2f} days.)\n".
                format (elapsed,
                (elapsed/done-elapsed),
                (elapsed/done-elapsed)/60,
                (elapsed/done-elapsed)/(60*60),
                (elapsed/done-elapsed)/(24*60*60)
                )
                + "   Logging in "+filename+"\n"
                )
        # truncate chain to last 45 blocks to avoid consuming excess memory
        BTG = BTG[BTG_tip-45:BTG_tip] 
        BTG_tip = 45

#=============
# final output
#=============

sim_stop = time.time()
BTG_diff_to_exp_list = []
for depth in range (log_depth):
    BTG_diff_to_exp_list.append( BTG_dev_list[depth]-BTG_theor_dev[depth])

logtxt = open(filename,"w")
logtxt.write("Variances calculated using BTG Mean: "
    + str( BTG_theor_mean)+"\nBlocks Simulated: " + str(blocks)
    + "\nActual BTG mean block time in this run: " 
    + str((BTG_time-BTG_start)/(blocks))+"\n\n"
    )
logtxt.write("Start: {} Stop: {} Elapsed: {}\n\n".format
    (sim_start, sim_stop,sim_stop-sim_start)
    )
logtxt.write("Exponential Distribution versus actual Standard Deviation at Depth D\n\n  D, ExpSD, BTGSD, dExpvAct\n")
for depth in range (log_depth):
    logtxt.write("{:>3}, {:f}, {:f}, {:f}\n".format(
        depth + 1,
        BTG_theor_dev[depth],
        BTG_dev_list[depth],
        BTG_diff_to_exp_list[depth]
        ))        
print()

print("end")