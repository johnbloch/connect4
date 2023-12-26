from connect_four import ConnectFourGame
from connect_four_gui import ConnectFourGUI

# Create an instance of the ConnectFourGame class
game = ConnectFourGame()

# Create an instance of the ConnectFourGUI class, passing the game instance
gui = ConnectFourGUI(game)

# Start the game
if __name__ == "__main__":
    gui.root.mainloop()
