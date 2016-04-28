import random
import cPickle as pickle
from collections import defaultdict
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

ECONOMY_DEBUG = 0
FED_DEBUG = 0
GRAPH = 1

K = 1000
MIN_RATE = 0
MAX_RATE = 1000
STEP = 25 ## 25bps steps

class economy:

	def __init__(self, natural_rate, a, b, belief):

		self.natural_rate = natural_rate
		self.a = a
		self.b = b
		self.inflation_expectation = 0
		self.inflation_belief = belief

	def round(self, number):
		if number > 1000:
			number = 1000
		if number < -1000:
			number = 1000
		if number < 0:
			if number%STEP >= STEP/2:
				return int(STEP+number-number%STEP)
			else:
				return int(number-number%STEP)
		else:
			if number%STEP >= STEP/2:
				return int(number + (STEP -  number%STEP))
			else:
				return int(number - number%STEP)

	def set_inflation_expectation(self, inflation):
		self.inflation_expectation = inflation

	def next (self, state, nominal_rate):
		if ECONOMY_DEBUG:
			print "====Economy generating next state===="
			print "input state (inflation, gap) : " + str(state),
			print "input nominal rate: " + str(nominal_rate)
		
		Pt = state[0]
		Yt = state[1]
		R_new = nominal_rate - Pt ## fisher equation
		
		if ECONOMY_DEBUG:
			print "New real interest rate = " + str(R_new)

		new_y = self.output_gap(Yt, R_new)
		inflation = self.inflation(Pt, Yt, new_y)

		if ECONOMY_DEBUG:
			print "New gap = " + str(new_y)
			print "New inflation = " + str(inflation)

		## discretize output

		inflation = self.round(inflation)
		new_y = self.round(new_y)

		return (inflation, new_y)


	def inflation (self, old_inflation, old_gap, new_gap):
		##error_term = self.error() ## only shock to y, not pi
		new_pi = self.inflation_belief * self.inflation_expectation + (1-self.inflation_belief) * old_inflation + self.a*(old_gap + new_gap)
		
		if ECONOMY_DEBUG:
			print "++++++Calculating new inflation++",
			print "old_inflation = " + str(old_inflation),
			print "old_gap = " + str(old_gap),
			print "new_gap = " + str(new_gap),
			print "a = " + str(self.a),
			print "inflation belief = " + str (self.inflation_belief),
			print "inflation expectation = " + str (self.inflation_expectation),
			print "new inflation = " + str(new_pi),
			print "++++++"
		return new_pi

	def output_gap (self, old_y, new_r):
		error_term = self.error()
		new_y = old_y - self.b * (new_r - self.natural_rate) + error_term
		if ECONOMY_DEBUG:
			print "++Calculating new gap",
			print "old_y = " + str(old_y),
			print "new_r = " + str(new_r),
			print "natural rate = " + str(self.natural_rate),
			print "b = " + str(self.b),
			print "error term for output gap is " + str(error_term),
			print "new_y = " + str(new_y)
		return new_y

	def error(self):
		return random.random() * 100 - 50

class fed:
	def __init__(self, target, alpha, gamma):
		self.gamma = gamma
		self.alpha = alpha
		self.inflation_target = target
		self.cumulative_reward = 0
		self.policy = defaultdict(int)
		## format: index = state, value = rate to set (argmax)
		## defaults to 0
		self.Q = defaultdict(int)
		## format: index = (state, rate), value = Q value
		## defaults to 0
		self.times_visited = defaultdict(int)
		## format: index = (state, rate), value = count
		
		self.rate_grid = []
		rate = MIN_RATE
		while rate <= MAX_RATE:
			self.rate_grid.append(rate)
			rate += STEP

		if FED_DEBUG:
			print "new rate grid: " + str(self.rate_grid)


	def load_progress(self):
		try:
			self.policy = pickle.load(open("policy.pickle", "rb"))
			self.maxQ = pickle.load(open("maxQ.pickle", "rb"))
			self.Q = pickle.load(open("Q.pickle", "rb"))
			self.times_visited = pickle.load(open("times_visited.pickle", "rb"))
		except:
			print "Open file error; files not found"

	def new_run(self, state, economy, periods, iterations):
		economy.set_inflation_expectation(self.inflation_target) ## CENTRAL BANK ANNOUNCEMENT
		t = 0
		while t < iterations:

			if FED_DEBUG:
				print "=================NEW ITERATION================="

			print "starting iteration " + str(t)
			self.new_iteration(state, economy, periods)
			t += 1


	def new_iteration(self, initial_state, economy, periods):
		## set current rewards to zero, back to initial conditions
		state = initial_state
		self.cumulative_reward = self.calculate_rewards(0, state, 0)

		t = 0
		inflation_array = []
		action_array = []
		gap_array = []
		
		while t < periods:
			## figure out which rate to set!
			## go through each possible action, calculate reward;
			## determine max
			if FED_DEBUG:
				print "---Beginning period " + str(t)
				print "---Current state is " + str(state)

			action = 0
			reward = 0
			q = -float("inf")
			next_state = state

			for action_candidate in self.rate_grid:
				next_state_candidate = economy.next(state, action_candidate)
				next_action_candidate = self.policy[next_state_candidate]
				f = self.Q[(next_state_candidate, next_action_candidate)] + K / (self.times_visited[(next_state_candidate, next_action_candidate)]+1) ## avoid div/0 error

				reward_potential = self.calculate_rewards(action_candidate, next_state_candidate, next_action_candidate)

				q_candidate  = (1-self.alpha) * self.Q[(state, action)]  + self.alpha * (reward_potential + self.gamma * f)
				self.Q[(state, action)] = q_candidate

				if FED_DEBUG:
					print "action candidate: " + str(action_candidate)
					print "f = " + str(f)
			
				if q_candidate > q:
					action = action_candidate
					next_state = next_state_candidate
					q = q_candidate
					reward = reward_potential
					if FED_DEBUG:
						print "New state-action pair considered.. ",
						print "action = " + str(action)
						print "next state candidate = " + str(next_state_candidate),
						print "next action candidate = " + str(next_action_candidate),
						print "times visited = " + str(self.times_visited[(next_state_candidate, next_action_candidate)]),
						print "reward calculated = " + str(reward),
						print "weighted f = " + str(f)
						print "q = " + str(q_candidate)

			if FED_DEBUG:
				print "============FINAL ACTION FOR STATE " + str(state) + " is " + str(action) + " ==================="
				print "============ q = " + str(q)
				print "============next state = " + str(next_state)
			
			self.times_visited[(state, action)] += 1
			self.policy[state] = action
			self.cumulative_reward += reward
			state = next_state
			t+=1

			if GRAPH:
				inflation_array.append(state[0])
				gap_array.append(state[1])
				action_array.append(action)

		if GRAPH:
		
			plt.plot(inflation_array)
			plt.show()
			
			plt.plot(gap_array)
			plt.show()

			plt.plot(action_array)
			plt.show()

			fig  = plt.figure()
			ax = fig.gca(projection='3d')
			ax.scatter(inflation_array, gap_array, action_array)
			plt.show()


	def calculate_rewards(self, action_candidate, state, next_action_candidate):
		## call internally to calculate the cumulative rewards at this state
		Pt = state[0]
		Yt = state[1]

		## loss function reversed; the smaller the loss the better
		## loss function * -1
		## good approximation??

		return  -1*((Pt - self.inflation_target)^2 + Yt^2)

	def show_policy(self):
		print self.policy

	def save_progress(self):

		pickle.dump(self.policy, open("policy.pickle", "wb"))
		pickle.dump(self.maxQ, open("maxQ.pickle", "wb"))
		pickle.dump(self.Q, open("Q.pickle", "wb"))
		pickle.dump(self.times_visited, open("times_visited.pickle", "wb"))



