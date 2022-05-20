import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("kitchen_assistant")

# recepie = SHEET.worksheet("recipes")
# recepie_list = SHEET.worksheet("recipes_list")
# validation = recepie_list.col_values(1)
# user_req = input("What you want to cook today? ")
# if user_req in validation:
#     rec_col = recepie.find(user_req)
#     datas = recepie.col_values(rec_col.col)
#     # print(f"Steps for {datas[0].capitalize()}")
#     for no,step in enumerate(datas):
#         if no == 0:
#             print(f"Steps for {datas[0].capitalize()}")
#         else:
#             print(f"{no}: {step}")
# else:
#     print("Not ofund")
# -----------------------------------------------------------------------------


# ---- RECIPE FUNCTIONS ----
def fetch_recipe_list():
    """
    Fetch and displays all the available recipes.
    """
    available_recipe_data = SHEET.worksheet("recipes_list")
    recipe_list = available_recipe_data.col_values(1)
    for nos, recipe in enumerate(recipe_list):
        print(f"{nos+1}: {recipe.capitalize()}")
    print("*" * 10)
    while True:
        user_cook = input("Would you like to cook today?(y/n)  ")
        print()
        if validate_yes_no(user_cook):
            if user_cook.lower() == "y":
                fetch_recipe_steps()
                print("*" * 30)
                break
            else:
                break
    main_menu = input("Would you like to go back to the main menu? y/n: ")
    while True:
        if validate_yes_no(main_menu):
            if main_menu.lower() == "y":
                main()
            break
        main_menu = input(": ")


def fetch_recipe_steps():
    """
    Fetch the steps for the user's chosen recipe
    """
    print("*" * 20)
    while True:
        food_choice = input("What would you like to cook today? ")
        if validate_recipe_choice(food_choice.lower()):
            next_step = check_ingredients(food_choice)
            if next_step is False:
                recipe_step_list = SHEET.worksheet("recipes")
                search_recipe = recipe_step_list.find(food_choice.lower())
                recipe_col = recipe_step_list.col_values(search_recipe.col)
                for step_no, step in enumerate(recipe_col):
                    if step_no == 0:
                        print(f"Recipe for {step.capitalize()}:")
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
    Checks ingredient requirement against inventory to see whether required amount is present.
    Returns True if ingredients are available, else create a shopping list.
    """
    recipe_ing_sheet = SHEET.worksheet("recipes_ing")
    ing_col_num = recipe_ing_sheet.find(data)  # Get column number of the recipe
    get_ing_list = recipe_ing_sheet.col_values(ing_col_num.col)  # Get data of req ing.
    ingredient_list = []
    for index in range(1, len(get_ing_list)):
        new_data = get_ing_list[index].split()
        ingredient_list.append(new_data)
    to_shop = []
    shortage_amount = {}
    inventory_sheet = SHEET.worksheet("inventory")
    print("Checking ingredients....")
    for items in ingredient_list:
        ingredient_amount = int(items[1])
        inventory_search = inventory_sheet.find(items[0])
        inventory_amount = int(inventory_sheet.cell(inventory_search.row, 2).value)
        if ingredient_amount > inventory_amount:
            shortage = ingredient_amount - inventory_amount
            print(f"{items[0].upper()}: Required- {ingredient_amount}{items[2]} Short By: {shortage}{items[2]}")
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


# ---- INGREDIENT FUNCTIONS ----
def check_inventory():
    """
    Fetch a list of all the available items and their amount in the inventory.
    Lets the user to add or edit items in the inventory
    """
    print("Fetching the inventory details...\n")
    print("Available items:\n")
    fetch_inventory()
    print("-" * 25)
    print("Would you like to make changes to the inventory? y/n")
    while True:
        user_choice = input("> ")    
        if validate_yes_no(user_choice):
            if user_choice.lower() == "y":
                print("Please type the ingredient name, amount and unit separated by space.")
                print("For eg: tomato 200 g")
                print("If ingredient has two words, use separator '-' or it might duplicate")
                print("For eg: green-chilli 5 pc")
                print("Press 0 to exit")
                update_inventory()
                break
           
            break
    main_menu = input("Would you like to go back to the main menu? y/n: ")
    while True:
        if validate_yes_no(main_menu):
            if main_menu.lower() == "y":
                main()
            break
        main_menu = input(": ")


def fetch_inventory():
    """
    Access the inventory worksheet and gets the list
    """
    global inventory_list
    inventory_list = SHEET.worksheet("inventory") 
    inventory_data = inventory_list.get_all_values()
    for serial, items in enumerate(inventory_data):
        print(f"{serial+1}: {items[0].capitalize()} - {items[1]}{items[2]}")


def update_inventory():
    """
    Updates the inventory with user's input
    """
    inventory_items = inventory_list.col_values(1)
    user_input = input("> ")
    while user_input != "0":
        input_list = user_input.split()
        if validate_invnetory_input(input_list):
            if input_list[0] in inventory_items:
                print("Updating...")
                get_row_number = inventory_list.find(input_list[0])
                inventory_list.update_cell(get_row_number.row, 2, input_list[1])
                inventory_list.update_cell(get_row_number.row, 3, input_list[2])
                print("Updated \n")
            else:
                print("Adding...")
                inventory_list.append_row(input_list)
                print("Added \n")
            
        user_input = input("> ")
    print("Inventory Updated! \n")


def list_of_services():
    """
    Generate all the services provided by the program.
    """
    services = ["Check Recipe", "Check Inventory", "Check Shopping List", "Exit"]
    for nos, service in enumerate(services):
        if service == "Exit":
            print("0: Exit")
        else:
            print(f"{nos+1}: {service}")


# ---- VALIDATION FUNCTIONS ----
def validate_service_choice(user_input):
    """
    Validate the user's choice for the services offered.
    """
    try:
        int(user_input)
        if int(user_input) not in range(0, 4):
            raise ValueError(
                f"{user_input} not a valid option. Please choose a service from the list."
            )
    except ValueError as error:
        print(f"Invalid Data: {error}")
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
                f"Sorry, recipe for {recipe_choice} not available. Please choose one from the list"
            )
    except ValueError as recipe_error:
        print(f"Invalid chocie: {recipe_error}")
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
        return False
    return True


def main():
    """
    Initial messages and codes to execute on the program launch
    """
    # user_input = ""
    while True:
        print("What would you like to do?")
        list_of_services()
        service_choice = input(": ")
        print("*" * 20)
        if validate_service_choice(service_choice):
            if service_choice == "1":
                fetch_recipe_list()
                break
            elif service_choice == "2":
                check_inventory()
                break
            elif service_choice == "3":
                print("You chose Shopping List")
                break
            else:
                break


print("Hi there!")
print("Welcome to you personal kitchen assistant!")
main()
print("See you again!")
