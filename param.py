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
BTG_MEAN_PLUS_2SD = [0.0000,1837.1901,2970.6863,3963.3812,4882.3664,5753.7286,6590.8098,7401.5704,8191.2300,8963.4950,9721.0610,10465.9800,11199.8734,11924.0524,12639.5644,13347.3120,14048.0628,14742.4590,15431.0538,16114.3482,16792.7704,17466.6980,18136.4744,18802.4214,19464.8172,20123.8764,20779.8290,21432.8982,22083.2668,22731.1074,23376.5696,24019.8182,24660.9768,25300.1854,25937.5424,26573.1684,27207.1562,27839.6186,28470.6542,29100.3418,29728.7596,30355.9888,30982.0896,31607.1198,32231.1500,32854.2384,33476.4478,34097.8258,34718.4278,35338.3054,35957.4758,36575.9684,37193.8204,37811.0414,38427.6746,39043.7322,39659.2378,40274.2258,40888.7034,41502.7084,42116.2682,42729.3938,43342.1044,43954.4382,44566.3876,45177.9724,45789.2094,46400.0926,47010.6646,47620.9294,48230.9236,48840.6690,49450.1430,50059.3694,50668.3696,51277.1302,51885.6704,52494.0090,53102.1486,53710.1116,54317.9056,54925.5354,55533.0144,56140.3470,56747.5428,57354.6108,57961.5504,58568.3864,59175.0980,59781.6914,60388.1816,60994.5542,61600.8272,62207.0066,62813.1020,63419.1224,64025.0508,64630.9004,65236.6758,65842.3902,66448.0520,67053.6498,67659.1868,68264.6488,68870.0518,69475.4048,70080.6994,70685.9480,71291.1454,71896.2942,72501.4020,73106.4550,73711.4736,74316.4528,74921.4052,75526.3330,76131.2306,76736.0920,77340.9262,77945.7228,78550.4964,79155.2406,79759.9428,80364.6306,80969.2886,81573.9182,82178.5320,82783.1206,83387.6930,83992.2466,84596.7892,85201.3236,85805.8426,86410.3484,87014.8298,87619.3050,88223.7798,88828.2352,89432.6760,90037.1022,90641.5006,91245.8982,91850.2842,92454.6478,93059.0090,93663.3654,94267.7106,94872.0488,95476.3862,96080.7150,96685.0332,97289.3418,97893.6578,98497.9770,99102.2820,99706.5862,100310.8802,100915.1704,101519.4530,102123.7350,102728.0294,103332.3142,103936.5826,104540.8428,105145.0986,105749.3614,106353.6278,106957.8936,107562.1470,108166.4098,108770.6848,109374.9516,109979.2168,110583.4768,111187.7346,111791.9834,112396.2230,113000.4740,113604.7272,114208.9836,114813.2342,115417.4894,116021.7432,116626.0054,117230.2718,117834.5440,118438.8022,119043.0592,119647.3026,120251.5260,120855.7322,121459.9400,122064.1492,122668.3630,123272.5742,123876.7856,124481.0062,125085.2388,125689.4730,126293.7066,126897.9422,127502.1800,128106.4124,128710.6362,129314.8626,129919.0882,130523.3252,131127.5588,131731.7852,132336.0100,132940.2240,133544.4288,134148.6286,134752.8200,135357.0078,135961.1988,136565.3900,137169.5942,137773.7958,138377.9946,138982.1830,139586.3704,140190.5424,140794.7172,141398.8816,142003.0320,142607.1736,143211.3268,143815.4852,144419.6462,145023.7900,145627.9376,146232.1000,146836.2798,147440.4640,148044.6486,148648.8370,149253.0290,149857.2288,150461.4378,151065.6504,151669.8756,152274.0962,152878.3228,153482.5468,154086.7590,154690.9636,155295.1546,155899.3468,156503.5390,157107.7176,157711.9008,158316.0870,158920.2676,159524.4574,160128.6396,160732.8144]