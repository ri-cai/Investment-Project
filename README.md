# Monte Carlo Student Loan vs Investment Simulator

Simulates whether it makes more sense to invest while carrying student debt or to minimise borrowing, given that UK student loans accrue interest linked to RPI. Runs 10,000 Monte Carlo paths over a 3-year horizon and compares net wealth across three scenarios.

## The question

UK maintenance loans accrue interest tied to RPI, which has been volatile in recent years. If you're going to carry the debt anyway, does it make sense to invest the money and hope equity returns outpace the inflation-linked interest? Or are you better off borrowing as little as possible?

## Scenarios

- **A (Leveraged investing):** borrow the full £17,835 each year and invest £17,500 up front, then £12,500 in years 2 and 3.
- **B (Borrow only):** borrow £5,000/year and invest nothing. Baseline for comparison.
- **C (Middle ground):** borrow £9,525/year and invest £5,000/year.

## How it works

Equity returns follow geometric Brownian motion with monthly steps, $\mu = 7\%$, $\sigma = 18\%$:

$$S_{t+\Delta t} = S_t \exp\left[\left(\mu - \tfrac{1}{2}\sigma^2\right)\Delta t + \sigma\sqrt{\Delta t}\,Z\right]$$

RPI is forecast stochastically: a linear trend is fitted to UK RPI (2015–2025, Statista), and Gaussian noise with the residual standard deviation is added on each path (floored at 0). Each of the 10,000 runs sees a different combination of market returns and inflation.

At the end of 3 years, net wealth = portfolio value − outstanding debt.

## Outputs

- Histogram of net wealth for all three scenarios
- Mean, median, 5th/95th percentiles and $P(\text{net} > 0)$
- Year-by-year average debt

## Setup

Python 3.9+.

```bash
pip install -r requirements.txt
python student_loan_vs_investments.py
```

No external data files needed; the historical RPI values are hardcoded in the script.

## Assumptions and caveats

- GBM parameters (7% drift, 18% vol) are rough proxies for a global equity index, not calibrated to a specific fund.
- RPI forecasting via a linear trend on 11 data points is crude, and the 2022–23 spike has a big influence on it.
- Repayment mechanics (income-contingent repayments, write-off) aren't modelled; this only covers the accumulation phase.
- Contributions are lump sums at the start of each year.
- No taxes, platform fees or fund charges.
