import random
import cPickle as pickle
from collections import defaultdict
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy
import math
import pandas ## for csv handling

ECONOMY_DEBUG = 0
FED_DEBUG = 0
EXPERIMENTAL = 0
BLANK = 0
RANDOM_DEBUG = 0

K = 1000
MIN_RATE = 0
MAX_RATE = 1000
STEP = 25 ## 25bps steps

class economy_log:

	def __init__(self):
		self.inflation_history = []
		self.gap_history = []
		self.actual_rate = []

		colnames = ['date', 'gap', 'inflation', 'rate']
		data = pandas.read_csv('benchmark.csv', names = colnames)

		self.gap_history = map(float, data.gap.tolist()[1:-1])
		self.inflation_history = map(float, data.inflation.tolist()[1:-1])
		self.actual_rate = map(float, data.rate.tolist()[1:-1])
		self.t = 0

	def round(self, number):
		if number > 1000:
			number = 1000
		if number < -1000:
			number = -1000
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

	def next (self):
		if self.t < len(self.gap_history):
			inflation = self.round(self.inflation_history[self.t])
			gap = self.round(self.gap_history[self.t])
			self.t +=1
			return (inflation, gap)
		else:
			print "error, t = " + str(self.t) + ", len = " + str(len(self.gap_history))

	def initial(self):
		return self.round(self.inflation_history[0]), self.round(self.gap_history[0])

	def periods(self):
		return len(self.gap_history)-1

	def set_inflation_expectation(self, inflation):
		pass





class economy:

	def __init__(self, natural_rate, a, b, c, belief, error_corr):

		self.natural_rate = natural_rate
		self.a = a
		self.b = b
		self.c = c
		self.inflation_expectation = 0
		self.inflation_belief = belief

		self.inflation_error_array = []
		self.gap_error_array = []

		self.generate_random_sequences(error_corr)

		if RANDOM_DEBUG:
			plt.scatter(self.inflation_error_array, self.gap_error_array)


	def generate_random_sequences(self, corr): ## generates correlated random sequence
		index = 0
		while index < 100:
			number = random.random() * 50 - 25
			self.inflation_error_array.append(number)
			number2 = random.random() * 50- 25
			self.gap_error_array.append(corr * number + math.sqrt(1 - corr**2) * number2)
			index +=1


	def round(self, number):
		if number > 1000:
			number = 1000
		if number < -1000:
			number = -1000
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

		error_index = int(random.random() * 100)
		new_y = self.output_gap(Yt, R_new, error_index)
		inflation = self.inflation(Pt, Yt, new_y, error_index)


		if EXPERIMENTAL:

			inflation = (self.a * self.c * (nominal_rate - self.natural_rate) + self.b * (Pt - self.inflation_expectation) - self.c * (2 * Yt - self.error()) - Pt) / (self.a * self.c - 1)


		if ECONOMY_DEBUG:
			print "New gap = " + str(new_y)
			print "New inflation = " + str(inflation)

		## discretize output

		inflation = self.round(inflation)
		new_y = self.round(new_y)

		return (inflation, new_y)

	def inflation (self, old_inflation, old_gap, new_gap, error_index):
		##error_term = self.error() ## only shock to y, not pi
		error_term = self.inflation_error_array[error_index]
		new_pi = self.inflation_belief * self.inflation_expectation + (1-self.inflation_belief) * old_inflation + self.c*(old_gap + new_gap)
	
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

	def output_gap (self, old_y, new_r, error_index):
		error_term = self.gap_error_array[error_index]
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
		##return random.random() * 25 - 50
		index = int(random.random() * 1000)
		return 

		##return 0

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

		self.inflation_array = []
		self.action_array = []
		self.gap_array = []
		self.real_array = []
		self.rewards = []
		self.rewards_avg = []

		self.inflation_mean_history = []
		self.inflation_sd_history = []
		self.gap_mean_history = []
		self.gap_sd_history = []
		self.action_mean_history = []
		self.action_sd_history = []


		self.inflation_error_history = []
		self.gap_error_history = []

	def load_progress(self):
		try:
			self.policy = pickle.load(open("policy.pickle", "rb"))
			self.Q = pickle.load(open("Q.pickle", "rb"))
			self.times_visited = pickle.load(open("times_visited.pickle", "rb"))
		except:
			print "Open file error; files not found"
	
	def save_progress(self):

		pickle.dump(self.policy, open("policy.pickle", "wb"))
		pickle.dump(self.Q, open("Q.pickle", "wb"))
		pickle.dump(self.times_visited, open("times_visited.pickle", "wb"))
	

	def dummy_run(self, state, economy, periods, rate):
		
		economy.set_inflation_expectation(self.inflation_target)
		t = 0

		next_state = state
		
		while t<periods:
			next_state = economy.next(next_state, rate)
			self.inflation_array.append(next_state[0])
			self.gap_array.append(next_state[1])
			self.action_array.append(rate)
			self.real_array.append(rate - next_state[0])
			t+=1

		self.graph_latest_run()



	def new_run(self, state, economy, periods, iterations):
		economy.set_inflation_expectation(self.inflation_target) ## CENTRAL BANK ANNOUNCEMENT
		t = 0
		while t < iterations:

			if FED_DEBUG:
				print "=================NEW ITERATION================="

			print "starting iteration " + str(t)
			self.new_iteration(state, economy, periods)
			print "cumulative reward = " + str(self.cumulative_reward)
			self.rewards.append(self.cumulative_reward) 

			if t > 10:
				running_avg = sum(self.rewards[-10:]) / 10
				self.rewards_avg.append(running_avg)

			t += 1

			inflation_mean = numpy.mean(self.inflation_array)
			inflation_sd = numpy.std(self.inflation_array)
			gap_mean = numpy.mean(self.gap_array)
			gap_sd = numpy.std(self.gap_array)
			action_mean = numpy.mean(self.action_array)
			action_sd = numpy.std(self.action_array)


			print "Inflation mean:%4d, inflation SD:%4d \ngap mean:%4d, gap SD:%4d \nnominal rate mean:%4d, nominal rate SD:%4d" % (inflation_mean, inflation_sd, gap_mean, gap_sd, action_mean, action_sd)

			self.inflation_mean_history.append(inflation_mean)
			self.inflation_sd_history.append(inflation_sd)
			self.gap_mean_history.append(gap_mean)
			self.gap_sd_history.append(gap_sd)
			self.action_mean_history.append(action_mean)
			self.action_sd_history.append(action_sd)


		plt.figure()
		plt.subplot(211)
		plt.plot(self.rewards)
		plt.title('reward trend')
		plt.subplot(212)
		plt.plot(self.rewards_avg)
		plt.title('10-iteration avg reward trend')
		plt.show()

		plt.figure()
		plt.subplot(321)
		plt.plot(self.inflation_mean_history)
		plt.title('Inflation mean trend')
		plt.subplot(322)
		plt.plot(self.inflation_sd_history)
		plt.title('Inflation SD trend')
		plt.subplot(323)
		plt.plot(self.gap_mean_history)
		plt.title('Gap mean trend')
		plt.subplot(324)
		plt.plot(self.gap_sd_history)
		plt.title('Gap SD trend')	
		plt.subplot(325)
		plt.plot(self.action_mean_history)
		plt.title('Nominal rate mean trend')	
		plt.subplot(326)
		plt.plot(self.action_sd_history)
		plt.title('Nominal rate SD trend')	
		plt.show()



		## stats

	def graph_latest_run(self):	

		plt.figure(1)
		plt.subplot(221)
		plt.plot(self.inflation_array)
		plt.title('Inflation trend')
		
		plt.subplot(222)
		plt.plot(self.gap_array)
		plt.title('Output gap trend')

		plt.subplot(223)
		plt.plot(self.action_array)
		plt.title('Nominal rate trend')

		plt.subplot(224)
		plt.plot(self.real_array)
		plt.title('Real rate trend')

		plt.show()

		fig  = plt.figure()
		ax = fig.gca(projection='3d')
		ax.scatter(self.inflation_array, self.gap_array, self.action_array)
		plt.title('Inflation v. Output V. Rate')
		
		plt.show()
		

	def new_iteration(self, initial_state, economy, periods):
		## set current rewards to zero, back to initial conditions
		state = initial_state
		self.cumulative_reward = self.calculate_rewards(0, state, 0)

		t = 0
		self.inflation_array = []
		self.action_array = []
		self.gap_array = []
		
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
			
			
			real_rate = action - state[0]

			self.times_visited[(state, action)] += 1
			self.policy[state] = action
			self.cumulative_reward += reward
			state = next_state
			t+=1


			self.real_array.append(real_rate)
			self.inflation_array.append(state[0])
			self.gap_array.append(state[1])
			self.action_array.append(action)


	def real_test_run(self, economy, economy_log):

		periods = economy_log.periods()
		t = 0
		while t < periods:
			state = economy_log.next()
			action = self.action_response(state, economy)
			self.inflation_array.append(state[0])
			self.gap_array.append(state[1])
			self.real_array.append(action - state[0])
			self.action_array.append(action)
			t+=1

		plt.figure(1)
		plt.subplot(321)
		plt.plot(self.inflation_array)
		plt.title('Inflation trend')
		
		plt.subplot(322)
		plt.plot(self.gap_array)
		plt.title('Output gap trend')

		plt.subplot(323)
		plt.plot(self.action_array)
		plt.title('Projected Nominal rate trend')


		plt.subplot(324)
		plt.plot(economy_log.actual_rate)
		plt.title('Actual rate trend')
		
		i = 0
		actual_rate_diff = []
		projected_rate_diff = []
		while i < len(self.action_array)-1:
			actual_rate_diff.append(economy_log.actual_rate[i+1] - economy_log.actual_rate[i])
			projected_rate_diff.append(self.action_array[i+1] - self.action_array[i])
			i+=1

		plt.subplot(325)
		plt.plot(projected_rate_diff)
		plt.title('Change in projected rate')

		plt.subplot(326)
		plt.plot(actual_rate_diff)
		plt.title('Change in actual rate')

		plt.show()


	def action_response(self, initial_state, economy): ## for plotting real world data
			## set current rewards to zero, back to initial conditions
			state = initial_state
			self.cumulative_reward = self.calculate_rewards(0, state, 0)

			t = 0
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
			


			return action


	def calculate_rewards(self, action_candidate, state, next_action_candidate):
		## call internally to calculate the cumulative rewards at this state
		Pt = state[0]
		Yt = state[1]

		## loss function reversed; the smaller the loss the better
		## loss function * -1
		## good approximation??

		return  -1*((Pt - self.inflation_target)^2 + Yt^2 + (2/3) * (action_candidate - next_action_candidate)^2)





