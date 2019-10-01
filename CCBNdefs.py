# Module for CCBNsim.py
# BTG LWMA - as configured for Bitcoin Gold after block 536200
from param import *
import random
import math
import os
from itertools import combinations

# ============================================================================
# Set runtime parameters in param.py to set sim scope

ffb = 0 # first forked block

mac_list = [] # list of blockchains used for notarychains (nocs)
    # mac_list is a list of attack chains
    # each mainchain (mac) is a list of blocks
    # each block is a list:
    #   [timestamp, target, blocktime, n,n,n... ]
    #   timestamp in seconds (simulation counter)
    #   target is current block target
    #   blocktime is last block find time (makes DAA calc faster)
    #   n,n,n are notarizations, as many as there are notarychains to test
    # mac_list is a list of lists of lists 
mac_curr_len = [] # chain length list: blockheight (faster than calling len())
mac_curr_diff = [] # list of difficulties
mac_random = [] # random generator object for this attack
mac_recording_queue = [] # queue of notarizations awaiting recording
for mac in range(MAC_COUNT):
    mac_list.append([])
    mac_curr_len.append(0)
    mac_curr_diff.append(0)
    mac_random.append(random.Random())
    mac_recording_queue.append([])
    for noc in range(NOC_COUNT):
        mac_recording_queue[mac].append([])

blank_notes = [] # list of blank notarizations to add to a block pending notarization
# zeroes are replaced with notarycahin blockheights when the block is recorded
for noc in range(NOC_COUNT): 
    blank_notes.append(0)

noc_list = [] # list of blockchains used for notarychains (nocs)
    # noc_list is a list of notary chains
    # each notarycahin (noc) is a list of blocks
    # each block is a list:
    #   [timestamp, target, blocktime]
    #   timestamp in seconds (simulation counter)
    #   target is current block target
    #   blocktime is last block find time (makes DAA calc faster)
    # noc_list is a list of lists of lists
noc_curr_len = [] # chain length list: blockheight
noc_curr_diff = [] # quick-access list for difficulties
    # noc_curr-len, diff used to reduce repetitive slow calls
    # (calling list.len() is slow, double-dereference is slow)
noc_random = [] # random generator objects for this noc
for noc in range(NOC_COUNT):
    noc_list.append([])
    noc_curr_len.append(0)
    noc_curr_diff.append(0)
    noc_random.append(random.Random())

test_state_list = [] # records chain status per chain/test:
# each is a chainstate from the perspective of test configuration
# test configuration: a chainstate for each combo of:
#   mac (main chain)
#   noc (notary chain)
#   weight (CCBN weight power parameter)
# each is a list storing new chainstate info per run, but also stores a Depth list:
# Depth: fail depth counts across runs (Depth list is not reset between runs, so the 
# counts at each Depth accumulate
for mac in range(MAC_COUNT):
    for noc in range(NOC_COUNT):
        for note_weight in range(NOTE_WEIGHT_COUNT):
            # construct unique filename
            myfilename = (str(SIMRUNS) +"-"+
                    str(MAC_POWERS[0])+"-"+
                    str(MAC_POWERS[mac])+"-"+
                    str(NOC_TARGETS[noc])+"-"+
                    str(CONFIRMATIONS)+"-"+
                    str(NOTE_WEIGHTS[note_weight])
                    )
            # Find matching mainchain config to current config, if
            # possible, to save in test_state_list[x][MYMAIN]
            # as a quick reference to the matchin mainchain test state
            mymain=[]
            for test in test_state_list[0:MAIN_COUNT]:
                if ( 
                    (test[NOC_X] == noc) 
                        and
                    (test[WEIGHT_X] == note_weight) 
                    ):
                    mymain = test
                    break
            # all data prepared; create state and append to list
            this = ([mac, # MAC_X
                    noc,  # NOC_X
                    note_weight, # WEIGHT_X
                    0, # FAILED
                    0, # DN_BLOCK_TIME
                    [], # FAIL_DEPTH
                    mymain, # MYMAIN
                    myfilename, # FILENAME
                    0, # FILEOBJECT
                    [] # pairlist
                    ])
            for maxdepth in range(BLOCKS_PER_RUN+1):
                this[FAIL_DEPTH].append(0) # add buckets for all fail depths
            test_state_list.append(this)
# PARSING NOTES FOR test_state_list:
# test_state_list[:MAIN_COUNT:] <- this slice is only states for mainchains
#       there is one state for each parameter combo with mainchain
# test_state_list[MAIN_COUNT::] <- this slice is only states for attack chains
#       there is one state for each parameter combo for each attack chain
# test_state_list[mac*MAIN_COUNT:(mac+1)*MAIN_COUNT] <- alls states with same attack
#       one state for each parameter combo, but only for a single attack power

# test_pairs - aggregator for combined pairs of tests
# the combo fails if either fails
test_pairs = [] 
if (TEST_PAIRS) and (NOC_COUNT > 1):
    pairs = combinations(test_state_list[MAIN_COUNT::],2)
    for pair in pairs:
        if pair[0][MAC_X]==pair[1][MAC_X]:
            this = ([0, # PAIR_FAILED
                    [], # PAIR_FAIL_DEPTH
                    pair[0][FILENAME], # TEST1_FILENAME
                    pair[1][FILENAME], # TEST2_FILENAME
                    ])
            test_pairs.append(this)
            pair[0][PAIRLIST].append(this)
            pair[1][PAIRLIST].append(this)
            for maxdepth in range(BLOCKS_PER_RUN+1):
                this[PAIR_FAIL_DEPTH].append(0) # buckets for all fail depths


def resets_per_run(run_counter):
    # reset mainchains
    ffb = 0
    mac_list.clear()
    mac_list.append([])
    mac_list[MAINCHAIN].append([0,MAIN_TARGET,0]) # add genesis block
    mac_curr_len[MAINCHAIN] = 1 # chain length: blockheight
    mac_curr_diff[MAINCHAIN] = 1/MAIN_TARGET
    mac_random[MAINCHAIN].seed(MAC_SEEDS[MAINCHAIN] + run_counter)
    mac_recording_queue.clear()
    mac_recording_queue.append([])
    for noc in range(NOC_COUNT):
        mac_recording_queue[MAINCHAIN].append([])
    # reset notarychains
    for noc in range (NOC_COUNT):
        noc_list[noc].clear()
        noc_list[noc].append([0]) # dummy genesis block
        noc_curr_len[noc]=1
        noc_curr_diff[noc]=1/NOC_TARGETS[noc]
        noc_random[noc].seed(NOC_SEEDS[noc] + run_counter)
    # reset chainstates
    for test in (test_state_list):
        # MAC_X, NOC_X, CONF_X, WEIGHT_X do not change
        test[FAILED] = 0
        test[DN_BLOCK] = 0
        # FAIL_DEPTH array values are cumulative between runs
        # MYMAIN, FILENAME, FILEOBJECT, PAIRLIST do not change
    for pair in test_pairs: pair[PAIR_FAILED] = 0


def tick_nocs(ts):
    for noc in range(NOC_COUNT):
        if noc_random[noc].random() < noc_curr_diff[noc]:
            # block was found: add to notarychain
            noc_list[noc].append([
                ts
                #,NOC_TARGETS[noc]
                #,(ts-noc_list[noc][noc_curr_len[noc]-1][0])
                ])
            noc_curr_len[noc]+=1
            # record queued notes for this noc in all mainchains
            for mac in range (MAC_COUNT):
                if mac_recording_queue[mac][noc]:
                    for note in mac_recording_queue[mac][noc]:
                        mac_list[mac][note][noc+3]=noc_curr_len[noc]
                    mac_recording_queue[mac][noc].clear()

def tick_nocs_pre_broadcast(ts): # no notarizing for attack chains
    for noc in range(NOC_COUNT):
        if noc_random[noc].random() < noc_curr_diff[noc]:
            # block was found: add to notarychain
            noc_list[noc].append([
                ts
                #,NOC_TARGETS[noc]
                #,(ts-noc_list[noc][noc_curr_len[noc]-1][0])
                ])
            noc_curr_len[noc]+=1
            # record queued notes for this noc in mainchain only
            mac = MAINCHAIN
            if mac_recording_queue[mac][noc]:
                for note in mac_recording_queue[mac][noc]:
                    mac_list[mac][note][noc+3]=noc_curr_len[noc]
                mac_recording_queue[mac][noc].clear()

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

def calc_weight(chain, tip, ffb, noc, dn_block, noc_tip, note_weight):
# dn_block is the notarization blockheight where metering begins
# before dn_block, each notarization weighted on height in notarycahin
# after dn_block, heights are delayed and recognized based after 
#      blocks pass equal to Mean + 2 x Stand Deviation of mainchain
    chain_weight = 0
    note_record = 3 + noc # index of the notarization for this noc
    noc_target = NOC_TARGETS[noc]
    depth=0
    last_depth=0
    dn_block_depth = (noc_tip - dn_block + 1)
    n = 0 # metering counter
    for block in chain[ffb+1:tip]: 
        record = block[note_record]
        if record:
            depth = (noc_tip - record + 1)
            if record < dn_block: # before dn_block, recognize normally
                chain_weight += depth**note_weight
                continue
            elif last_depth == 0: # first note is at dn_block, recognize normally
                chain_weight += depth**note_weight
                last_depth = depth
                continue
            else: # otherwise, metering applies
                n += 1
                min_blocks_since_dn = BTG_MEAN_PLUS_2SD[n]//noc_target
                if dn_block_depth - depth < min_blocks_since_dn:
                    depth = dn_block_depth - min_blocks_since_dn
                if depth > 0:
                    chain_weight += depth**note_weight
                    last_depth = depth
                    continue
                else: 
                    break
    return int(chain_weight)

#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # =============================================================
# code below not in use

# calc_weight_naive - naive weighting formula
def calc_weight_naive(chain, tip, ffb, noc, dn_block, noc_tip, note_weight):
    chain_weight = 0
    note_record = 3 + noc # index of the notarization for this noc
    for block in chain[ffb:tip]:
        record = block[note_record]
        if record:
            depth = noc_tip - record + 1
            chain_weight += depth**note_weight
    return chain_weight

# calc_weight_delayed_recognition - naive weight with 1-block delayed recognition
# delayed recognition prevents abuse of CCBN for Selfish Mining with gamma=1
def calc_weight_delayed_recognition(chain, tip, ffb, noc, dn_block, noc_tip, note_weight):
    chain_weight = 0
    note_record = 3 + noc # index of the notarization for this noc
    for block in chain[ffb+1:tip]:
        record = block[note_record]
        if record:
            depth = noc_tip - record + 1
            chain_weight += depth**note_weight
    return chain_weight
    
# calc_weight_linear_metering weight with linear metering after delayed recognition
def calc_weight_linear_metering(chain, tip, ffb, noc, dn_block, noc_tip, note_weight):
# DNblock is the notariztion blockheight where metering begins
    chain_weight = 0
    note_record = 3 + noc # index of the notarization for this noc
    depth=0
    last_depth=0
    metered_pace=round((1.15*MAIN_TARGET)//NOC_TARGETS[noc])
    for block in chain[ffb+1:tip]: # before dn_block, recognize normally
        record = block[note_record]
        if record:
            depth = (noc_tip - record + 1)
            if record < dn_block: # before DN, recognize normally
                chain_weight += depth**note_weight
                continue
            elif last_depth == 0: # first note in dn_block, recognize normally
                chain_weight += depth**note_weight
                last_depth = depth
                continue
            else: # otherwise, metering applies
                if last_depth - depth < metered_pace:
                    depth = last_depth - metered_pace
                if depth > 0:
                    chain_weight += depth**note_weight
                    last_depth = depth
                    continue
                else: break
    return chain_weight
