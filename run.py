import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("kitchen_assistant")
INV_LIST = SHEET.worksheet("inventory")
SHOPPING_WORKSHEET = SHEET.worksheet("shopping_list")


# ---- RECIPE FUNCTIONS ----
def fetch_recipe_list():
    """
    Fetch and displays all the available recipes.
    """
    available_recipe_data = SHEET.worksheet("recipes_list")
    recipe_list = available_recipe_data.col_values(1)
    for nos, recipe in enumerate(recipe_list):
        print(f"{nos+1}: {recipe.capitalize()}")
    print("*" * 30)
    while True:
        user_cook = input("Would you like to cook today?(y/n)\n")
        print()
        if validate_yes_no(user_cook):
            if user_cook.lower() == "y":
                fetch_recipe_steps()
                print("*" * 30)
                break
            break
    main_menu = input("Would you like to go back to the main menu? y/n:\n")
    while True:
        if validate_yes_no(main_menu):
            if main_menu.lower() == "y":
                print()
                main()
                break
            break
        main_menu = input(":\n")


def fetch_recipe_steps():
    """
    Fetch the steps for the user's chosen recipe
    """
    print("*" * 30)
    while True:
        food_choice = input("Please enter the recipe name:\n")
        if validate_recipe_choice(food_choice.lower()):
            next_step = check_ingredients(food_choice)
            if next_step is False:
                recipe_step_list = SHEET.worksheet("recipes")
                search_recipe = recipe_step_list.find(food_choice.lower())
                recipe_col = recipe_step_list.col_values(search_recipe.col)
                print()
                for step_no, step in enumerate(recipe_col):
                    if step_no == 0:
                        print(f"Recipe for {step.capitalize()}:")
                        print("-" * 30)
                    else:
                        print(f"{step_no}: {step} \n")
                print("*" * 30)
                print("Enjoy!")
                break
            else:
                print()
                print("Not all ingredients available \n")
                print("Adding to the shopping list... \n")
                add_shopping_list(next_step)
                break


def check_ingredients(data):
    """
    Checks ingredient requirement against inventory to see
    whether required amount is present.
    Returns False if ingredients are available, else create a shopping list.
    """
    recipe_ing_sheet = SHEET.worksheet("recipes_ing")
    ing_col_num = recipe_ing_sheet.find(data)  # Get column number of the recp
    get_ing_list = recipe_ing_sheet.col_values(ing_col_num.col)  # Get req ing.
    ingredient_list = []
    for index in range(1, len(get_ing_list)):
        new_data = get_ing_list[index].split()
        ingredient_list.append(new_data)
    to_shop = []
    shortage_amount = {}
    inventory_sheet = SHEET.worksheet("inventory")
    print()
    print("Checking ingredients....")
    print("*" * 30)
    for items in ingredient_list:
        ingredient_amount = int(items[1])
        inv_search = inventory_sheet.find(items[0])
        inventory_amount = int(inventory_sheet.cell(inv_search.row, 2).value)
        if ingredient_amount > inventory_amount:
            shortage = ingredient_amount - inventory_amount
            print(f"** {items[0].upper()}: Required- {ingredient_amount}{items[2]} Short By: {shortage}{items[2]}")
            shortage_amount[items[0]] = f"{shortage}{items[2]}"
        else:
            print(f"{items[0].upper()}: Required- {ingredient_amount}{items[2]}: Available")
    if shortage_amount:
        to_shop.append(shortage_amount)
        return shortage_amount
    return False


def add_shopping_list(shopping: dict):
    """
    Adds the required short amount of ingredients to the shopping list
    """
    # print(shopping)
    shopping_list_sheet = SHEET.worksheet("shopping_list")
    for ingredients, amount in shopping.items():
        append_list = [ingredients, amount]
        shopping_list_sheet.append_row(append_list)
    print("Shopping list updated..")


# ---- INVENTORY FUNCTIONS ----
def check_inventory():
    """
    Fetch a list of all the available items and their amount in the inventory.
    Lets the user to add or edit items in the inventory
    """
    print("Fetching the inventory details...\n")
    print("Available items:\n")
    fetch_inventory()
    print("-" * 30)
    print("Would you like to make changes to the inventory? y/n")
    while True:
        user_choice = input(">\n")
        if validate_yes_no(user_choice):
            if user_choice.lower() == "y":
                print()
                print("*" * 30)
                print("* Please type the ingredient name, amount and unit separated by space.")
                print("* For eg: tomato 200 g")
                print("* If ingredient has two words, use separator '-' or it might duplicate")
                print("* For eg: green-chilli 5 pc")
                print("* Press 0 to exit")
                print("*" * 30)
                update_inventory()
                break

            break
    main_menu = input("Would you like to go back to the main menu? y/n:\n")
    while True:
        if validate_yes_no(main_menu):
            if main_menu.lower() == "y":
                print()
                main()
                break
            break
        main_menu = input(":\n")


def fetch_inventory():
    """
    Access the inventory worksheet and gets the list
    """
    inventory_data = INV_LIST.get_all_values()
    for serial, items in enumerate(inventory_data):
        print(f"{serial+1}: {items[0].capitalize()} - {items[1]}{items[2]}")


def update_inventory():
    """
    Updates the inventory with user's input
    """
    inventory_items = INV_LIST.col_values(1)
    user_input = input(">\n")
    while user_input != "0":
        input_list = user_input.split()
        if validate_invnetory_input(input_list):
            if input_list[0] in inventory_items:
                print()
                print("Updating...")
                get_row_number = INV_LIST.find(input_list[0])
                INV_LIST.update_cell(get_row_number.row, 2, input_list[1])
                INV_LIST.update_cell(get_row_number.row, 3, input_list[2])
                print("Updated \n")
            else:
                print()
                print("Adding...")
                INV_LIST.append_row(input_list)
                print("Added \n")

        user_input = input(">\n")
    print("*" * 30)
    print("Inventory Updated! \n")
    print("*" * 30)


# ---- SHOPPING LIST FUNCTIONS ----
def check_shopping_list():
    """
    Fetches the shopping list and provide options to add/remove items
    or clear the list.
    """
    shopping_list = SHOPPING_WORKSHEET.get_all_values()
    print("Checking Shopping List...\n")
    if len(shopping_list) == 0:
        print("** Shopping list is empty. **")
    else:
        for index, items in enumerate(shopping_list):
            print(f"{index + 1}. {items[0].capitalize()}: {items[1]}")

    print()
    print("What would you like to do?")
    shopping_list_options()
    print()
    print("Select Option Number as 1, 2, 3, 4")
    while True:
        user_choice = input(">\n")
        if validate_shopping_list_options(user_choice):
            if user_choice == "1":
                add_items()
            elif user_choice == "2":
                remove_items()
            elif user_choice == "3":
                clear_list()
            else:
                break
            break
    main_menu = input("Would you like to go back to the main menu? y/n:\n")
    while True:
        if validate_yes_no(main_menu):
            if main_menu.lower() == "y":
                print()
                main()
                break
            break
        main_menu = input(":\n")


def add_items():
    """
    Lets user to add items to the shopping list.
    """
    print()
    print("*" * 30)
    print("* Please type in the item and amount as prompted.")
    print("* Press 0 to exit.\n")
    continue_add = "y"
    while continue_add != "n":
        item_list = []
        if validate_yes_no(continue_add):
            item_name = input("Name of the item:\n")
            if item_name == "0":
                pass
            else:
                item_list.append(item_name)
                item_amount = input("Amount to buy:\n")
                item_list.append(item_amount)
                SHOPPING_WORKSHEET.append_row(item_list)
                print()
                print("Added!\n")
        continue_add = input("Do you want to continue? y/n:\n")
        print()


def remove_items():
    """
    Lets user to remove items from the shopping list.
    """
    shopping_list = SHOPPING_WORKSHEET.get_all_values()
    if len(shopping_list) == 0:
        print()
        print("** No items found to remove. **")
        print()
    else:
        print()
        print("*" * 30)
        print("You are choosing to delete items from the Shopping List.")
        print("If there are duplicate items, it'll remove the last one added.")
        print("Press 0 to exit or 'n' when prompted")
        print("*" * 30)
        continue_remove = "y"
        while continue_remove != "n":
            if validate_yes_no(continue_remove):
                item_to_remove = input("What would you like to remove?\n")
                while True:
                    if item_to_remove == "0":
                        break
                    elif validate_remove_item(item_to_remove):
                        item_row = SHOPPING_WORKSHEET.findall(item_to_remove)
                        SHOPPING_WORKSHEET.delete_rows(item_row[-1].row)
                        print()
                        print("Item Removed.")
                        break
                    item_to_remove = input(">")
            continue_remove = input("Do you want to continue? y/n:\n")
            print()


def clear_list():
    """
    Lets user to clear the Shopping List.
    """
    print()
    print("*** WARNING: This will clear the whole shopping list. ***")
    while True:
        list_clear = input("Do you want to continue? y/n:\n")
        if validate_yes_no(list_clear):
            if list_clear.lower() == "y":
                SHOPPING_WORKSHEET.clear()
                print("*" * 30)
                print("Shopping List cleared!")
                print("*" * 30)
            break
        print()


def shopping_list_options():
    """
    Contains and prints services provided for Shopping List.
    """
    options = ["Add Items", "Remove Items", "Clear List", "Main Menu"]
    for index, items in enumerate(options):
        print(f"{index + 1}: {items}")


# ---- VALIDATION FUNCTIONS ----
def validate_service_choice(user_input):
    """
    Validate the user's choice for the services offered.
    """
    try:
        int(user_input)
        if int(user_input) not in range(0, 4):
            raise ValueError(
                f"{user_input} not a valid option"
            )
    except ValueError as error:
        print(f"Invalid Data: {error}. Please choose an available service.")
        print()
        return False
    return True


def validate_yes_no(choice):
    """
    Validates user's answers for Yes/No queries.
    """
    try:
        if choice.lower() != "y" and choice.lower() != "n":
            raise ValueError(
                f"choice: {choice} not valid. Please answer as 'y' or 'n'"
            )
    except ValueError as choice_error:
        print(f"Invalid Data: {choice_error}")
        print()
        return False
    return True


def validate_recipe_choice(recipe_choice):
    """
    Validate the user's choice of recipe against the available list of recipe.
    """
    recipe_list_sheet = SHEET.worksheet("recipes_list")
    available_recipes = recipe_list_sheet.col_values(1)
    try:
        if recipe_choice not in available_recipes:
            raise ValueError(
                f"Sorry, recipe for {recipe_choice} not available"
            )
    except ValueError as recipe_error:
        print(f"Invalid chocie: {recipe_error}. Please choose from the list")
        print()
        return False
    return True


def validate_invnetory_input(data):
    """
    Validates the inventory data input by the user
    """
    try:
        if len(data) != 3:
            raise ValueError(
                f"Input Data Invalid: {len(data)} items found out of 3."
            )
    except ValueError as inventory_error:
        print(f"{inventory_error} Input the data as 'item amount unit'")
        print()
        return False
    return True


def validate_shopping_list_options(user_input):
    """
    Validates the user input for Shopping List services.
    """
    try:
        transform_data = int(user_input)
        if transform_data not in range(1, 5):
            raise ValueError(
                f"You selected {user_input}, which does not exist."
            )
    except ValueError as shop_list_error:
        print(f"Invalid Input: {shop_list_error}. Please choose from the list")
        print()
        return False
    return True


def validate_remove_item(items):
    """
    Checks whether the item to be removed from the list exists.
    Returns true if the item is on the list, else returns an error.
    """
    shopping_items_list = SHOPPING_WORKSHEET.col_values(1)
    try:
        if items not in shopping_items_list:
            raise ValueError(
                f"{items} not on the list. Please choose an item from the list to remove."
            )
    except ValueError as remove_error:
        print(f"Invalid Input: {remove_error}")
        print()
        return False
    return True


# ---- INTIAL EXECUTING FUNCTIONS ----
def list_of_services():
    """
    Generate all the services provided by the program.
    """
    services = ["Check Recipe", "Check Inventory",
                "Check Shopping List", "Exit"]
    for nos, service in enumerate(services):
        if service == "Exit":
            print("0: Exit")
        else:
            print(f"{nos+1}: {service}")


def main():
    """
    Initial messages and codes to execute on the program launch
    """
    while True:
        print("*" * 30)
        print("What would you like to do?")
        print("Choose a service as 1, 2, 3, 4")
        print("*" * 30)
        list_of_services()
        service_choice = input(">\n")
        print("*" * 30)
        if validate_service_choice(service_choice):
            if service_choice == "1":
                fetch_recipe_list()
                break
            elif service_choice == "2":
                check_inventory()
                break
            elif service_choice == "3":
                check_shopping_list()
                break
            else:
                break


print("Hi there!")
print("Welcome to your personal kitchen assistant!")
main()
print("*" * 30)
print("See you again!")
print("*" * 30)
print("*" * 30)
