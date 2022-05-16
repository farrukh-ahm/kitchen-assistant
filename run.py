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
    recipe_step_list = SHEET.worksheet("recipes")
    search_recipe = recipe_step_list.find(food_choice.lower())
    recipe_col = recipe_step_list.col_values(search_recipe.col)
    for step_no, step in enumerate(recipe_col):
        if step_no == 0:
            print(f"Recipe for {step.capitalize()}:")
        else:
            print(f"{step_no}: {step}")
    main()


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