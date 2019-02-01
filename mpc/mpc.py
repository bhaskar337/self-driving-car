N = 10
dt = 0.1

Lf = 2.67

ref_cte = 0
ref_epsi = 0
ref_v = 0

x_start = 0
y_start = x_start + N
psi_start = y_start + N
v_start = psi_start+ N
cte_start = v_start + N
epsi_start = cte_start + N
delta_start = epsi_start + N 
a_start = delta_start + N - 1
-

n_vars = N * 6 + (N - 1) * 2
n_contraints = N * 6

vars = [0] * n_vars

vars

x[t+1] = x[t] + v[t] * cos(psi[t]) * dt
y[t+1] = y[t] + v[t] * sin(psi[t]) * dt
psi[t+1] = psi[t] 

for t in range(N):
	cost += pow(epsi[t], 2)
	cost += pow(cte[t], 2)
	cost += pow(v[t] - ref_v, 2)

	if t < N - 1:
		cost += pow(delta[t], 2)
		cost += pow(a[t], 2)

		cost += pow(delta[t+1] - delta[t], 2)
		cost += pow(a[t+1] - a[t], 2