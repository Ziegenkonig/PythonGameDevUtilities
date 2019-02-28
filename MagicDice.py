import random

#Can instantiate an instance of MagicDice to always have to use
class MagicDice:

	def __init__(self, amount, sides):

		self.sides 	= sides
		self.amount = amount

	#Returns a list of each individual dice roll, as well as the sum of the roll
	def roll(self):

		print('Rolling ' + str(self.amount) + 'd' + str(self.sides))

		results = []
		roll = 0;

		for dice in range(self.amount):
			roll = random.randint(1, self.sides)
			results.append( roll )
			print('    Dice ' + str(dice+1) + ': ' + str(roll))

		print( 'Total For The Roll: ' + str(sum(results)) )

		return ( results, sum(results) )

	#Returns a list of each individual dice roll, displays each whole roll, and displays the total sum across all rolls
	def multiRoll(self, number_of_rolls):

		print('Rolling ' + str(self.amount) + 'd' + str(self.sides) + ' ' + str(number_of_rolls) + ' Times\n')

		results = []
		result = []
		roll = 0;

		for rounds in range(number_of_rolls):
			print('    Round ' + str(rounds+1) + ': ')
			for dice in range(self.amount):
				roll = random.randint(1, self.sides)
				result.append( roll )
				print('        Dice ' + str(dice+1) + ': ' + str(roll))
			results.append(result)
			print( '    Total For The Round: ' + str(sum(result)) + '\n')
			result = []

		total_sum = 0
		for lists in results:
			total_sum += sum(lists)
		print( 'Total For All Rolls: ' + str(total_sum) )

		return ( results, total_sum )

#Needs a separate call every time
class RegularDice:

	#Returns a list of each individual dice roll, as well as the sum of the roll
	def roll(self, amount, sides):

		print('Rolling ' + str(amount) + 'd' + str(sides))

		results = []
		roll = 0;

		for dice in range(amount):
			roll = random.randint(1, sides)
			results.append( roll )
			print('    Dice ' + str(dice+1) + ': ' + str(roll))

		print( 'Total For The Roll: ' + str(sum(results)) )

		return ( results, sum(results) )

	#Returns a list of each individual dice roll, displays each whole roll, and displays the total sum across all rolls
	def multiRoll(self, amount, sides, number_of_rolls):

		print('Rolling ' + str(amount) + 'd' + str(sides) + ' ' + str(number_of_rolls) + ' Times\n')

		results = []
		result = []
		roll = 0;

		for rounds in range(number_of_rolls):
			print('    Round ' + str(rounds+1) + ': ')
			for dice in range(amount):
				roll = random.randint(1, sides)
				result.append( roll )
				print('        Dice ' + str(dice+1) + ': ' + str(roll))
			results.append(result)
			print( '    Total For The Round: ' + str(sum(result)) + '\n')
			result = []

		total_sum = 0
		for lists in results:
			total_sum += sum(lists)
		print( 'Total For All Rolls: ' + str(total_sum) )

		return ( results, total_sum )


reg_dice = RegularDice()
reg_dice.roll(2, 20)
reg_dice.multiRoll(2, 20, 3)

test_dice = MagicDice( 3, 6 )
test_dice.roll()
test_dice.multiRoll(3)
