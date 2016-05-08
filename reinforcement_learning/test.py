import rl
import sys


def new_learning_session(feddy, Pt, Yt, periods, iterations):

	feddy.new_run((Pt, Yt), econ, periods, iterations)
	feddy.save_progress()

def continue_learning(feddy, Pt, Yt, periods, iterations):
	feddy.load_progress()
	feddy.new_run((Pt, Yt), econ, periods, iterations)
	feddy.save_progress()

def new_test_run(feddy, Pt, Yt, periods):

	feddy.load_progress()
	feddy.new_run((Pt, Yt), econ, periods, 1)
	feddy.graph_latest_run()

def new_dummy_run(feddy, Pt, Yt, periods):
	feddy.dummy_run((Pt, Yt), econ, periods, 550)


def new_real_run(feddy):
	feddy.real_test_run(econ, econ_log)





if __name__ == "__main__":


	print "Initializing economy"

	econ = rl.economy(300, 0.1, 0.1, 0.1, 0.5, -0.7)
	econ.set_inflation_expectation(200)
	
	print "initializing fed"

	feddy = rl.fed(200, 0.2, 0.5)

	econ_log = rl.economy_log()


	print "getting the fed started"
	
	Pt = 300
	Yt = 200

	### MANUAL TOGGLE###
	if sys.argv[1] == '1':
		new_learning_session(feddy, Pt, Yt, 100, int(sys.argv[2]))
	elif sys.argv[1] == '2':
		continue_learning(feddy, Pt, Yt, 100, int(sys.argv[2]))
	elif sys.argv[1] == '3':
		new_test_run(feddy, Pt, Yt, int(sys.argv[2]))
	elif sys.argv[1] == '4':
		new_dummy_run(feddy, Pt, Yt, int(sys.argv[2]))
	elif sys.argv[1] == '5':
		new_real_run(feddy)


	








