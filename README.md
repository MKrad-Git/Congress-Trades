# Insider Trading Algorithm
---
### The Basics:
This looks at all the SEC Filings by Congress. It has several editable parameters to narrow your search. These fillings are used to automate trades on your Robbinhood account. There is a risk variable that allows you to change what amount to invest in each stock. This risk is a fraction of what a congress person invested in the same stock. you can change what options you want to look at, over what period, and what politcal party as well.

---
### Setup:
I reccomend commenting out the everything in main except get_stocks() and Stock.print_all_instances() and running it once to see what the output looks like and then you can see what you want to do with the data, ajust any of the parameters you need to get your expected output then you can run it for real. If you make changes to the code make sure to delete the stock_info file or modify to match the changes. If you dont do this you can run into unexpected errors. for example changing the risk will cause their to be two of the same trade just under different prices in the document and thus the code will trade it twice.

---
### Liability:
I am not liable for any damages financial or otherwise from using this code. You assume full responsibilty for any actions you choose to use this for.