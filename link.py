import pygplates as pyg
from colorama import init, Fore
import argparse
from constants import *

init(autoreset=True)

parser = argparse.ArgumentParser()
parser.add_argument("--collid", required=True, help="ID that has changed conjugate plate.")
parser.add_argument("--conjid", required=False, default=0, help="Conjugate ID. Zero by default.")
parser.add_argument("--time", required=True, help="Time of change.")

raw_args = parser.parse_args()
coll_id = abs(int(raw_args.collid))
conj_id = abs(int(raw_args.conjid))
time = float(raw_args.time)

if time < 0.01:
    print(Fore.RED + "Cannot work after this time.")
    exit()

try:
    feature_collection = pyg.FeatureCollection(ROT_FILE)
except Exception as e:
    print(Fore.RED + f"ERROR: Could not load rotation file. Details: {e}")
    exit()

rotation_model = pyg.RotationModel(feature_collection)

modified_features = []
target_found = False

for feature in feature_collection:
    total_reconstruction_pole = feature.get_total_reconstruction_pole()
    if not total_reconstruction_pole:
        modified_features.append(feature)
        continue

    fixed_plate_id, moving_plate_id, rotation_sequence = total_reconstruction_pole

    if moving_plate_id == coll_id:
        target_found = True

        time_samples = rotation_sequence.get_enabled_time_samples()

        abs_rotation_at_T = rotation_model.get_rotation(time, coll_id)
        
        if conj_id == 0:
            new_rel_rotation_at_T = abs_rotation_at_T
        else:
            abs_conj_rotation_at_T = rotation_model.get_rotation(time, conj_id)
            new_rel_rotation_at_T = abs_conj_rotation_at_T.get_inverse() * abs_rotation_at_T

        new_samples = []
        for sample in time_samples:
            if sample.get_time() > time:
                new_samples.append(sample);

        old_rot_at_T = rotation_model.get_rotation(time, fixed_plate_id)
        new_samples.append(pyg.GpmlTimeSample(pyg.GpmlFiniteRotation(new_rel_rotation_at_T), time, "Anchor switch"))

        for sample in time_samples:
            if sample.get_time() == 0:
                new_samples.append(sample)

        new_samples.sort(key=lambda s: s.get_time())

        irregular_sampling = pyg.GpmlIrregularSampling(new_samples)
        new_feature = pyg.Feature.create_total_reconstruction_sequence(fixed_plate_id=conj_id, moving_plate_id=coll_id, total_reconstruction_pole=irregular_sampling)
        modified_features.append(new_feature)
    else:
        modified_features.append(feature)

if not target_found:
    print(Fore.YELLOW + f"WARNING: Plate ID {coll_id} not found.")
else:
    output_collection = pyg.FeatureCollection(modified_features)
    output_collection.write(ROT_FILE)

import drift_correction
