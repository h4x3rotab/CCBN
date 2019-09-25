# Code to validate that the python BTGDAA simulator output actually matches the 
# the actual BTG blockchain - this code uses data from block chain to seed
# the DAA averaging window and then run the simulator to determine next difficulty
# based on actual block find times
#
# Process: 
#   1. Read 50 blocks of actual blockchain data to seed the DAA
#   2. Calculate the next 50 difficulties & compare to actual

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
    
#==================================================================================

# pull stream of actual BTG chain data from
# CSV with format "timestamp, difficulty, findtime"
# this code uses the findtime (curr - prev), not the timestamp
blockfile = open("btgvalidationdata.csv","r")
actual_chain_data = []
block_count = 0
for line in blockfile:
    block_data = line.split(",")
    # block = [timestamp, difficulty, findtime]
    actual_chain_data.append([
        int(block_data[0]),
        float(block_data[1]),
        int(block_data[2])])
    block_count += 1

# BTG DAA uses prior 45 blocks in averaging window
# seed simulated chain with 50 blocks from validation data (copy real BTG chain data)
simulated_chain = []
for i in range(0,50):
    simulated_chain.append(actual_chain_data[i])

# begin running simulated DAA on mainchain
# note that DAA builds on prior targets, 
# so any unbalanced error should be magnified as more blocks go by
for i in range(50, block_count):
    # block = [timestamp, difficulty, findtime]
    simulated_chain.append([
        actual_chain_data[i][0], # actual timestamp
        BTGDAA(simulated_chain, i),  # our difficulty calc
        actual_chain_data[i][2]]) # actual findtime

# Compare actual difficulty with simulated difficutly & show delta
output = open("CCBNsimvalid.txt","w")
out=""
output.write("Simulated DAA begins after 50 blocks.\n\n")
output.write("Block: [actual chain data] [simulated DAA chain] delta: difficulty difference\n")
output.write("=============================================================================\n")

for i in range (0,len(actual_chain_data)):
    out = (str(i+1) + ": " + 
        str(actual_chain_data[i][1]) +" "+ 
        str(simulated_chain[i][1]) +
        " delta: "+ str(actual_chain_data[i][1]-simulated_chain[i][1]) +
        " err: " + str((actual_chain_data[i][1]-simulated_chain[i][1])/actual_chain_data[i][1])
        )
    output.write(out+"\n")
    print(out)

blockfile.close()
output.close()
