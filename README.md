# YNAB-Venmo integration

I used YNAB to track my finances and can't live without it. I often use Venmo to split transactions between friends, but I have to manually enter all transactions. Venmo discontinued its API in 2016, so an API connection directly between the two services is impossible. 
To work around this, I set up an email address that all my Venmo notifications are forwarded to.

## To Run

```
conda activate ynabvenmo
python3 main.py --real
```


## Setup 

1. Create a new Gmail account. Set up a forwarding filter on the email account that's connected to your Venmo so that all emails from `venmo@venmo.com` are forwarded to this Gmail. 

2. In the root folder of the repo, run 
