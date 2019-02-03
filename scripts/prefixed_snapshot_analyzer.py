#!/usr/bin/env python3

from ..core import KappaSnapshot
import glob
import csv
import argparse
import warnings


def snapshot_analyzer(base_directory: str, snap_prefix: str, verbosity: bool):
    # Get the file names of snapshots in specified directory that fit the pattern [prefix][number].ka
    snap_names = glob.glob(base_directory + snap_prefix + '*.ka')
    snap_num = len(snap_names)
    if verbosity:
        print("Found " + str(snap_num) + " snapshots in directory " + base_directory + ' with prefix <' + snap_prefix + '> .')
    if snap_num < 2:
        warnings.warn('Found less than 2 snapshots.')

    # For each snapshot, get the size distribution & update the results dictionary {size: abundance}
    # Also get the number of complexes in that snapshot and save it to another dictionary {snapshot name: number of complexes}
    cum_dist = {}
    total_complexes = {}
    lc_size = {}
    for snap_index in range(snap_num):
        snap_name = snap_names[snap_index]
        if verbosity:
            print('Now parsing file <{}>, {} of {}, {}%'.format(
                snap_name, snap_index, snap_num, snap_index/snap_num))
        current_snapshot = KappaSnapshot(snap_name)
        total_complexes[snap_name] = sum(current_snapshot.get_all_abundances())
        lc_size[snap_name] = current_snapshot.get_largest_complexes()[0].get_size_of_complex()
        size_dist = current_snapshot.get_size_distribution()
        for key in size_dist.keys():
            if key in cum_dist:
                cum_dist[key] += size_dist[key]
            else:
                cum_dist[key] = size_dist[key]


    # Save the cumulative distribution to file
    cum_dist_file_name = base_directory + snap_prefix + 'distribution_cumulative.csv'
    with open(cum_dist_file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Size', 'Cumulative Abundance'])
        for key, value in cum_dist.items():
            writer.writerow([key, value])
    if verbosity:
        print('Cumulative distribution written to file: ' + cum_dist_file_name)

    # Save the mean distribution to file; it's identical to the cumulative but divided by the total number of snapshots
    # found in the directory
    mean_dist_file_name = base_directory + snap_prefix + 'distribution_mean.csv'
    with open(mean_dist_file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Size', 'Mean Abundance'])
        for key, value in cum_dist.items():
            writer.writerow([key, value/snap_num])
    if verbosity:
        print('Mean distribution written to file: ' + mean_dist_file_name)

    # Save the number of complexes in each snapshot to a file
    num_species_file_name = base_directory + snap_prefix + 'total_complexes.csv'
    with open(num_species_file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Snapshot Name', 'Number of complexes'])
        for key, value in total_complexes.items():
            writer.writerow([key, value])
    if verbosity:
        print('Distribution of number of complexes written to file: ' + num_species_file_name)


    # Save the largest-complex statistics to file
    largest_complex_stats_file_name = base_directory + snap_prefix + 'largest_complex_stats.csv'
    with open(largest_complex_stats_file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Snapshot Number', 'Largest Complex(es) Size'])
        for key, value in lc_size.items():
            writer.writerow([key, value])
    if verbosity:
        print('Largest complex sizes written to file: ' + largest_complex_stats_file_name)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get cumulative and mean distribution of complex sizes, plus distribution of number of species,'
                    ' based on snapshots sharing a common prefix, like "t_one_snap_7.ka" having the prefix "t_one_".'
                    ' Snapshots must contain the word "snap" and end in ".ka". Files will be produced in the same'
                    ' directory as the snapshots are. They will be prefixed accordingly, e.g. '
                    ' [prefix]distribution_cumulative.csv')
    parser.add_argument('-p', '--prefix', type=str, default='',
                        help='Prefix identifying snapshots to analyze; e.g. "foo_snap_" is the prefix for'
                             '"foo_snap_76.ka". Files must end with [number].ka')
    parser.add_argument('-d', '--working_directory', type=str, default='./',
                        help='The directory where snapshots are held, and where distribution files will be saved to.')
    parser.add_argument('-v', '--verbosity', action='store_true',
                        help='Print extra information, like number of snapshots found, directory understood, and'
                             ' file names used for output.')
    args = parser.parse_args()

    snapshot_analyzer(base_directory=args.working_directory, snap_prefix=args.prefix, verbosity=args.verbosity)
