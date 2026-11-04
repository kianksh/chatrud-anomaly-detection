from dataclasses import dataclass


@dataclass(frozen=True)
class DepositModel:
    key: str
    label: str
    pathfinders: tuple
    quantile: float
    min_elements: int
    validation_pairs: tuple = ()


GENERAL_MODEL = DepositModel(
    key="Final_Anomalies",
    label="General",
    pathfinders=("Cr", "Ni", "Cu", "Au", "As", "Sb", "Mo"),
    quantile=0.95,
    min_elements=1,
)

DEPOSIT_MODELS = (
    DepositModel(
        key="Chromite",
        label="Chromite",
        pathfinders=("Cr", "Ni"),
        quantile=0.95,
        min_elements=1,
        validation_pairs=(("Ni", "Cr"),),
    ),
    DepositModel(
        key="VMS",
        label="VMS (Ophiolitic)",
        pathfinders=("Cu", "Co", "Zn", "Fe"),
        quantile=0.95,
        min_elements=1,
        validation_pairs=(("Zn", "Cu"),),
    ),
    DepositModel(
        key="Epithermal",
        label="Epithermal",
        pathfinders=("Cu", "Au", "Ag", "As", "Sb"),
        quantile=0.90,
        min_elements=3,
        validation_pairs=(("Au", "Cu"), ("Au", "As"), ("Cu", "As")),
    ),
    DepositModel(
        key="Porphyry",
        label="Porphyry",
        pathfinders=("Cu", "Mo", "Au", "Ag", "Fe"),
        quantile=0.80,
        min_elements=3,
        validation_pairs=(("Cu", "Mo"), ("Cu", "Au")),
    ),
)


def apply_filter(candidates, reference, model):
    """Keep candidates at or above the model's quantile (computed on reference) in enough pathfinders."""
    columns = list(model.pathfinders)
    thresholds = reference[columns].quantile(model.quantile)
    hits = (candidates[columns] >= thresholds).sum(axis=1)
    return candidates[hits >= model.min_elements].copy()
