import numpy as np

from risk_budgeting.business.model.riskbudgeting import RiskBudgetingParams
from risk_budgeting.business.model.solve import SolveParams


def median_absolute_deviation_method(
    rb_params: RiskBudgetingParams.__annotations__,
    solve_params: SolveParams.__annotations__,
    store: bool,
) -> SolveParams:
    # Initialize t
    if solve_params.t_init is None:
        t = np.dot(
            np.dot(solve_params.y, np.cov(solve_params.X, rowvar=False)), solve_params.y
        )

    else:
        t = solve_params.t_init
    y_ = [solve_params.y]
    t_ = [t]
    for s in range(solve_params.epochs):
        np.random.shuffle(solve_params.X)
        for i in range(0, solve_params.n, solve_params.minibatch_size):

            # Mini-batch
            x = solve_params.X[i:i + solve_params.minibatch_size]

            # Step size schedule
            eta_t = solve_params.eta_0_t / (1 + solve_params.k) ** solve_params.c
            eta_y = solve_params.eta_0_y / (1 + solve_params.k) ** solve_params.c

            # Gradient
            indicator_pos = (np.dot(solve_params.y, x.T) - t >= 0).reshape((x.shape[0], 1))
            indicator_neg = 1 - indicator_pos
            grad_t = np.mean(rb_params.beta * -1 * indicator_pos + indicator_neg)
            grad_y = np.mean(rb_params.beta * x * (
                    indicator_pos - indicator_neg) - rb_params.budgets.value / solve_params.y - rb_params.delta * rb_params.expectation * x,
                                axis=0)

            # Descent
            t = t - eta_t * grad_t
            solve_params.y = solve_params.y - eta_y * grad_y
            solve_params.y = np.where(
                solve_params.y <= 0, solve_params.proj_y, solve_params.y
            )

            if solve_params.k + 1 > solve_params.sum_k_first:
                solve_params.y_sum += solve_params.y

            if store:
                y_.append(solve_params.y)
                t_.append(t)

            solve_params.k += 1
    return solve_params, t_, y_

