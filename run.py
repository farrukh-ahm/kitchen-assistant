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
#--------------------------------------------------------------------------------------------------


def fetch_recipe_list():
    """
    Fetch and displays all the available recipes.
    """
    available_recipe_data = SHEET.worksheet("recipes_list")
    recipe_list = available_recipe_data.col_values(1)
    for nos, recipe in enumerate(recipe_list):
        print(f"{nos+1}: {recipe.capitalize()}")
    print("*" * 10)
    user_cook = input("Would you like to cook today?(y/n)  ")
    print()
    # ADD VALIDATION FUNCTION HERE
    if user_cook.lower() == "y":
        fetch_recipe_steps()
    else:
        main()


def fetch_recipe_steps():
    """
    Fetch the steps for the user's chosen recipe
    """
    food_choice = input("What would you like to cook today? ")
    print("*" * 20)
    # ADD VALIDATION FUNCTION HERE
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
        print("*" * 20)
    else:
        print()
        print("Not all ingredients available \n")
        print("Adding to the shopping list... \n")
        add_shopping_list(next_step)
    main()


def check_ingredients(data):
    """
    Check ingredients requirement against inventory to see whether required amount is present.
    Returns True is ingredients are available, else create a shopping list.
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
            print(f"{items[0]} short by {shortage}{items[2]}")
            shortage_amount[items[0]] = f"{shortage}{items[2]}"
        else:
            print(f"{items[0]}: Available")
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
    print("*" * 20)


def list_of_services():
    """
    Generate all the services provided by the program.
    """
    services = ["Check Recipe", "Check Ingredients", "Check Shopping List", "Exit"]
    for nos, service in enumerate(services):
        if service == "Exit":
            print("0: Exit")
        else:
            print(f"{nos+1}: {service}")


def main():
    """
    Initial messages and codes to execute on the program launch
    """
    user_input = ""
    while user_input != "0":
        print("What would you like to do?")
        list_of_services()
        user_input = input(": ")
        # ADD FUNCTION TO VALIDATE INPUT HERE
        print("*" * 20)
        if user_input == "1":
            fetch_recipe_list()
            break
        elif user_input == "2":
            print("You chose Check Ingredients")
            break
        elif user_input == "3":
            print("You chose Shopping List")
            break
        else:
            break


print("Hi there!")
print("Welcome to you personal kitchen assistant!")
main()
print("See you again!")
