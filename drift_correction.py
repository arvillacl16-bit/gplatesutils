import pygplates as pyg
from colorama import init, Fore
from constants import *

init(autoreset=True)

try:
    feature_collection = pyg.FeatureCollection(ROT_FILE)
except Exception as e:
    print(Fore.RED + f"ERROR: Could not load rotation file. Details: {e}")
    exit()

modified_features = []

for feature in feature_collection:
    total_reconstruction_pole = feature.get_total_reconstruction_pole()
    if not total_reconstruction_pole:
        modified_features.append(feature)
        continue

    fixed_plate_id, moving_plate_id, rotation_sequence = total_reconstruction_pole

    time_samples = rotation_sequence.get_enabled_time_samples()
    if not time_samples:
        modified_features.append(feature)
        continue

    sorted_samples = sorted(time_samples, key=lambda s: s.get_time())
    non_zero_samples = [s for s in sorted_samples if s.get_time() > 0.0]
    if non_zero_samples:
        latest_non_zero_sample = min(non_zero_samples, key=lambda s: s.get_time())
        rotation_to_copy = latest_non_zero_sample.get_value()
    else:
        rotation_to_copy = sorted_samples[-1].get_value()

    latest_sample = sorted_samples[-1]
    latest_rotation = latest_sample.get_value()

    new_samples = []
    has_zero = False
    for sample in sorted_samples:
        if sample.get_time() == 0.:
            new_samples.append(sample)
            has_zero = True

    if not has_zero:
        identity_rot = pyg.FiniteRotation.create_identity_rotation()
        new_samples.append(pyg.GpmlTimeSample(pyg.GpmlFiniteRotation(identity_rot), 0, "Present Day"))

    new_samples.append(pyg.GpmlTimeSample(rotation_to_copy, 0.01, "Drift Correction"))

    for sample in sorted_samples:
        if sample.get_time() > 0.:
            new_samples.append(sample)

    new_samples.sort(key=lambda s: s.get_time())

    irregular_sampling = pyg.GpmlIrregularSampling(new_samples)
    new_feature = pyg.Feature.create_total_reconstruction_sequence(
            fixed_plate_id=fixed_plate_id,
            moving_plate_id=moving_plate_id,
            total_reconstruction_pole=irregular_sampling
            )
    modified_features.append(new_feature)

output_collection = pyg.FeatureCollection(modified_features)
output_collection.write(ROT_FILE)
