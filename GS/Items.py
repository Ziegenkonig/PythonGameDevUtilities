class Item:
	#an item that can be picked up and used.
	def pick_up(self, message, inventory, objects):
		#add to the player's inventory and remove from the map
		if len(inventory) >= 26:
			message('Your inventory is full, cannot pick up ' + self.owner.name + '.', (255,0,0))
		else:
			inventory.append(self.owner)
			objects.remove(self.owner)
			message('You picked up a ' + self.owner.name + '!', (0,255,0))