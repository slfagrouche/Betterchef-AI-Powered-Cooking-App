
```plaintext
datasets/
├── raw/
│   ├── A_recipes.txt        # Contains recipes starting with the letter 'A'.
│   ├── B_recipes.txt        # Contains recipes starting with the letter 'B'.
│   ├── C_recipes.txt        # Contains recipes starting with the letter 'C'.
│   ├── D_recipes.txt        # Contains recipes starting with the letter 'D'.
│   ├── E_recipes.txt        # Contains recipes starting with the letter 'E'.
│   ├── F_recipes.txt        # Contains recipes starting with the letter 'F'.
│   └── G_recipes.txt        # Contains recipes starting with the letter 'G'.
│   └── ...        # Till letter starting with the letter 'Z'.

└── processed/
    ├── A_Nice_Cup_of_Tea.txt                    # Detailed recipe for making a nice cup of tea.
    ├── Aadun_(Nigerian_Corn_Flour_with_Palm_Oil).txt   # Detailed recipe for Aadun, a Nigerian dish.
    ├── Abacha_Mmiri_(Soaked_Cassava_Flakes).txt         # Detailed recipe for Abacha Mmiri, a dish involving soaked cassava flakes.
    ├── ... # ect


### Note on Dataset Availability

Due to the large size of some dataset files, not all files are included in this repository. To generate these files locally:

1. Navigate to the `scripts/` directory.
2. Run the `scrape_data.py` script:
   - python scrape_data.py

   ```
   This script will scrape and process the data, populating the `raw/` and `processed/` directories with the necessary recipe files.

```

