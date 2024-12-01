import numpy as np
import scipy
import matplotlib.pyplot as plt
import scipy.optimize as opt

N = np.random.randint(20, 200)
mean_weight = np.random.normal(40, 5, size=1)

data = np.random.lognormal(np.log(mean_weight), 0.2, size=N)
data_sorted = np.sort(data)

print(mean_weight, N)

# plt.hist(data, bins=20)
# plt.show()

A_can_compete_with_B = np.ndarray((N, N))

for i, weight in enumerate(data_sorted):
    w_low = 0.9 * weight
    w_high = 1.1 * weight

    A_can_compete_with_B[i, :] = np.logical_and(
        w_low <= data_sorted, data_sorted <= w_high
    )

B_can_compete_with_A = A_can_compete_with_B.T

both_can_compete = np.logical_and(A_can_compete_with_B, B_can_compete_with_A)




# try out a lot of combinations / "smart bruteforce" ;-)

def potential_class_sizes(class_path, both_can_compete):
    length_sizes = sum(class_path)

    if length_sizes < len(both_can_compete):
        max_from_here = np.sum(both_can_compete[length_sizes,length_sizes:])
        valid_sizes = list(range(1, int(max_from_here)+1))
    else:
        valid_sizes = []
    return valid_sizes

class_paths = [[]]
class_path_status = [True]

for depth in range(12):
    print(f"Iteration: {depth}")

    new_class_paths = []
    new_class_path_status = []

    for class_path, status in zip(class_paths, class_path_status):

        if status:
            valid_sizes = potential_class_sizes(class_path, both_can_compete)
            
            # only use 3 biggest sizes if many are possible
            if len(valid_sizes) > 3:
                valid_sizes = valid_sizes[-3:]
            
            # only include class size 1, if no other option available
            elif len(valid_sizes) > 1:
                valid_sizes = valid_sizes[1:]
            
            # create new class paths
            for vs in valid_sizes:
                new_class_path = class_path + [vs]
                new_class_paths.append(new_class_path)
                if sum(new_class_path) == N:
                    new_class_path_status.append(False)
                else:
                    new_class_path_status.append(True)
        
        else:
            new_class_paths.append(class_path)
            new_class_path_status.append(False)
    
    # overwrite old information
    class_paths = new_class_paths
    class_path_status = new_class_path_status


print("\n\n", len(class_paths))
suitable_results = []
for class_path, status in zip(class_paths, class_path_status):
    if not status:
        number_of_ones = sum([l for l in class_path if l == 1])
        suitable_results.append((class_path, number_of_ones, len(class_path), np.std(class_path)))

suitable_results = sorted(suitable_results, key=lambda x: x[3])
for res in suitable_results[:10]:
    print(res)

# plot
X_weight, Y_weight = np.meshgrid(data_sorted, data_sorted)
X_count, Y_count = np.meshgrid(np.arange(N), np.arange(N))

fig, ax = plt.subplots(1, 2)


# visualize one solution
best_solution = suitable_results[0][0]  # "best" not best
best_solution_visualization = both_can_compete * 1.0
i = 0
for icat, cat in enumerate(best_solution):
    best_solution_visualization[i:i+cat,i:i+cat] = 2
    print(f"Category {icat+1:02d}: {data_sorted[i]:0.2f} - {data_sorted[i+cat-1]:0.2f} kg")
    i += cat


ax[0].pcolormesh(X_weight, Y_weight, best_solution_visualization, edgecolors="k", linewidth=0.0)
ax[1].pcolormesh(X_count, Y_count, best_solution_visualization, edgecolors="k", linewidth=0.0)

ax[0].set_aspect("equal")
ax[1].set_aspect("equal")

plt.show()