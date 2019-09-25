# CCBN
Simulation code for CCBN on BTG

To run a simulation, edit 'param.py' with the conditions you wish to simulate, then run 'CCBNsim.py'. Results are logged in unique files in the specified subfolder.

The simulator will run multiple conditions simultaneously for multiple attack hashpowers and multiple notarychains defending; always test your configuration for a short run to confimr you're capturing the desired data before running a long simulation.

The main simulator code is in `CCBNsim.py`. Parameters & contants for readability are in `param.py`. `CCBNdefs.py` contains supporting functions & initializations, while `CCBNlogger.py` contains the code for creating the output to screen and file.

### Subfolders

- DAA Validation: code & output validating this implementation of the BTG DAA (Difficulty Adjustment Algorithm)
- BTG Blocktime Mean: code for long simulation to determine actual BTG mean (which is not exactly 600 seconds)
- BTG Blocktime SD: code for long simulation to estimate BTG Standard Deviation, which does not match the Exponential distribution
