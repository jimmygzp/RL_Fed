
<h1>Readme for test.py and rl.py</h1>
by Zepeng Guan
z.lastname@columbia.edu


<h2>Required python packages</h2>

numpy, pandas (for csv handling), matplotlib, mpl_toolkits (both for plotting)


<h2>Usage</h2>

<p>test.py contains several funtions that allows the user to test the functions in rl.py. There are 5 basic modes of usage; each includes a specific use case that will be detailed below, with recommended commands.</p>

<h3>1. Learning</h3>

The RL engine will run through a given number of iterations based on user discretion, with each iteration consisting a specifc number of time periods. The mode can be called as the follows:

python test.py 1 num_of_periods_in_each_iteration num_of_iterations

Example used in paper:

python test.py 1 100 100

Which means running 100 iterations of exploration, with each iteration consisting of 100 periods.

The learning progress will  be plotted after completion.

Upon completion, the policy data will be saved in the form of several *.pickle files. It is imperative that these files be kept before running any other functions. Any new learning session will overwrite previous *.pickle files.


<h3>2. Continue Lerning</h3>

The RL engine can pick up where it left off previously by loading the *.pickle files, and continue running more iterations before saving the new progress. The syntax is very similar:

python test.py 2 num_of_periods_in_each_iteration num_of_iterations

An error will be thrown if there are no valid *.pickle files found in the program directory.


<h3>3. Trial run</h3>

This is a one-iteration run that details the changes in each period, used after a complete learning session. The program will attempt to load the *.pickle files in the current directory. If none is found, and error will be thrown, and step 1 must be performed first. Note that each trial run may have different results due to random shocks. The syntax is the follows:

python test.py 3 num_of_periods

Example used in paper:

python test.py 3 100

Which means running a 100-period iteration.

<h3>4. Dummy run</h3>

This is simply using a fixed rate to test the state transitions of the toy economy. The mode can be called by

python test.py 4 num_of_periods

<h3>5. Real run</h3>

In this mode, the rates set by the virtual federal reserve will be compared to those set by the real federal reserve. In addition to the *.pickle files, the program will attempt to load the historical data from benchmark.csv, found in the program directory, that includes data from St.Louis Fed. The results will then be compared and graphed. The syntax is very simple:

python test.py 5


================

<h2>Important details</h2>

There are many parameters used in both the economic model and learning model. They are all modifiable; however, there are four types of variables in terms of modifiability:

1. Variables that are governed by input parameters: periods, etc. These are the easiest to modify

2. Variables that are governed by explicit variables found on the top rl.py: action space, state space, etc. These are relatively easy to modify, but requires modifications to the source code

3. Parameters that are hardcoded in the funciton calls in test.py: inflation expectation, etc. these are a little harder to modify, because the function descriptions in rl.py will have to be referenced. But they are nevertheless modifiable

4. Parameters that are hardcoded in the learning model in rl.py: decay parameter, etc. These are the hardest to modify, because some lack explicit documentation in code, but they can still be modified if the code is read carefully

As the code is still in its early stage, the future goal is to transition most varaibles in types 3 and 4 into types 1 and 2, so the program can be adjusted with ease.


