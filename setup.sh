#!/bin/bash

echo -e "\nThis script will set up the env vars for your YNAB-Venmo integration.\nHelp: https://github.com/hcussen/ynab-venmo\n"

# Get YNAB token
read -p "Please enter your YNAB token: " ynab_token

# Get Venmo account URL
echo -e "\nPlease navigate to your Venmo account in YNAB."
read -p "Paste the URL (format: https://app.ynab.com/{budgetID}/accounts/{accountID}): " url

# Extract budget and account IDs using regex
if [[ $url =~ app\.ynab\.com/([^/]+)/accounts/([^/]+) ]]; then
    budget_id="${BASH_REMATCH[1]}"
    account_id="${BASH_REMATCH[2]}"
else
    echo "Error: Invalid URL format"
    exit 1
fi

# Ask about development budget
while true; do
    read -p $'\nWould you like to set up a development budget? (y/n): ' dev_budget
    if [[ $dev_budget == "y" || $dev_budget == "n" ]]; then
        break
    fi
    echo "Please enter 'y' or 'n'"
done

# Create .env content
env_content="YNAB_TOKEN=$ynab_token
REAL_BUDGET_ID=$budget_id
REAL_ACCOUNT_ID=$account_id"

if [[ $dev_budget == "y" ]]; then
    echo -e "\nPlease navigate to your development Venmo account in YNAB."
    read -p "Paste the URL (format: https://app.ynab.com/{budgetID}/accounts/{accountID}): " dev_url
    
    if [[ $dev_url =~ app\.ynab\.com/([^/]+)/accounts/([^/]+) ]]; then
        dev_budget_id="${BASH_REMATCH[1]}"
        dev_account_id="${BASH_REMATCH[2]}"
        env_content="$env_content
DEV_BUDGET_ID=$dev_budget_id
DEV_ACCOUNT_ID=$dev_account_id"
    else
        echo "Error: Invalid development URL format"
        exit 1
    fi
fi

# Write to .env file
echo "$env_content" > .env

echo -e "\nSetup complete! .env file has been created."