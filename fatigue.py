import numpy as np
from numpy import random
number_of_job = 1000
corrective_maintence_cost = 10
preventive_maintence_cost = 1
standard_deviation_parameter = 0.2
wp1 = 886
wp2 = -0.14
k = 0.4
reference_number_of_cycles = 50000
load_amplitude_first_value = 140
load_amplitude_second_value = 120
damage_level_limit = 0.1
failure_type = ""
man = False

ni = np.full((number_of_job,), 1000)
#print(ni)

sigma_a = np.full((int(number_of_job/2),), load_amplitude_first_value)
sigma_b = np.full((int(number_of_job/2),), load_amplitude_second_value)
sigma = np.hstack((sigma_a, sigma_b))
#print(sigma)

nf_virtual = np.power(sigma/wp1, 1/wp2)
#print(nf_virtual)

rk_virtual = np.power(nf_virtual/reference_number_of_cycles, k)
#print(rk_virtual)

nei_virtual = np.array([])
nei_virtual = np.hstack((nei_virtual, ni[0]))
#print(nei_virtual)

dk_virtual = np.array([])
if not man:
    dk_virtual_first_cell = np.power(nei_virtual[0]/nf_virtual[0], rk_virtual[0])
else:
    dk_virtual_first_cell = np.power(ni[0]/nf_virtual[0], rk_virtual[0])
dk_virtual = np.hstack((dk_virtual, dk_virtual_first_cell))
#print(dk_virtual)

normal_mean = np.power(sigma/wp1, 1/wp2)
normal_stand_dev_st = np.power(sigma/wp1, 1/wp2)*standard_deviation_parameter
nf_sampled = random.normal(normal_mean[0], normal_stand_dev_st[0], 1)
#print(nf_sampled)

rk_sampled = np.array([])
rk_sampled_first_cell = np.power(nf_sampled[0]/reference_number_of_cycles, k)
rk_sampled = np.hstack((rk_sampled, rk_sampled_first_cell))
#print(rk_sampled)

nei_sampled = np.array([])
nei_sampled = np.hstack((nei_sampled, ni[0]))
#print(nei_sampled)

dk_sampled = np.array([])
dk_sampled_first_cell = np.power(nei_sampled[0]/nf_sampled[0], rk_sampled)
dk_sampled = np.hstack((dk_sampled, dk_sampled_first_cell))
#print(dk_sampled)

i = 1
for job in range(0, number_of_job-1):

    condition_1 = dk_virtual[i-1] < damage_level_limit
    condition_2 = ((1 > dk_virtual[i-1]) & (dk_virtual[i-1] > damage_level_limit))
    condition_3 = dk_virtual[i-1] > 1

    simulated_condition_1 = dk_sampled[i-1] > 1
    simulated_condition_2 = dk_sampled[i-1] < 1

    simulated_condition_3 = dk_sampled[i-1] - 1 < dk_virtual[i-1] - damage_level_limit #virtual happen sooner=preventive
    simulated_condition_4 = dk_sampled[i-1] - 1 > dk_virtual[i-1] - damage_level_limit #sampled happen sooner=corrective

    simulated_condition_5 = dk_virtual[i-1] > dk_sampled[i-1]
    simulated_condition_6 = dk_virtual[i-1] < dk_sampled[i-1]

    and_1 = condition_1 * simulated_condition_1
    and_2 = condition_2 * simulated_condition_1 * simulated_condition_3
    and_3 = condition_2 * simulated_condition_1 * simulated_condition_4
    and_4 = condition_2 * simulated_condition_2
    and_5 = condition_3 * simulated_condition_1 * simulated_condition_5
    and_6 = condition_3 * simulated_condition_1 * simulated_condition_6

    #print(f"{i}: {dk_virtual[i-1]}\t{dk_sampled[i-1]}")
    #print(f"{nf_sampled[i-1]}\t{rk_sampled[i-1]}\t{nei_sampled[i-1]}")

    if and_1:
        man = True
        failure_type = "corrective1"
        print(f"failure type is {failure_type}")
    elif and_2:
        man = True
        failure_type = "preventive1"
        print(f"failure type is {failure_type}")
    elif and_3:
        man = True
        failure_type = "corrective2"
        print(f"failure type is {failure_type}")
    elif and_4:
        man = True
        failure_type = "preventive2"
        print(f"failure type is {failure_type}")
    elif and_5:
        man = True
        failure_type = "preventive3"
        print(f"failure type is {failure_type}")
    elif and_6:
        man = True
        failure_type = "corrective3"
        print(f"failure type is {failure_type}")
    else:
        man = False


    nei_virtual_new_cell = np.power(dk_virtual[i-1], 1/rk_virtual[i])*nf_virtual[i]
    nei_virtual = np.hstack((nei_virtual, nei_virtual_new_cell))

    if not man:
        dk_virtual_new_cell = np.power((nei_virtual[i] + ni[i]) / nf_virtual[i], rk_virtual[i])
        dk_virtual = np.hstack((dk_virtual, dk_virtual_new_cell))
    else:
        dk_virtual_new_cell = np.power(ni[i]/nf_virtual[i], rk_virtual[i])
        dk_virtual = np.hstack((dk_virtual, dk_virtual_new_cell))


    if not man:
        nf_sampled_new_cell = nf_sampled[i-1]
        nf_sampled = np.hstack((nf_sampled, nf_sampled_new_cell))
    else:
        nf_sampled_new_cell = random.normal(normal_mean[i-1], normal_stand_dev_st[i-1], 1)
        nf_sampled = np.hstack((nf_sampled, nf_sampled_new_cell))


    rk_sampled_new_cell = np.power(nf_sampled[i]/reference_number_of_cycles, k)
    rk_sampled = np.hstack((rk_sampled, rk_sampled_new_cell))

    nei_sampled_new_cell = nf_sampled[i] * np.power(dk_sampled[i - 1], 1 / rk_sampled[i])
    nei_sampled = np.hstack((nei_sampled, nei_sampled_new_cell))

    if not man:
        dk_sampled_new_cell = np.power((nei_sampled[i]+ni[i])/nf_sampled[i], rk_sampled[i])
        dk_sampled = np.hstack((dk_sampled, dk_sampled_new_cell))
    else:
        dk_sampled_new_cell = np.power(ni[i]/nf_sampled[i], rk_sampled[i])
        dk_sampled = np.hstack((dk_sampled, dk_sampled_new_cell))


    i += 1
#print(nei_virtual)
#print(dk_virtual)
#print(nf_sampled)
#print(rk_sampled)
#print(nei_sampled)
#print(dk_sampled)


