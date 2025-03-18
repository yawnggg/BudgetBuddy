from expense import Expense
import datetime
import calendar
import pandas as pd
import re

def main():
    print(f"Running Expense Tracker!")
    expense_file_path = "expenses.csv"
    budget = 2000

    while True:
        expense = get_user_expense()
        save_expense_to_file(expense, expense_file_path)
        summary = summarize_expenses(expense_file_path, budget)
        print_summary(summary)

        cont = input("Would you like to add another expense? (y/n): ").strip().lower()
        if cont != 'y':
            print("\nExiting Expense Tracker. Have a great day!")
            break


def get_user_expense():
    print(f"Getting User Expense...")
    expense_name = input("Enter expense name: ")

    while True:
        user_input = input("Enter expense amount: ")

        if re.match(r'^\d+(\.\d{1,2})?$', user_input):
            expense_amount = float(user_input)
            break
        else:
            print("Invalid amount. Please enter a number with up to two decimal places (e.g., 12.34).")

    expense_categories = [
        "Food 🍔", 
        "Home 🏠", 
        "Work 💼", 
        "Fun 🎉", 
        "Misc ✨"
    ]
    
    while True:
        print("Select a category: ")
        for i, category_name in enumerate(expense_categories):
            print(f"  {i + 1}. {category_name}")

        try:
            selected_index = int(input(f"Enter a category number [1 - {len(expense_categories)}]: ")) - 1
            if 0 <= selected_index < len(expense_categories):
                selected_category = expense_categories[selected_index]
                new_expense = Expense(
                    name=expense_name, category=selected_category, amount=expense_amount
                )
                return new_expense
            else: 
                print("Invalid category. Please try again!")
        except ValueError:
            print("Invalid input. Please enter a valid category value.")
    

def save_expense_to_file(expense: Expense, expense_file_path):
    print(f"Saving User Expense: {expense} to {expense_file_path}")

    columns = ["name", "amount", "category"]
    
    try:
        df = pd.read_csv(expense_file_path)
        if list(df.columns) != columns:
            print("CSV file is missing headers. Fixing file format...")
            df = pd.DataFrame(columns=columns)
            df.to_csv(expense_file_path, index=False)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=columns)
        df.to_csv(expense_file_path, index=False)

    new_data = pd.DataFrame([[expense.name, expense.amount, expense.category]], columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(expense_file_path, index=False)


def summarize_expenses(expense_file_path, budget):
    print(f"Summarizing User Expense")

    try:
        df = pd.read_csv(expense_file_path)
    except FileNotFoundError:
        print("No expenses recorded yet.")
        return {}
    
    # Grouping expense by category
    expense_summary = df.groupby("category")["amount"].sum().to_dict()

    # Computing total spent and remaining budget
    total_spent = sum(expense_summary.values())
    remaining_budget = budget - total_spent
    
    # Get remaining days in the month
    today = datetime.datetime.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]    
    remaining_days = days_in_month - today.day
    daily_budget = remaining_budget / remaining_days if remaining_days > 0 else 0

    return {
        "expenses_by_category": expense_summary,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "remaining_days": remaining_days,
        "budget_per_day": daily_budget
    }

def print_summary(summary):
    if not summary:
        return

    print("Expenses by Category: ")

    # for category, amount in summary["expenses_by_category"].items():
    #     print(f"  {category}: ${amount:.2f}")

    # New method for printing categories with amounts (instead of using a for loop)
    df_summary = pd.DataFrame(list(summary["expenses_by_category"].items()), columns=["Category", "Amount ($)"])
    print(df_summary.to_string(index=False))

    print(f"\nTotal Spent: ${summary['total_spent']:.2f}")
    print(f"Budget Remaining: ${summary['remaining_budget']:.2f}")
    print(f"Remaining days in the current month: {summary['remaining_days']}")

    if summary['remaining_days'] > 0:
        print(f"Budget Per Day 👉: ${summary['budget_per_day']:.2f}")


if __name__ == "__main__":  # By putting this condition, we stop the app from running main() if expense_tracker.py is ever imported into another class. This condition will only be true (and main() will only run) when it is run directly as a file
    main()