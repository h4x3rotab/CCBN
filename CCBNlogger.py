#logging code for CCBN simulator

import os
import time
from param import * # get same config as simulator

# ===============================================================

def initialize (test_state_list):
    global filename
    global logtxt
    global logcsv
    global out
    global outcsv
    global start
    start=time.time()
    time_stamp=str(start)
    print(DATAFOLDER)
    if not os.path.exists(DATAFOLDER):
        os.mkdir(DATAFOLDER)
    targetpath = os.path.normpath(DATAFOLDER + "/" + time_stamp)
    if not os.path.exists(targetpath):
        os.mkdir(targetpath)
    filename = os.path.normpath(targetpath + "/master")
    logtxt = open(filename + ".txt","w")
    logcsv = open(filename + ".csv","w")
    out = ("Output file: " + str(filename) + " in txt and csv format.\n\n"
            + "Attack hashpower multiples: " + str(MAC_POWERS)
            + "\n (first is mainchain post-attack power)" + "\n"
            + "Notarychain blocktime targets: " + str(NOC_TARGETS) + "\n"
            + "CCBN weighting powers: " + str(NOTE_WEIGHTS) + "\n"
            + "Confirmation requirement: " + str(CONFIRMATIONS) + "\n"
            + "Max block depth per run: " + str(BLOCKS_PER_RUN)  + "  "
            + "Simulation Runs: " + str(SIMRUNS) + "\n")
    logtxt.write(out)
    print(out)
    out = ("Detail Logging: " + str(DETAIL_LOGGING) + 
        "  Paired Analysis: " + str(TEST_PAIRS) +
        "\nMainchain Seeds: " + str(MAC_SEEDS) +
        "\nNotarychain Seeds:" + str(NOC_SEEDS) + "\n")
    logtxt.write(out + "\n")
    print(out)
    outcsv = "AttHash, Conf, Weight, NChain, Defeats, Defeat%, MDepth"
    for x in range(BLOCKS_PER_RUN + 1):
        outcsv += "," + str(x)
    logcsv.write(outcsv + "\n")
    if (DETAIL_LOGGING):
        for test in test_state_list[MAIN_COUNT::]: # skips the mainchain, iterates the tests
            myfilename = os.path.normpath(targetpath +"/"+ test[FILENAME])
            test[FILEOBJECT] = open(myfilename + ".txt","w")
        for test in test_state_list[MAIN_COUNT::]: # skips the mainchain, iterates the tests
            test[FILEOBJECT].write("Run, FailHeight, FailWeight (0 = no failure)\n")
    print("===================================================================")
    print("=                             STARTING                            =")
    print("===================================================================")
    out = "Start: " + str(start)
    logtxt.write(out + "\n")
    print(out)

def progress_update (run_counter):
    start
    now=time.time()
    done=run_counter/SIMRUNS
    elapsed=now-start
    print(run_counter,"runs,",int(elapsed),"seconds elapsed, approx",
            int(elapsed/done-elapsed),"to go (",int((elapsed/done-elapsed)/60),
            "minutes or %.2f" % ((elapsed/done-elapsed)/(60*60)),
            "hours or %.2f" % ((elapsed/done-elapsed)/(24*60*60)),"days.)\n")
           
def detail_log (run_counter, height, test_state_list):
    # ==================== FIXIT ==========================
    for test in test_state_list[MAIN_COUNT::]: # skips the mainchain, iterates the tests
        test[FILEOBJECT].write(
        str(run_counter) + ", " +
        str(height) + ", " +
        str(test[FAILED]) + "\n")


def status_output (test_state_list, run_counter):
    # ==================== FIXIT ==========================
    out = ("\n------------------------------------------------------\n"
            + "Sim Runs: " + str(run_counter) + " out of "
            + str(SIMRUNS) + ", " + str(run_counter/SIMRUNS) + "\n")
    print(out) 
    logtxt.write(out + "\n")
    for test in test_state_list[MAIN_COUNT::]: # skips the mainchain, iterates the tests
    # we assume that any run will eventually be defeated, and set the final
    # column with the remaining undefeated runs. This avoids a falsely low
    # average and avoids division by zero.
        defeats=sum(test[FAIL_DEPTH])
        undefeated = run_counter - defeats
        printlist = test[FAIL_DEPTH].copy() # temp copy of fail dpeth list
        printlist.append(undefeated) # add final field with remainder
        weightedsumdefeats = 0
        for x in range(BLOCKS_PER_RUN + 1):
            weightedsumdefeats += (x * printlist[x])
        meandepth = weightedsumdefeats/run_counter
        out = ("Attack Hash x " + str(MAC_POWERS[test[MAC_X]]) 
            + ", Notarychain: "+ str(NOC_TARGETS[test[NOC_X]]) 
            +", Confirmations: " + str(CONFIRMATIONS)
            + ", CCBN Weight: " + str(NOTE_WEIGHTS[test[WEIGHT_X]])+ "\n" 
            + str(defeats) + " defeat(s) out of " + str(run_counter) + ", "
            + str(defeats/run_counter) + "\n" + "Mean defeat depth " 
            + str(meandepth) + "; full list:\n"
            + str(printlist) + "\n") 
        print(out) 
        logtxt.write(out + "\n")
    logtxt.flush()
    if (DETAIL_LOGGING):
        for test in test_state_list[MAIN_COUNT::]: # skips the mainchain, iterates the tests
            test[FILEOBJECT].flush()

def final_output (test_state_list, test_pairs):
    out = ("\n=======================================================\n"
        + "\nFinal Chainstates After " + str(SIMRUNS) + " runs:")
    print(out) 
    logtxt.write(out + "\n")
    # ==================== FIXIT ==========================
    for test in test_state_list[MAIN_COUNT::]:
        # we assume that any run will eventually be defeated, and set the final
        # column with the remaining undefeated runs. This avoids a falsely low
        # average and avoids division by zero.
        defeats=sum(test[FAIL_DEPTH])
        undefeated = SIMRUNS - defeats
        test[FAIL_DEPTH][BLOCKS_PER_RUN] = undefeated
        weightedsumdefeats=0
        for x in range(BLOCKS_PER_RUN + 1):
            weightedsumdefeats += (x * test[FAIL_DEPTH][x])
        meandepth = weightedsumdefeats/SIMRUNS
        out = ("Attack Hash x " + str(MAC_POWERS[test[MAC_X]]) 
            + ", Notarychain: "+ str(NOC_TARGETS[test[NOC_X]]) 
            +", Confirmations: " + str(CONFIRMATIONS)
            + ", CCBN Weight: " + str(NOTE_WEIGHTS[test[WEIGHT_X]])+ "\n" 
            + str(defeats) + " defeat(s) out of " + str(SIMRUNS) + ", "
            + str(defeats/SIMRUNS) + "\n" + "Mean defeat depth " 
            + str(meandepth) + "; full list:\n"
            + str(test[FAIL_DEPTH]) + "\n")
        outcsv = (str(MAC_POWERS[test[MAC_X]]) + ", "
            + str(CONFIRMATIONS)+", "+ str(NOTE_WEIGHTS[test[WEIGHT_X]]) 
            + ", "+str(NOC_TARGETS[test[NOC_X]])
            + ", "+str(defeats)+", "
            + str(defeats/SIMRUNS)
            + ", "+str(weightedsumdefeats/SIMRUNS) + ", "
            + str(test[FAIL_DEPTH]).strip('[]'))
        print(out)
        logtxt.write(out + "\n")
        logcsv.write(outcsv + "\n")
    for pair in test_pairs:
        defeats=sum(pair[PAIR_FAIL_DEPTH])
        undefeated = SIMRUNS - defeats
        pair[PAIR_FAIL_DEPTH][BLOCKS_PER_RUN] = undefeated
        weightedsumdefeats=0
        for x in range(BLOCKS_PER_RUN + 1):
            weightedsumdefeats += (x * pair[PAIR_FAIL_DEPTH][x])
        meandepth = weightedsumdefeats/SIMRUNS
        out = (str(pair[TEST1_FILENAME])+" & "+str(pair[TEST2_FILENAME])+"\n" 
            + str(defeats) + " defeat(s) out of " + str(SIMRUNS) + ", "
            + str(defeats/SIMRUNS) + "\n" + "Mean defeat depth " 
            + str(meandepth) + "; full list:\n"
            + str(pair[PAIR_FAIL_DEPTH]) + "\n")
        outcsv = (str(pair[TEST1_FILENAME])+ ",,"+str(pair[TEST2_FILENAME])
            + ",,"+str(defeats)+", " + str(defeats/SIMRUNS)
            + ", "+str(weightedsumdefeats/SIMRUNS) + ", "
            + str(pair[PAIR_FAIL_DEPTH]).strip('[]'))
        print(out)
        logtxt.write(out + "\n")
        logcsv.write(outcsv + "\n")
    outcsv = ("\n\nOutput file: " + str(filename) + " in txt and csv format.\n\n"
        + str(MAC_POWERS) + ", Attack hashpower multiples" 
        + "\n (first is mainchain post-attack power)\n"
        + str(NOC_TARGETS) + ", Notarychain blocktime targets\n"
        + str(NOTE_WEIGHTS) + ", CCBN weighting powers\n"
        + str(CONFIRMATIONS) + ", Confirmation requirement\n"
        + str(BLOCKS_PER_RUN) + ", Max block depth per run\n"
        + str(SIMRUNS) + ", Simulation Runs\n"
        + str(DETAIL_LOGGING) + ", Detail Logging\n"  
        + str(TEST_PAIRS) + ", Paired Analysis\n" 
        + str(MAC_SEEDS) + ",Mainchain Seeds\n" 
        + str(NOC_SEEDS) + ",Notarychain Seeds\n"
        )
    logcsv.write(outcsv)

    print("===================================================================")
    print("=                            FINISHED                             =")
    print("===================================================================")

    # ============================================================================
    
    logtxt.write("\n")
    stop = time.time()
    out = ("\n\nStop: " + str(stop) + " Elapsed: " + str(stop-start) + ", " 
        + str(SIMRUNS) + " simulation runs, average "
        + str((stop-start)/SIMRUNS) + " seconds per run.\n"
        + "Output file: " + str(filename) + " in txt and csv format.\n")
    logtxt.write(out + "\n")
    print(out)
    # ==================== FIXIT ==========================
    if (DETAIL_LOGGING):
        for test in test_state_list[MAIN_COUNT::]: # skips the mainchain, iterates the tests
            test[FILEOBJECT].close()
    logtxt.close()
    logcsv.close()
