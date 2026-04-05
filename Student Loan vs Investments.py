import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

INITIAL_INVEST_Y1 = 17_500
ADDITIONAL_INV_Y2 = 12_500
ADDITIONAL_INV_Y3 = 12_500

BORROW_A = 17_835
BORROW_B = 5_000
BORROW_C = 9_525
INVEST_C_START = 5_000
INVEST_C_PER_YEAR = 5_000

HORIZON_YEARS = 3
DT = 1/12
MU = 0.07
SIGMA = 0.18
N_SIMS = 10000
SEED = None

# data from https://www.statista.com/statistics/285203/percentage-change-of-the-retail-price-index-rpi-in-the-uk/
HIST_RPI_YEARS = np.arange(2015, 2026)
HIST_RPI = np.array([0.9, 1.6, 3.1, 3.3, 2.4, 2.6, 1.5, 9, 13.5, 4.3, 3.2])

def forecast_rpi_stochastic(years_forward=3, n_sims=N_SIMS, seed=SEED):
    X = HIST_RPI_YEARS.reshape(-1,1)
    y = HIST_RPI.reshape(-1,1)
    model = LinearRegression().fit(X,y)
    future_years = np.arange(HIST_RPI_YEARS[-1]+1,HIST_RPI_YEARS[-1]+1+years_forward).reshape(-1,1)
    preds = model.predict(future_years).flatten()
    residuals = y.flatten() - model.predict(X).flatten()
    sigma_rpi = np.std(residuals)/100
    if seed is not None:
        np.random.seed(seed)
    rpi_paths = np.zeros((n_sims, years_forward))
    for i in range(n_sims):
        shocks = np.random.normal(0, sigma_rpi, years_forward)
        rpi_paths[i,:] = np.maximum(preds/100 + shocks, 0)
    return rpi_paths

def simulate_gbm_monthly(n_sims, mu, sigma, dt, months, seed=None):
    if seed is not None:
        np.random.seed(seed)
    dW = np.random.normal(0, np.sqrt(dt), (n_sims, months))
    S = np.ones((n_sims, months+1))
    for t in range(1, months+1):
        S[:,t] = S[:,t-1]*np.exp((mu-0.5*sigma**2)*dt + sigma*dW[:,t-1])
    return S

def compute_portfolio(multipliers, contrib_month_idx, contributions):
    n_sims = multipliers.shape[0]
    final_idx = multipliers.shape[1]-1
    total = np.zeros(n_sims)
    for month, amount in zip(contrib_month_idx, contributions):
        total += amount * multipliers[:,final_idx] / multipliers[:,month]
    return total

def loan_path_mc(borrow_per_year, rpi_paths):
    n_sims = rpi_paths.shape[0]
    years = len(borrow_per_year)
    balances = np.zeros((n_sims, years))
    loan = np.zeros(n_sims)
    for t in range(years):
        loan += borrow_per_year[t]
        loan *= (1 + rpi_paths[:,t])
        balances[:,t] = loan
    return balances

def run_simulation():
    rpi_paths = forecast_rpi_stochastic(HORIZON_YEARS, N_SIMS, SEED)
    months_total = int(HORIZON_YEARS/DT)
    multipliers = simulate_gbm_monthly(N_SIMS, MU, SIGMA, DT, months_total, SEED)

    contrib_months_A = [0, int(1/DT), int(2/DT)]
    contribs_A = [INITIAL_INVEST_Y1, ADDITIONAL_INV_Y2, ADDITIONAL_INV_Y3]
    portfolio_A = compute_portfolio(multipliers, contrib_months_A, contribs_A)
    debt_path_A = loan_path_mc([BORROW_A]*3, rpi_paths)
    debt_A = debt_path_A[:,-1]
    net_A = portfolio_A - debt_A

    debt_path_B = loan_path_mc([BORROW_B]*3, rpi_paths)
    debt_B = debt_path_B[:,-1]
    net_B_value = -debt_B

    contrib_months_C = [0, int(1/DT), int(2/DT)]
    contribs_C = [INVEST_C_START, INVEST_C_PER_YEAR, INVEST_C_PER_YEAR]
    portfolio_C = compute_portfolio(multipliers, contrib_months_C, contribs_C)
    debt_path_C = loan_path_mc([BORROW_C]*3, rpi_paths)
    debt_C = debt_path_C[:,-1]
    net_C = portfolio_C - debt_C

    plt.figure(figsize=(10,6))
    plt.hist(net_A, bins=80, alpha=0.5, label='Scenario A (Leveraged Investing)')
    plt.hist(net_C, bins=80, alpha=0.5, label='Scenario C (Partial Invest / Moderate Debt)')
    plt.hist(net_B_value, bins=80, alpha=0.5, label='Scenario B (Borrow Only)')
    plt.title("Monte Carlo Net Wealth Distribution after 3 Years")
    plt.xlabel("Net Wealth (£)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.show()

    def summarize(arr, label):
        mean = np.mean(arr)
        median = np.median(arr)
        p5 = np.percentile(arr,5)
        p95 = np.percentile(arr,95)
        prob_pos = np.mean(arr>0)
        print(f"--- {label} ---")
        print(f"Mean net wealth: £{mean:,.2f}")
        print(f"Median net wealth: £{median:,.2f}")
        print(f"5th percentile: £{p5:,.2f}")
        print(f"95th percentile: £{p95:,.2f}")
        print(f"Probability(net>0): {prob_pos*100:.2f}%\n")
    summarize(net_A,"Scenario A")
    print(f"--- Scenario B ---\nMean net wealth: £{np.mean(net_B_value):,.2f}")
    summarize(net_C,"Scenario C")

    print("Year | Debt A       | Debt B       | Debt C")
    for i in range(HORIZON_YEARS):
        print(f"{i+1:<4} | £{np.mean(debt_path_A[:,i]):,.2f} | £{np.mean(debt_path_B[:,i]):,.2f} | £{np.mean(debt_path_C[:,i]):,.2f}")

    return net_A, net_B_value, net_C

if __name__=="__main__":
    net_A, net_B, net_C = run_simulation()
