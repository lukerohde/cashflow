from datetime import date, datetime, timedelta
from io import StringIO
import os
import csv
import matplotlib.pyplot as plt



class Application:
    def __init__(self):
        # Initialize any necessary variables or resources here
        pass

    def get_transactions(self, key, data_dict):
        return [{"description": desc, "amount": amt} for desc, amt in data_dict.get(key, {}).items()]

      # Functions to determine the appropriate key for each interval type
    def get_weekly_key(self, date):
        return date.weekday()

    def get_fortnightly_key(self, date, data_dict):
        matching_dates = [start_date for start_date in data_dict.keys() if (date - datetime.strptime(start_date, '%Y-%m-%d').date()).days % 14 == 0]
        return str(matching_dates[0]) if matching_dates else None

    def get_monthly_key(self, date):
        # to do only match transactions for the weekend on or after the weekend
        
        return date.day
      
    def get_monthly_transactions(self, date, data):
        # bring weekend transactions forward to Friday
        if date.weekday() == 5 or date.weekday() == 6:
            return []
        elif date.weekday() == 4:
            return self.get_transactions(self.get_monthly_key(date), data) + \
                self.get_transactions(self.get_monthly_key(date + timedelta(days=1)), data) + \
                self.get_transactions(self.get_monthly_key(date + timedelta(days=2)), data)
        
        return self.get_transactions(self.get_monthly_key(date), data)
      
    # Function to build up the statement
    def get_statement(self, data, start_date, end_date, initial_balance):
        transactions = []
        date = start_date
        balance = initial_balance
        while date < end_date:
            # Retrieve transactions for the day
            daily_income_transactions = self.get_transactions(self.get_weekly_key(date), data["weekly_income"]) + \
                                 self.get_transactions(self.get_fortnightly_key(date, data["fortnightly_income"]), data["fortnightly_income"]) + \
                                 self.get_monthly_transactions(date, data["monthly_income"])
                                 #self.get_transactions(self.get_monthly_key(date), data["monthly_income"])
                                 
            daily_expense_transactions = self.get_transactions(self.get_weekly_key(date), data["weekly_expense"]) + \
                                 self.get_transactions(self.get_fortnightly_key(date, data["fortnightly_expense"]), data["fortnightly_expense"]) + \
                                 self.get_transactions(self.get_monthly_key(date), data["monthly_expense"])
            
            # Add transactions to the list and update the balance
            for trans in daily_income_transactions:
                t = {}
                t["date"] = date
                t["description"] = trans["description"]
                t["credit"] = trans["amount"]
                t["debit"] = 0
                balance +=  trans["amount"]
                t["balance"] = round(balance)
                transactions.append(t)
                
            for trans in daily_expense_transactions:
                t = {}
                t["date"] = date
                t["description"] = trans["description"]
                t["credit"] = 0
                t["debit"] = trans["amount"]
                balance -=  trans["amount"]
                t["balance"] = round(balance)
                transactions.append(t)
            
            date += timedelta(days=1)
        
        return transactions
      
  
    # Function to generate CSV from the statement
    def generate_csv(self, transactions):
        output = StringIO()
        fieldnames = ["date", "description", "credit", "debit", "balance"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for trans in transactions:
            writer.writerow(trans)
        
        return output.getvalue() 
            
    
    def plot_running_balance(self, data, title):
        
        # Extract dates and balances
        dates = [entry['date'] for entry in data]
        balances = [entry['balance'] for entry in data]

        # Plot the data
        plt.figure(figsize=(10, 6))
        # plt.plot(dates, balances, color='blue', linestyle='-', linewidth=2)
        # plt.plot(dates, balances, marker='o', markersize=3, markerfacecolor='red')
        plt.title(title, fontsize=16)
        plt.plot(dates, balances)
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Balance', fontsize=14)
        plt.tight_layout()
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(True)
        plt.subplots_adjust(bottom=0.2, left=0.1)
        plt.style.use('fivethirtyeight')
        
        plt.savefig("output.png")
      
    def start(self, config, start_date, end_date, start_balance):
        # Generate the statement
        statement = self.get_statement(config, start_date, end_date, start_balance)

        # Find the minimum balance
        min_balance = min(trans["balance"] for trans in statement)

        # Generate the CSV
        csv_output = self.generate_csv(statement)

        for line in csv_output.split("\n"):
            parts = line.split(",")
            
            if len(parts) == 5:
                formatted_line = "{:<10} {:<18}{:>10}{:>10}{:>10}".format(parts[0], parts[1], parts[2], parts[3], parts[4])
            
            # Call the function with sample data
            
            print(formatted_line)
        
        title = f"Opening Balance: {start_balance} Minimum Balance: {min_balance}"
        print(title)
        
        self.plot_running_balance(statement, title)


    
    
    def close(self):
        # Write code to cleanly close the application here
        pass