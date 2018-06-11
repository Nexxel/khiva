"""
Copyright (c) 2018 Shapelets.io

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
########################################################################################################################
# IMPORT
########################################################################################################################
import matplotlib.pyplot as plt
import pandas as pd
import os.path
from subprocess import call


########################################################################################################################


def read_data(file_path):
    """
    Reads the CSV file generated by Google benchmark. This function drops the column 'name' and
    adds 3 extra columns based on it:
    1. benchmark_name: The name of the benchmark. To be used subsequently in the figure title
    2. backend: The backend name. To be used subsequently in the series name of the plot
    3. params: Each parameter combination with which the given benchmark was executed

    :param file_path: the CSV file path
    :return: a pandas DataFrame with the data contained in the CSV file specified
    """
    df = pd.read_csv(file_path, skiprows=2).dropna(axis=1, how='all')
    df["benchmark_name"] = df['name'].str.split("<").str.get(0)
    df["backend"] = df['name'].str.split(
        "af::Backend::AF_BACKEND_").str[1].str.split(",").str[0]
    df["params"] = df['name'].str.split("/").str[1:].str.join("/")
    df = df.drop(["name"], axis=1)
    return df


def plot_benchmarks_from_df(df, field, units, grid=False, save=True, output_path=None):
    """
    Plot all the benchmarks contained in the input Pandas DataFrame 'df'. The 'benchmark_name' column values are
    used to determine the number of figures to create. For all the given benchmark names, the function iterates
    over the backends in which the benchmark has been executed and plots all of them as separate series in the
    same figure

    :param df: Input DataFrame containing all the data
    :param field: Column to be plotted
    :param units: Units of measure of the field column. To be used in the Y axis label
    :param grid: Determines whether to use a grid or not in the plot function
    :param save: Determines whether the plots are save on disk or they are just displayed in the screen. The output
    folder is contained in the output_path input variable. The output files' names are: <benchmark_name>-<field>.png
    (All of them generated in the output_path directory)
    :param output_path: Determines the directory where to store the output benchmark images
    """
    benchmark_names = df["benchmark_name"].drop_duplicates().values.tolist()
    backends = df["backend"].drop_duplicates().values.tolist()

    for benchmark_name in benchmark_names:
        values = []
        indexes = []
        for backend in backends:
            benchmark_f = df["benchmark_name"] == benchmark_name
            backend_f = df["backend"] == backend
            df_bn = df[benchmark_f & backend_f][field]
            df_indexes = df[benchmark_f & backend_f]["params"]
            values += [df_bn.values.tolist()]
            indexes = df_indexes.values.tolist()

        width = max(10, int(len(indexes) * 0.25))
        height = 8
        plt.figure()
        plt.tight_layout()
        new = pd.DataFrame(
            data=list(map(list, zip(*values))), columns=backends)
        new.plot(figsize=(width, height), legend=True,
                 title=benchmark_name, grid=grid)
        plt.xlabel("params")
        plt.xlim([0, len(indexes) - 1])
        plt.xticks(range(len(indexes)), indexes,
                   size='small', rotation=45, ha="right")
        plt.ylabel(field + " (" + units + ")")
        plt.subplots_adjust(bottom=0.15)
        if save:
            output_name = output_path + "/" + benchmark_name + "-" + field + ".png"
            plt.savefig(fname=output_name, bbox_inches="tight")
        else:
            plt.show()


def plot_benchmarks_from_file(file_path, fields_units, grid=False, save=True):
    """
    Plot all the benchmarks contained in the input Pandas DataFrame 'df'. The 'benchmark_name' column values are
    used to determine the number of figures to create. For all the given benchmark names, the function iterates
    over the backends in which the benchmark has been executed and plots all of them as separate series in the
    same figure

    Example:
        fields_units = [{"field": "real_time", "unit": "us"}, {"field": "Memory", "unit": "bytes"}]
        plot_benchmarks_from_file("benchmark-results.csv", fields_units)
        # Displaying the results on screen
        plot_benchmarks_from_file("benchmark-results.csv", fields_units, save=False)

    :param file_path: Path to the input CSV file from where to read the benchmark results
    :param fields_units: List of dictionaries containing the fields
    :param grid: Determines whether to use a grid or not in the plot function
    :param save: Determines whether the plots are save on disk or they are just displayed in the screen.
    """
    input_dir = os.path.abspath(os.path.join(file_path, os.pardir))
    df = read_data(file_path)
    for field_unit in fields_units:
        plot_benchmarks_from_df(
            df, field_unit["field"], field_unit["unit"], grid, save, input_dir)


def main():
    directory = os.path.dirname(os.path.abspath(
        __file__)) + os.path.sep + "../build/benchmarks/results"
    if not os.path.exists(directory):
        os.makedirs(directory)
    fields_units = [{"field": "real_time", "unit": "us"},
                    {"field": "Memory", "unit": "bytes"}]

    bin_dir = os.path.dirname(os.path.abspath(
        __file__)) + os.path.sep + "../build/bin"
    for benchmark in os.listdir(bin_dir):
        print(benchmark)
        if benchmark.endswith("Bench"):
            executable = bin_dir + os.path.sep + benchmark
            file_name = directory + os.path.sep + benchmark + ".csv"
            print("Running benchmark suite: " + benchmark)
            call([executable, "--benchmark_min_time=1e-1",
                  "--benchmark_out=" + file_name, "--benchmark_out_format=csv"])
            print("Plotting the results of the benchmark suite: " + benchmark)
            plot_benchmarks_from_file(file_name, fields_units)


if __name__ == "__main__":
    main()