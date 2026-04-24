remedies = {
    "nitrogen-N": [
        "Yellowing of older leaves, especially during fruit growth",
        "Sparse vegetation / stunted growth",
        "Branches dry from tip to base"
    ],
    "phosphorus-P": [
        "Older opaque green leaves",
        "Brown or purplish spots on tip or middle",
        "Premature falling leaves & poor root development"
    ],
    "potasium-K": [
        "Yellowing of tips and borders on older leaves",
        "Leaf margin burn & branch dieback",
        "Increase in void fruits and reduced grain size"
    ],
    "calcium-Ca": [
        "New leaves show yellowing along edges",
        "Symptoms move inward between leaf veins",
        "Reduced flowering & poorly developed roots"
    ],
    "magnesium-Mg": [
        "Yellowing between ribs on older leaves",
        "Turns brown between veins",
        "Premature leaf fall"
    ],
    "sulphur-S": [
        "Similar to nitrogen deficiency but on new leaves",
        "Shortened internodes"
    ],
    "iron-Fe": [
        "New leaves turn yellow but ribs remain green",
        "Fine reticulate chlorosis"
    ],
    "manganese-Mn": [
        "Whitish marks on new leaves merging to yellow",
        "Egg-yolk-like chlorosis"
    ],
    "zinc-Zn": [
        "Short internodes & narrow yellow new leaves",
        "Death of terminal buds",
        "Smaller fruits"
    ],
    "copper-Cu": [
        "New leaves with prominent secondary veins",
        "Leaf blade deformation & downward bending"
    ],
    "boron-B": [
        "Small new leaves with bizarre shapes",
        "Death of terminal buds (apical necrosis)",
        "Poor flowering & declining root system"
    ],
    "molybdenum-Mo": [
        "Yellowish spots on older leaves",
        "Browning between veins & leaf edge rolling"
    ],
    "healthy": [
        "Leaf appears normal with no visible deficiency",
        "Uniform green color and proper size"
    ],
    "more-deficiencies": [
        "Multiple overlapping symptoms detected",
        "Consult an agronomist for precise diagnosis"
    ]
}

def get_remedy(deficiency_class):
    """Returns a list of remedies for a given deficiency class."""
    return remedies.get(deficiency_class, ["No specific symptoms found. Consult an expert."])
