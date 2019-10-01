from param import *
from CCBNdefs import *
import os
import CCBNlogger
import random
import math


CCBNlogger.initialize(test_state_list)
print("Run started.")
run_counter = 0
# ============================================================================
#  SIMULATION RUN START - PREP AND MAINCHAIN RUN-IN
# ============================================================================
while run_counter < SIMRUNS:
    resets_per_run(run_counter) # RESET PER-RUN VARIABLES
    ts = 1       
    live_tests = TEST_COUNT

    # chain prep: warmup before DAA activated
    while mac_curr_len[0] < 45: # ensure this is long enough to seed the DAA
        if mac_random[MAINCHAIN].random() < mac_curr_diff[MAINCHAIN]:
           mac_list[MAINCHAIN].append([
                   ts,
                   MAIN_TARGET,
                   ts-mac_list[MAINCHAIN][mac_curr_len[0]-1][0]])
           mac_curr_len[0] += 1
        ts += 1

    # activate DAA and continue run-in to allow time for full "normal" 
    # variance to be established - for BTG, adding 
    # blocks = 2 x DAA window (2*45) is sufficient
    # note: to change run-in length, MUST change RUN_IN constant in param.py
    while mac_curr_len[0] < 135:
        if mac_random[MAINCHAIN].random() < mac_curr_diff[MAINCHAIN]:
            new_target = BTGDAA(mac_list[MAINCHAIN],mac_curr_len[0])
            mac_list[MAINCHAIN].append([
                    ts,
                    new_target,
                    (ts-mac_list[MAINCHAIN][mac_curr_len[0]-1][0])])
            mac_curr_len[0] += 1
            mac_curr_diff[MAINCHAIN]=1/new_target
        ts += 1

# run-in is complete; fork mainchain for attack chains
    for mac in range(1,MAC_COUNT):
        mac_list.append(mac_list[MAINCHAIN].copy())
        mac_curr_len[mac]=mac_curr_len[MAINCHAIN]
        mac_curr_diff[mac]=mac_curr_diff[MAINCHAIN]
        mac_random[mac].seed(MAC_SEEDS[mac] + run_counter)
        mac_recording_queue.append([])
        for noc in range(NOC_COUNT):
            mac_recording_queue[mac].append([])
    ffb = mac_curr_len[0] # index of first forked block
    attack_broadcast = RUN_IN + CONFIRMATIONS
    for noc in range(NOC_COUNT): 
        noc_list[noc][0] = ts # this should not matter, block[0] never used
    # attack begins at fork; we assume double-spend deposit is made in same block
    # (this is best-case scenario for attacker)
# ============================================================================
# BEGIN MAIN SIMULATION LOOPS
# ============================================================================
#  first while loop: 
#    BEFORE ANY ATTACK IS BROADCAST
#  while blocks < Confirmation requirement, no attack has beeen
#  broadcast: therefore failure is impossible, and weights do not
#  need to be calculated/compared yet. Mainchain is being notarized,
#  attack chains are not notarized
# ============================================================================
    while mac_curr_len[0] < attack_broadcast:
        # tick all notarychains ============================================
        tick_nocs_pre_broadcast(ts) # find blocks & record notarizations
        # tick all mainchains being compared ================================== 
        for mac in range (MAC_COUNT):
            if mac_random[mac].random() < mac_curr_diff[mac]:
                # block was found: add block to the chain
                block_num = mac_curr_len[mac]
                new_target = BTGDAA(mac_list[mac],block_num)
                block = ([ts,
                        new_target,
                        (ts-mac_list[mac][block_num-1][0])]
                        + blank_notes)
                mac_list[mac].append(block)
                # add block to appropriate notarization recording queues
                for noc in range(NOC_COUNT):
                    mac_recording_queue[mac][noc].append(block_num)
                mac_curr_len[mac] = block_num + 1
                mac_curr_diff[mac] = (1-(1-1/new_target)**MAC_POWERS[mac])
        ts += 1
        
# after here, we've met the CONFIRMATIONS required
# attack blocks can be released & begin getting notraized, so
# everything gets queued for notarization. Also, the DN_block
# will likely be the next notarycahin block found, so we check
# weights and notarychain metering will aply
# 
# ============================================================================
#  middle while loop:
#    after CONFIRMATIONS have been met and FIRST ATTACK IS BROADCAST 
#      (but possibly not all attacks have been broadcast)
#    must find dn_block for each chain where attack has been broadcast
#    some test configs subject to failure; begin calculating notarychain
#    weights as necessary to compare to mainchain
# ============================================================================
#
    DN_count = TEST_COUNT
    while DN_count:
        # tick all notarychains ============================================
        tick_nocs(ts) # find blocks & record notarizations
        # check each attack test for first recording & capture in DN_BLOCK
        for test in test_state_list[MAIN_COUNT::]:
            dn_block = test[DN_BLOCK]
            if not dn_block:
                mac = test[MAC_X]
                if mac_curr_len[mac]>ffb:
                    dn_block = mac_list[mac][ffb][test[NOC_X]+3]
                if dn_block: 
                    test[DN_BLOCK] = dn_block
                    DN_count -= 1
        # tick all mainchains being compared ================================== 
        for mac in range (MAC_COUNT): 
            if mac_random[mac].random() < mac_curr_diff[mac]:
                # block was found: add block to the chain
                new_target = BTGDAA(mac_list[mac],mac_curr_len[mac])
                block = ([ts,
                        new_target,
                        (ts-mac_list[mac][mac_curr_len[mac]-1][0])]
                        + blank_notes)
                mac_list[mac].append(block)
                # add block to appropriate notarization recording queues
                for noc in range(NOC_COUNT):
                    mac_recording_queue[mac][noc].append(mac_curr_len[mac])
                # update length and Difficulty
                mac_curr_len[mac] += 1
                mac_curr_diff[mac] = (1-(1-1/new_target)**MAC_POWERS[mac])
                # check for potential reorg & check weights
                if mac > MAINCHAIN: # if this is an attack, check lengths
                    if mac_curr_len[mac] > mac_curr_len[MAINCHAIN]:
                    # if attack chain > mainchain, re-org is possible, 
                    # must check weights for all tests using this mac
                        for test in test_state_list[mac*MAIN_COUNT:(mac+1)*MAIN_COUNT]:
                            if not test[FAILED]: # skip tests that failed already
                                main_weight = calc_weight (
                                    mac_list[MAINCHAIN],
                                    mac_curr_len[MAINCHAIN],
                                    ffb,
                                    test[NOC_X],
                                    test[DN_BLOCK],
                                    noc_curr_len[test[NOC_X]],
                                    NOTE_WEIGHTS[test[WEIGHT_X]])
                                attack_weight = calc_weight (
                                        mac_list[mac],
                                        mac_curr_len[mac],
                                        ffb,
                                        test[NOC_X],
                                        test[DN_BLOCK],
                                        noc_curr_len[test[NOC_X]],
                                        NOTE_WEIGHTS[test[WEIGHT_X]])
                                if attack_weight > main_weight:
                                    test[FAILED] = attack_weight
                                    depth = mac_curr_len[MAINCHAIN]-ffb
                                    test[FAIL_DEPTH][mac_curr_len[MAINCHAIN]-ffb] += 1
                                    live_tests -= 1
                                    for pair in test[PAIRLIST]:
                                        pair[PAIR_FAILED]+=1
                                        if pair[PAIR_FAILED]==2:
                                            pair[PAIR_FAIL_DEPTH][depth] += 1
        ts +=1
        # 1 SECOND HAS PASSED; check for live tests remaining
        if live_tests == 0: break # jump to next loop if all have failed
        # end while loop
#
# ============================================================================
#  last while loop:
#    after AFTER ALL ATTACKS HAVE BEEN BROADCAST and dn_block is already set
#  any test config can fail any time; must re-calc weights
#  and compare to mainchain each time
# ============================================================================
#
    while mac_curr_len[0] < SIMRUN_BLOCK_COUNT:
        # tick all notarychains ============================================
        tick_nocs(ts) # find noc blocks & record notarization in mains
        # tick all mainchains being compared ================================== 
        for mac in range (MAC_COUNT): 
            if mac_random[mac].random() < mac_curr_diff[mac]:
                # block was found: add block to the chain
                new_target = BTGDAA(mac_list[mac],mac_curr_len[mac])
                block = ([ts,
                        new_target,
                        (ts-mac_list[mac][mac_curr_len[mac]-1][0])]
                        + blank_notes)
                mac_list[mac].append(block)
                # add block to appropriate notarization recording queues
                for noc in range(NOC_COUNT):
                    mac_recording_queue[mac][noc].append(mac_curr_len[mac])
                # update length and Difficulty
                mac_curr_len[mac] += 1
                mac_curr_diff[mac] = (1-(1-1/new_target)**MAC_POWERS[mac])
                # check for potential reorg & check weights
                if mac > MAINCHAIN: # if this is an attack, check lengths
                    if mac_curr_len[mac] > mac_curr_len[MAINCHAIN]:
                    # if attack chain > mainchain, re-org is possible, 
                    # must check weights for all tests using this mac
                        for test in test_state_list[mac*MAIN_COUNT:(mac+1)*MAIN_COUNT]:
                            if not test[FAILED]: # skip tests that failed already
                                main_weight = calc_weight (
                                    mac_list[MAINCHAIN],
                                    mac_curr_len[MAINCHAIN],
                                    ffb,
                                    test[NOC_X],
                                    test[DN_BLOCK],
                                    noc_curr_len[test[NOC_X]],
                                    NOTE_WEIGHTS[test[WEIGHT_X]])
                                attack_weight = calc_weight (
                                        mac_list[mac],
                                        mac_curr_len[mac],
                                        ffb,
                                        test[NOC_X],
                                        test[DN_BLOCK],
                                        noc_curr_len[test[NOC_X]],
                                        NOTE_WEIGHTS[test[WEIGHT_X]])
                                if attack_weight > main_weight:
                                    test[FAILED] = attack_weight
                                    depth = mac_curr_len[MAINCHAIN]-ffb
                                    test[FAIL_DEPTH][mac_curr_len[MAINCHAIN]-ffb] += 1
                                    live_tests -= 1
                                    for pair in test[PAIRLIST]:
                                        pair[PAIR_FAILED]+=1
                                        if pair[PAIR_FAILED]==2:
                                            pair[PAIR_FAIL_DEPTH][depth] += 1
        ts +=1
        # 1 SECOND HAS PASSED; check for live tests remaining
        if live_tests == 0: break # jump to next run if all have failed
        # end while loop
    run_counter +=1
    # THIS RUN FINISHED; display timing info & estimates, RECORD OUTPUT
    # LOG FAIL_DEPTH FOR EACH TEST
    if run_counter%STATUS_INTERVAL == 0:
        CCBNlogger.progress_update(run_counter)
    if run_counter%LOG_INTERVAL == 0:
        CCBNlogger.status_output(test_state_list, run_counter)
    if DETAIL_LOGGING:
        CCBNlogger.detail_log(run_counter, (mac_curr_len[0]-RUN_IN), test_state_list)
CCBNlogger.final_output(test_state_list, test_pairs)

#=============================================================================
#  EXECUTION GOES BACK FOR NEXT RUN UNTIL run_counter > SIMRUNS
#  OTHERWISE, ALL RUNS FINISHED
#============================================================================= 
