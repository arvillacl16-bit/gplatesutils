import pygplates as pyg
import argparse
from colorama import Fore, init

init(autoreset=True)

parser = argparse.ArgumentParser(description="Make an initial .rot file.")
parser.add_argument("--ids", nargs="+", required=True, help="IDs to add.")
parser.add_argument("--start", required=False, default=1000, help="Time of beginning. Defaults to 1000.")

raw_args = parser.parse_args()
start = float(raw_args.start)
ids = [int(i) for i in raw_args.ids]
if start <= 0.01:
    print(Fore.RED + "ERROR: Start has to be before 0.01 Ma")
    exit()

features = []
for i in ids:
    rotation_samples = [pyg.GpmlTimeSample(pyg.GpmlFiniteRotation(pyg.FiniteRotation.create_identity_rotation()), 0.0, "Dummy"),
                        pyg.GpmlTimeSample(pyg.GpmlFiniteRotation(pyg.FiniteRotation.create_identity_rotation()), start, "Beginning")]

    irregular_sampling = pyg.GpmlIrregularSampling(rotation_samples)
    rotation_feature = pyg.Feature.create_total_reconstruction_sequence(fixed_plate_id=0, moving_plate_id=i, total_reconstruction_pole=irregular_sampling)
    features.append(rotation_feature)

feature_collection = pyg.FeatureCollection(features)
feature_collection.write("rotation.rot")
