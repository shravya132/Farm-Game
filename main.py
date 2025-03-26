import tkinter as tk
from typing import Callable, Union, Optional
from a3_support import *
from model import *
from constants import *

# Implement your classes here
class InfoBar(AbstractGrid):
    """ A class representing the infomation bar in the Farm Game"""
    # This class sets the size and dimensions of information bar.
    # Which includes the number of rows and columns, width and height.
    # Whilst also setting the text to be displayed.
    SIZE = (700, INFO_BAR_HEIGHT)
    DIMENSIONS = (2, 3) 
    def __init__ (self, master: tk.Tk | tk.Frame) -> None:
        """Constructor for information bar.

        Parameters: master tk.Tk which initialises the InfoBar object
        """
        super().__init__(master, self.DIMENSIONS, self.SIZE)
        self.redraw(1, Player().get_money(), Player().START_ENERGY)

    def redraw(self, day: int, money: int, energy: int) -> None:
        """Clears the infobar and redraws it to display day, money and energy.

        Parameters:
            day: the number of day/s on the farm.
            money: the amount of money the player has.
            energy: the amount of energy the player remaining that day. 
        """
        self.clear()
        self.day = day
        self.money = money
        self.energy = energy
        self.annotate_position((0, 0), 'Day:', font = HEADING_FONT)
        self.annotate_position((1, 0), f"{day}", font = HEADING_FONT)
        self.annotate_position((0, 1), "Money:", font = HEADING_FONT)
        self.annotate_position((1, 1), f"${money}", font = HEADING_FONT)
        self.annotate_position((0, 2), "Energy:", font = HEADING_FONT)
        self.annotate_position((1, 2), f"{energy}", font = HEADING_FONT)

    
        
class FarmView(AbstractGrid):
    """A class representing the display of the farm game."""
    def __init__(self, master: tk.Tk | tk.Frame,
                 dimensions: tuple[int, int], size: tuple[int, int],
                 **kwargs) -> None:
        """ Constructor for farm view.

        Parameters:
            dimensions: the rows and columns of played farm game map.
            size: the width and height of farm game map.
            
        """
        self._size = size
        self._dimensions = dimensions
        super().__init__(master, self._dimensions, self._size, **kwargs)
        self.image_cache = {}


    def redraw(self, ground: list[str], plants: dict[tuple[int, int], 'Plant'],
               player_position: tuple[int, int], player_direction: str) -> None:
        """Clears the farm view display then creates the images for
            the ground, plants and player.
            Format allows the render order of player>plant>ground.

        Parameters:
            ground: the list[str] of the read map file
            plants: the position and name of the plant
            player_position: gives the position of the player
        """
        self.clear()
        
        # creates instance of Plant class
        plant = Plant() 

        #ground images
        for row, line in enumerate(ground):
            for col, char in enumerate(line.strip()):
                if char == GRASS:
                    position = row, col
                    image_file = IMAGES[GRASS]
                    
                elif char == UNTILLED:
                    position = row, col
                    image_file = IMAGES[UNTILLED]
                    
                elif char == SOIL:
                    position = row, col
                    image_file = IMAGES[SOIL]
                else:
                    pass
                
                image = get_image(f"images/{image_file}", self.get_cell_size(),
                                  self.image_cache)
                self.create_image(self.get_midpoint(position), image=image)


        #plants images
        for key, value in plants.items():
            plant = value
            image_plant = get_plant_image_name(plant)
            image = get_image(f"images/{image_plant}", self.get_cell_size(),
                              self.image_cache)
            self.create_image(self.get_midpoint(key), image=image)
            pass


        #player images
        PLAYER = {'s': 'player_s.png', 'w': 'player_w.png', 'd': 'player_d.png',
                  'a': 'player_a.png'} 
        image = get_image(f"images/{PLAYER[player_direction]}", self.get_cell_size(),
                          self.image_cache)
        self.create_image(self.get_midpoint(player_position), image=image)

        

    
        
        


class ItemView(tk.Frame): 
    """A class representing the display of item view."""
    # Creates a frame which displays the relevant information, such as item name and amount,
    # sell price, buy price for each item.
    # Also displays sell and buy button for each item.

    def __init__(self, master: tk.Frame, item_name: str, amount: int,
                 select_command: Optional[Callable[[str], None]] = None,
                 sell_command: Optional[Callable[[str], None]] = None,
                 buy_command: Optional[Callable[[str], None]] = None) -> None:
        """ Constructor for item view.

        Parameters:
            item_name = the name of the item.
            amount =  the amount of the item.
            select_command = the command that initiates when an item is selected.
            sell_command = command that allows an item to be sold.
            buy_command = command that allows an item to be bought. 
        """
        
        super().__init__(master, bd=2, relief=tk.SUNKEN)
        self._item_name = item_name
        self._amount = amount
        self._master = master
        self.select_command = select_command
        self.buy_command = buy_command
        self.sell_command = sell_command
        self.selected = False

        
        self.item_view_label = tk.Label(
            self,
            text=(
                f"{self._item_name}: {amount}\n"
                f"Sell price: ${SELL_PRICES[self._item_name]}\n"
                f"Buy price: ${BUY_PRICES.get(self._item_name, 'N/A')}"
            ),
            fg="black"
            )
        self.item_view_label.pack(side=tk.LEFT, anchor = tk.W)
        self.item_view_label.bind("<Button-1>", self.label_clicked)
        self.bind("<Button-1>", self.label_clicked)


        # create a button for selling the item
        sell_button = tk.Button(self, text="Sell",
                                command=lambda: self.sell_command(self._item_name))
        sell_button.pack(side="left")

        # create a button for buying the item
        if BUY_PRICES.get(self._item_name, 'N/A') != 'N/A':
            buy_button = tk.Button(self, text="Buy",
                                   command=lambda: self.buy_command(self._item_name))
            buy_button.pack(side="left")

        
        self.configure(bg=INVENTORY_COLOUR)
        self.item_view_label.configure(bg=INVENTORY_COLOUR)


    def label_clicked(self, event: tk.Event) -> None:
        """ When item is selected, changes the background colour to represent its state.
            Handles the click event on the item view label.
        """
        
        if self.select_command:
            self.select_command(self._item_name)

        if self._amount == '0':
            self.selected = False
            self.configure(bg=INVENTORY_EMPTY_COLOUR)
            self.item_view_label.configure(bg=INVENTORY_EMPTY_COLOUR)

        else:   
            if not self.selected:
                self.selected = True
                self.configure(bg=INVENTORY_SELECTED_COLOUR)
                self.item_view_label.configure(bg=INVENTORY_SELECTED_COLOUR)

            else:
                self.selected = False
                self.configure(bg=INVENTORY_COLOUR)
                self.item_view_label.configure(bg=INVENTORY_COLOUR)

    

    def update(self, amount: int, selected: bool = False) -> None:
        """ Updates the text on the label, and the colour of this Item View.

        Parameters:
            amount = the amount in which the item needs to be updated to
            selected = determines if item label has been selected. Default is False. 
        """
        self._amount = amount
        self._selected = selected
        if self._selected:
            self.item_view_label.configure(
                text=(
                    f"{self._item_name}: {amount}\n"
                    f"Sell price: ${SELL_PRICES[self._item_name]}\n"
                    f"Buy price: ${BUY_PRICES.get(self._item_name, 'N/A')}"
                )
            )

        if self._amount == '0':
            self.configure(bg=INVENTORY_EMPTY_COLOUR)
            self.item_view_label.configure(bg=INVENTORY_EMPTY_COLOUR)
            
        else:
            self.configure(bg=INVENTORY_COLOUR)
            self.item_view_label.configure(bg=INVENTORY_COLOUR)
            pass
                         
    

    
class FarmGame(object):
    """An abstract class providing the functionality of the Farm Game."""
    def __init__(self, master: tk.Tk, map_file: str) -> None:
        """Constructor for farm game.

        Parameters:
            map_file: the file of the chosen map.
        """
        
        self._master = master
        self._map_file = map_file
        self._image_cache = {}

        
        #set title of window
        master.title("Farm Game")
        self.updated_map_file = None


        #create title banner
        self._banner = get_image('images/header.png', (700, BANNER_HEIGHT),
                                 self._image_cache)
        banner_label = tk.Label(self._master, image=self._banner)
        banner_label.pack(side=tk.TOP)


        #create FarmModel instance
        self.farmmodel = FarmModel(self._map_file)
        self.player = self.farmmodel.get_player()


        #create instances of view classes
        next_day_button = tk.Button(master, text="Next day", command=self.next_day)
        next_day_button.pack(side=tk.BOTTOM)
        
        self._infobar = InfoBar(master)
        self._infobar.pack(side=tk.BOTTOM)

        self.plant_dict = {}

        map_data = read_map(self._map_file)
        num_rows = len(map_data)
        num_cols = len(map_data[0]) 
        
        
        self._farmview = FarmView(master, (num_rows, num_cols), (FARM_WIDTH, FARM_WIDTH))
        self._farmview.pack(side=tk.LEFT)
        self._farmview.redraw(self.farmmodel.get_map(), self.plant_dict,
                              self.farmmodel.get_player_position(),
                              self.farmmodel.get_player_direction())

        self.item_views = []
        self.inventory = self.player.get_inventory()
        for item_name in ITEMS:
            self.item_view = ItemView(master, item_name, self.inventory.get(item_name, '0'),
                                      select_command=self.select_item,
                                      sell_command=self.sell_item,
                                      buy_command=self.buy_item)
            
            self.item_view.pack(side=tk.TOP, fill=tk.X, expand=True, ipady=12)
            self.item_view.update(self.inventory.get(item_name, '0'), False)
            self.item_views.append(self.item_view)  
            

        self._master.bind('<KeyPress>', self.handle_keypress)


    def handle_keypress(self, event):
        """Handles the button press actions in the game."""
        
        # Get the key pressed
        key = event.keysym

        # Handle the keypress event based on the key
        if key == 'w':
            self.move_and_redraw(UP)
            
        elif key == 'a':
            self.move_and_redraw(LEFT)
            
        elif key == 's':
            self.move_and_redraw(DOWN)
            
        elif key == 'd':
            self.move_and_redraw(RIGHT)
            
        elif key == 't':
            row, col = self.farmmodel.get_player_position()
            if self.farmmodel._map[row][col] == UNTILLED:
                self.replace_character(self._map_file, self.farmmodel.get_player_position(), 'S')
                self.farmmodel.till_soil(self.farmmodel.get_player_position())
                self.redraw()
            
        elif key == 'u':
            row, col = self.farmmodel.get_player_position()
            if self.farmmodel._map[row][col] == SOIL:
                self.replace_character(self._map_file, self.farmmodel.get_player_position(), 'U')
                self.farmmodel.untill_soil(self.farmmodel.get_player_position())
                self.redraw()

        elif key == 'p':
            for item_view in self.item_views:
                if item_view.selected == True:
                    if item_view._item_name in SEEDS:
                        row, col = self.farmmodel.get_player_position()
                        if self.farmmodel._map[row][col] == SOIL:
                            if self.inventory.get(item_view._item_name, '0') != '0':
                                PLANTS = {'Potato Seed': PotatoPlant(),
                                          'Kale Seed': KalePlant(),
                                          'Berry Seed': BerryPlant()}
                                
                                plant = PLANTS[item_view._item_name]
                                self.farmmodel.add_plant(self.farmmodel.get_player_position(), plant)
                                self.player.remove_item((item_view._item_name, 1))
                                amount=self.inventory.get(item_view._item_name, '0')
                                item_view.update(amount, True)
                                self.redraw()
                                
        elif key == 'r':
            player_position = self.farmmodel.get_player_position()
            keys = self.farmmodel.get_plants().keys()
            if player_position in keys:
                self.farmmodel.remove_plant(player_position)
                self.redraw()
                
        elif key == 'h':
            for item_view in self.item_views:
                keys = self.farmmodel.get_plants().keys()
                values = self.farmmodel.get_plants().values()
                player_position = self.farmmodel.get_player_position()
                if player_position in keys:
                    self.farmmodel.harvest_plant(player_position)
                    PRODUCE = {'Potato Seed': 'Potato', 'Kale Seed': 'Kale', 'Berry Seed':'Berry'}
                    item_name = self.player.get_selected_item()
                    if item_name == 'Berry Seed':
                        crop = PRODUCE[item_name]
                        self.player.add_item((crop, 1))
                        amount=self.inventory.get(crop, '0')
                        self.redraw()
                    
                    elif player_position not in keys:
                        crop = PRODUCE[item_name]
                        self.player.add_item((crop, 1))
                        amount=self.inventory.get(crop, '0')
                        self.redraw()                  
        
        else:
            pass
        
        
    def move_and_redraw(self, direction):
        """Allows the player to move and redraw with the player's current position.

        Parameter:
            direction = the side the player faces. 
        """
        self.farmmodel.move_player(direction)
        self._farmview.redraw(self.farmmodel.get_map(), self.farmmodel.get_plants(),
                              self.farmmodel.get_player_position(),
                              self.farmmodel.get_player_direction())
        
        self._infobar.redraw(self.farmmodel.get_days_elapsed(),
                             self.player.get_money(),
                             self.player.get_energy())
        

    def redraw(self) -> None:
        """ Redraws the entire game based on current model state.
        
        """
        self._farmview.redraw(self.farmmodel.get_map(),
                              self.farmmodel.get_plants(),
                              self.farmmodel.get_player_position(),
                              self.farmmodel.get_player_direction())
        
        self._infobar.redraw(self.farmmodel.get_days_elapsed(),
                             self.player.get_money(),
                             self.player.get_energy())
        
        for item_view in self.item_views:
            item_name = item_view._item_name
            amount = self.inventory.get(item_name, '0')
            item_view.update(amount, True)

        
    def select_item(self,item_name: str) -> None:
        """ Sets the selected item to be item_name and redraw view"""
        if self.inventory.get(item_name, '0') != '0':
            self.player.select_item(item_name)
            self.item_view
            for item_view in self.item_views:
                item_view.update(self.inventory.get(item_view._item_name, '0'))
                item_view.selected = False
                              

    def buy_item(self, item_name: str) -> None:
        """Allows player to attempt to buy item with the given item_name with specific buy prices,
            and redraws view.

            Parameters:
                item_name = item_name that the player wants to buy.
        """
        buy_price = BUY_PRICES.get(item_name, 'N/A')
        if buy_price != 'N/A':
            self.player.buy(item_name, buy_price)
            amount = self.inventory.get(item_name, '0')
            for item_view in self.item_views:
                if item_view._item_name == item_name:
                    item_view.update(amount, True)
            self.redraw()
            

    def sell_item(self, item_name: str) -> None:
        """Allows player to attempt to sell item with given item_name with specific sell prices,
            and redraws view.

            Parameters:
                item_name = item_name that the player wants to sell.
        """
        sell_price = SELL_PRICES.get(item_name)
        self.player.sell(item_name, sell_price)
        amount=self.inventory.get(item_name, '0')
        for item_view in self.item_views:
            if item_view._item_name == item_name:
                item_view.update(amount, True)
            self.redraw()
        

    def next_day(self):
        """Allows the farm game to progress to the next day and redraws view."""
        self.farmmodel.new_day()
        self.redraw()

        
    def replace_character(self, map_file: str, position, new_character):
        """Replaces the character in the map file when map is changed

            Parameters:
                map_file = the given map file.
                position = position of the character to be replaced.
                new_character = new_character to replace the original character with.
        """
        
        map_rows = read_map(map_file)
        row_index = position[0]
        col_index = position[1]
        # Replaces the character in the map when player tills or untills the ground
        map_rows[row_index] = map_rows[row_index][:col_index] + new_character + map_rows[row_index][col_index+1:]
        updated_map = '\n'.join(map_rows)
        self.updated_map_file = map_file.replace('.txt', '_updated.txt')

        with open(self.updated_map_file, 'w') as file:
            file.write(updated_map)
        return self.updated_map_file




            
def play_game(root: tk.Tk, map_file: str) -> None:
    """Constructs the controller instance using map_file and root.Tk."""
    FarmGame(root, map_file) 
    root.mainloop()
    

def main() -> None:
    """ Construct the root tk.Tk instance."""
    root = tk.Tk()
    game = play_game(root, 'maps/map1.txt')



if __name__ == '__main__':
    main()
    
    