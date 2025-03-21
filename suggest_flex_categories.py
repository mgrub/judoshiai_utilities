import argparse
import json
import os
import re

import pandas
import numpy as np
import matplotlib.pyplot as plt

from dbutils import JudoShiaiConnector_WEB


class FlexWeightUtils:
    def __init__(self, category, hostname):
        self.category_pattern = re.compile("^(.*?) ([\+\-\d]*)kg$")
        self.category = category
        self.jsc = JudoShiaiConnector_WEB(host=hostname)

    def load_competitors(self):
        competitors = self.jsc.get_competitors_of_category(self.category)
        return competitors

    def _modify_weight_for_testing(self, competitors):
        N = len(competitors)
        mean_weight = np.random.normal(40, 5, size=1)

        random_weights = 1000 * np.random.lognormal(
            np.log(mean_weight), 0.2, size=N
        )  # grams

        competitors_modified = []

        for c, new_weight in zip(competitors, random_weights):
            c_mod = c[:-1] + [str(int(new_weight))]
            competitors_modified.append(c_mod)

        return competitors_modified

    def potential_class_sizes(self, class_path, both_can_compete):
        length_sizes = sum(class_path)

        if length_sizes < len(both_can_compete):
            max_from_here = np.sum(both_can_compete[length_sizes, length_sizes:])
            valid_sizes = list(range(1, int(max_from_here) + 1))
        else:
            valid_sizes = []
        return valid_sizes

    def propose_weight_categories(self, competitors):
        N = len(competitors)
        data = [int(c[-1]) for c in competitors]
        data_sorted = np.sort(data)

        # who is allowed to compete with whom?
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
        class_paths = [[]]
        class_path_status = [True]

        for depth in range(12):
            print(f"Iteration: {depth}")

            new_class_paths = []
            new_class_path_status = []

            for class_path, status in zip(class_paths, class_path_status):
                if status:
                    valid_sizes = self.potential_class_sizes(
                        class_path, both_can_compete
                    )

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
                suitable_results.append(
                    (class_path, number_of_ones, len(class_path), np.std(class_path))
                )

        suitable_results = sorted(suitable_results, key=lambda x: x[3])

        return suitable_results, both_can_compete, data

    def create_overview(self, competitors, suitable_results, both_can_compete, data):
        data_sorted = np.sort(data) / 1000
        N = len(data)

        # suitable results
        for res in suitable_results[:10]:
            print(res)

        # label prefix        
        cat_name_all = self.category.replace('?', '').strip()
        label_prefix = self.category.replace("?", "G")

        # who belongs to which class? --> visualize one ("best") solution
        competitors_sorted = sorted(competitors, key=lambda x: x[-1])
        best_solution = suitable_results[0][0]  # "best" not best
        best_solution_visualization = both_can_compete * 1.0
        cat_descriptions = {}
        i = 0
        for icat, cat in enumerate(best_solution):
            best_solution_visualization[i : i + cat, i : i + cat] = 2
            lower_limit = data_sorted[i]
            upper_limit = data_sorted[i + cat - 1]
            cat_text = f"Gruppe {label_prefix}{icat + 1:02d} ({lower_limit:0.2f} - {upper_limit:0.2f} kg)"
            competitor_texts = []

            competitors_in_group = [
                c
                for c in competitors_sorted
                if lower_limit <= float(c[-1]) / 1000
                and float(c[-1]) / 1000 <= upper_limit
            ]
            for cig in competitors_in_group:
                competitor_text = f"{cig[0]}, {cig[1]}, {cig[2]}, {float(cig[-1])/1000:0.2f}kg"
                competitor_texts.append(competitor_text)
            cat_descriptions[cat_text] = competitor_texts # sorted(competitor_texts)
            i += cat

        # plot some information about the weight distribution
        X_weight, Y_count = np.meshgrid(data_sorted, np.arange(N), indexing="ij")

        fig, ax = plt.subplots(2, 1, sharex=True)
        ax[0].hist(data_sorted, bins=20)
        #ax[0].set_xlabel("weight in [kg]")
        ax[0].set_ylabel("competitors")

        ax[1].pcolormesh(
            X_weight,
            Y_count,
            best_solution_visualization,
            edgecolors="white",
            linewidth=0.1,
            cmap="Greys",
        )

        # ax.set_aspect("equal")
        ax[1].set_xlabel("weight in [kg]")
        ax[1].set_ylabel("competitors")

        plot_filename = f"suggested_flex_cat_{cat_name_all}.png"
        fig.savefig(plot_filename, bbox_inches="tight", dpi=300)

        # turn into markdown file
        f = open(f"suggested_flex_cat_{cat_name_all}.md", "w", encoding="UTF-8")
        
        f.write(f"# Gewichtsklassen {cat_name_all}\n\n")
        for cd in cat_descriptions.keys():
            f.write(f"- {cd}\n")
        f.write("\n")

        f.write("## Zuordnungen\n\n")
        for cd, cts in cat_descriptions.items():
            f.write(f"### {cd}\n\n")
            for ct in cts:
                f.write(f"- {ct}\n")
            f.write("\n")
        
        f.write("## Verteilung\n\n")
        f.write(f"![image]({plot_filename})\n")
        f.write("Gewichtsverteilung sowie Klasseneinteilung über Gewicht\n")
        
        f.close()

        # TODO: directly generate pdf for printing using pandoc 

if __name__ == "__main__":
    # argparse interface
    parser = argparse.ArgumentParser(
        prog="ShiFlexWeightUtil",
        description="Suggest flexible weight categories based on actual weigh-in",
    )

    parser.add_argument(
        "category",
        help="Category that holds all the competitors",
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="URL/IP for host that runs JudoShiai",
    )

    parser.add_argument(
        "--replace_weights",
        action="store_true",
        help="use random weights for debugging",
    )

    args = parser.parse_args()

    # analyse competitors
    fwu = FlexWeightUtils(args.category, args.host)

    c = fwu.load_competitors()

    if args.replace_weights:
        # used only for testing :-)
        c = fwu._modify_weight_for_testing(c)

    res, bcc, data = fwu.propose_weight_categories(c)
    fwu.create_overview(c, res, bcc, data)
