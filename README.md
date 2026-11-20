# Investment-Project
Portfolio optimisation for deciding investment vs student loan 
Monte Carlo Student Loan vs Investment Simulator
Simulates whether it makes more sense to invest while carrying student debt or to minimise borrowing, given that UK student loans are linked to RPI. Runs 10,000 Monte Carlo paths over a 3-year horizon and compares the net wealth outcomes across three scenarios.
The question
UK maintenance loans accrue interest tied to RPI, which has been volatile in recent years. If you're going to carry the debt anyway, does it make sense to invest the money and hope equity returns outpace the inflation-linked interest? Or are you better off borrowing as little as possible?
This script models three approaches:

Scenario A (Leveraged investing): Borrow the full amount each year (£17,835) and invest aggressively (£17,500 up front, then £12,500 in years 2 and 3).
Scenario B (Borrow only): Borrow £5,000/year, don't invest anything. Baseline for comparison.
Scenario C (Middle ground): Borrow £9,525/year and invest £5,000/year. A more moderate approach.

How it works
Stock returns are modelled as geometric Brownian motion with monthly steps:

Expected return (μ): 7%
Volatility (σ): 18%

RPI (loan interest) is forecast stochastically- a linear regression is fitted on historical UK RPI data (2015–2025, sourced from Statista), and then random noise based on the residual standard deviation is added to the trend for each simulation path. This means each of the 10,000 runs sees a different combination of market returns and inflation.
At the end of 3 years, net wealth = portfolio value - outstanding debt.
What it outputs

Histogram of net wealth distributions for all three scenarios
Summary stats for each: mean, median, 5th/95th percentiles, probability of ending up net positive
Year-by-year average debt progression

Setup
Needs Python 3.9+ and:
numpy
matplotlib
scikit-learn
Then just run:
bashpython monte_carlo_sim.py
No external data files needed- the historical RPI values are hardcoded in the script.
Assumptions and caveats

The GBM parameters (7% drift, 18% vol) are rough proxies for a global equity index. They're not calibrated to any specific fund.
RPI forecasting via linear regression on 11 data points is pretty crude. The recent spike (2022-2023) has a big influence on the trend line.
Loan repayment mechanics aren't modelled- this only looks at the accumulation side, not what happens when you start repaying.
Contributions are modelled as lump sums at the start of each year, not spread monthly.
No taxes, platform fees, or fund charges are included.
