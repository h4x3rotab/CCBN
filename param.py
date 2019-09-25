# Runtime parameters for CCBNsim.py

#define sim scope 
SIMRUNS = 1000 # number of times to run a simulated attack and add to datatable
LOG_INTERVAL = 50 # freq of logfile updates (in sim runs) to capture stats before 
# during sim (set LOG_INTERVAL = SIMRUNS to skip updates)
STATUS_INTERVAL = 10 # freq of status/progress updates ( in sim runs) on console

DATAFOLDER = "var" # folder target for log files
BLOCKS_PER_RUN = 100 # how deep to run each attack, in mainchain blocks
    # attacks run for this many mainchain blocks, unless already defeated
    # if all simulated scenarios are defeated before 100 blocks pass, the
    # run stops and goes to the next run. As a result, even deep runs of
    # BLOCKS_PER_RUN = 1000 will be quick if the CCBN parameters are very weak
    # and the defense fails in the first 10 blocks. Conversely, if CCBN
    # params are strong, and the defense does not fail, the sim will run
    # out the full BLOCKS_PER_RUN for each run, taking more time - this is true
    # even if only one simulated scenario is strong. One "strong defense" 
    # scenario will make them all wait for the full depth, so be aware when
    # batching configurations to analyze

CONFIRMATIONS = 6 # confirmation depth requirement to test
# Attacker will delay start of notarization until confirmation is met
# This simulates attacking an exchange that waits for this many confirmations
MAC_POWERS = [.75,4] # main and attack chain hashpower multiples to test 
    # example: use 2 to simulate attack with 2X natural network haspower
    # note that elemnet 0 is mainchain
    # example: if mainchain power is expected to drop by 25% when an attacker
    # buys away all the "market" power, use element 0 = .75
    # [.5,2] tests when mainchain drops to half power while attacked by 2x normal
    # MAKE SURE you have at least as many MAC_SEEDS as MAC_POWERS!
NOC_TARGETS = [30,60] # Notarychain blocktimes targets
    # ETH = 20... RSK = 30... LTC = 150... BTC = 600
    # for notarycahins, sim assumes fixed difficulty and stable hashrate
    # MAKE SURE you have at least as many NOC_SEEDS as NOC_TARGETS!

NOTE_WEIGHTS = [2,3,4] # CCBN notarization weight powers to test

MAC_SEEDS = [0,1,2,3,4,5,6,7,8,9] # random seeds for mainchains
NOC_SEEDS = [20,21,22,23,24,25,26,27,28,29] # random seeds for notarychains
    # nth MAC_POWERS uses nth MAC_SEED, nth NOC uses nth NOC_SEED
    # never use same seed for two chains
    # if using > 10 MAC_POWERS or NOC_TARGETS, add extra seeds
    # if trying to replicate results, make sure entire config is
    # replicated, including correlation of seeds to chains


# Simulation speed considerations:
# SIMRUNS * BLOCKS_PER_RUN is the number of passes, runtime grows linearly
# Adding MAC_POWERS has large impact; each power is another blockchain to 
# run and track, including random check each second per chain
# Adding NOC_TARGETS also has large impact; there's mininmal tracking on a
# notarychain, but each additional chain requires an additional random check 
# per "second" to simulate block mining/creation
# Adding more NOTE_WEIGHTS and CONFIRMATIONS has minor impact; those
# just add a few extra calculations/storage each time a block is found, 
# HOWEVER, if the  NOTE_WEIGHTS & CONFIRMATIONS make the chain very safe, 
# runs will take longer as they are unlikely to fail, and so will run the 
# full BLOCKS_PER_RUN for each pass


# ============================================================================
#                       Make no changes below here
# ============================================================================

NOTE_WEIGHT_COUNT = len(NOTE_WEIGHTS) # number of weight power settings to test
MAC_COUNT = len(MAC_POWERS) # number of mainchains forks in the run
NOC_COUNT = len(NOC_TARGETS) # number of notarychains in the run
TEST_CONFIGS = MAC_COUNT * NOC_COUNT * NOTE_WEIGHT_COUNT
MAIN_COUNT = NOC_COUNT * NOTE_WEIGHT_COUNT
TEST_COUNT = (MAC_COUNT-1) * NOC_COUNT * NOTE_WEIGHT_COUNT

RUN_IN = 135 # number of blocks spent in initialization
    # (to create typical variance before beginning attack sim)
    # 3 x averaging window (3 * 45) is sufficient for BTG
    # this happens at the start of each simrun
SIMRUN_BLOCK_COUNT = BLOCKS_PER_RUN + RUN_IN

MAIN_TARGET = 603.078 # blocktime target for mainchain; BTG = 603.078
MAINCHAIN = 0 # when referring to index 0 of a list where 0 = mainchain

# Test State List
# test_state_list element constants for readability:
MAC_X = 0 # mainchain index (to MAC_POWERS)
NOC_X = 1 # notarychain index (to NOC_TARGETS)
WEIGHT_X = 2 # notarization weight index (to NOTE_WEIGHTS)
FAILED = 3 # flag if this config has been beaten
DN_BLOCK = 4 # the block with the first duplicate (attack) notarization
FAIL_DEPTH = 5 # list of defeat depths from all past runs
MYMAIN = 6 # reference to cs_list mainchain with same config as this
FILENAME = 7 # filename and fileobject only used if doing verbose per-test logging
FILEOBJECT = 8 # filename and fileobject only used if doing verbose per-test logging
PAIRLIST = 9

# Test Pairs
# test_pairs element constants for readability
PAIR_FAILED = 0
PAIR_FAIL_DEPTH = 1
TEST1_FILENAME = 2
TEST2_FILENAME = 3

# BTG Standard Deviation for a series of N blocks
BTG_MEAN_PLUS_2SD = [0,1837.2,2970.6,3963.3,4882.2,5753.5,6590.5,7401.3,8190.9,8963.2,9720.8,10465.7,11199.6,11923.8,12639.3,13347.1,14047.8,14742.3,15430.9,16114.3,16792.7,17466.7,18136.6,18802.5,19465.0,20124.0,20780.0,21433.1,22083.5,22731.3,23376.8,24020.0,24661.2,25300.4,25937.8,26573.5,27207.4,27839.9,28470.9,29100.5,29728.9,30356.0,30982.1,31607.0,32231.0,32854.1,33476.2,34097.4,34718.2,35338.0,35957.2,36575.6,37193.5,37810.7,38427.4,39043.4,39658.9,40273.9,40888.4,41502.4,42116.0,42729.1,43341.8,43954.1,44566.0,45177.6,45788.8,46399.7,47010.2,47620.5,48230.5,48840.2,49449.6,50058.9,50667.9,51276.6,51885.1,52493.5,53101.6,53709.6,54317.4,54925.1,55532.6,56140.0,56747.2,57354.2,57961.2,58568.0,59174.7,59781.4,60387.9,60994.3,61600.6,62206.8,62813.0,63419.0,64025.0,64630.8,65236.7,65842.4,66448.1,67053.7,67659.2,68264.6,68870.0,69475.3,70080.6,70685.9,71291.0,71896.2,72501.3,73106.3,73711.3,74316.3,74921.2,75526.1,76131.0,76735.8,77340.7,77945.4,78550.2,79154.9,79759.6,80364.3,80968.9,81573.6,82178.2,82782.8,83387.4,83992.0,84596.5,85201.1,85805.6,86410.1,87014.6,87619.1,88223.6,88828.0,89432.5,90037.0,90641.4,91245.8,91850.2,92454.6,93059.0,93663.4,94267.8,94872.1,95476.5,96080.8,96685.2,97289.6,97893.9,98498.3,99102.6,99706.9,100311.2,100915.5,101519.8,102124.0,102728.3,103332.6,103936.8,104541.1,105145.3,105749.6,106353.8,106958.0,107562.2,108166.5,108770.7,109374.9,109979.1,110583.3,111187.6,111791.8,112396.0,113000.2,113604.4,114208.7,114812.9,115417.2,116021.4,116625.7,117229.9,117834.1,118438.3,119042.5,119646.7,120250.9,120855.1,121459.3,122063.5,122667.7,123271.9,123876.1,124480.3,125084.5,125688.7,126292.9,126897.1,127501.3,128105.6,128709.8,129314.0,129918.2,130522.5,131126.7,131730.9,132335.1,132939.3,133543.4,134147.6,134751.8,135356.0,135960.2,136564.3,137168.5,137772.7,138376.9,138981.1,139585.3,140189.4,140793.6,141397.8,142002.0,142606.2,143210.4,143814.6,144418.8,145023.0,145627.2,146231.3,146835.5,147439.7,148043.9,148648.1,149252.3,149856.5,150460.6,151064.8,151669.0,152273.1,152877.3,153481.4,154085.6,154689.8,155294.0,155898.1,156502.3,157106.5,157710.7,158314.9,158919.1,159523.3,160127.5,160731.7]