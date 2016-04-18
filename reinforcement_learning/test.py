import rl




if __name__ == "__main__":


	print "Initializing economy"

	econ = rl.economy(300, 0.1, 0.1, 0.5)
	econ.set_inflation_expectation(200)
	
	print "initializing fed"

	feddy = rl.fed(200, 0.2, 0.5)


	print "getting the fed started"
	
	Pt = 300
	Yt = 200
	
	##feddy.new_run((Pt, Yt), econ, 1000, 1000)
	feddy.load_progress()
	##feddy.show_policy()

	feddy.new_run((Pt, Yt), econ, 100, 1)

	##feddy.save_progress()
	





