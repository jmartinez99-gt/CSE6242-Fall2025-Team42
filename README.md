# CSE6242-Fall2025-Team42
CSE 6242 Fall 2025 Final Project code repository for Team 42

## Instructions

### i. Just use the visualization
To simple open and use the visualization
1. [Click Here](https://public.tableau.com/views/sport_participation/NCAASportsParticipation?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

### ii. Obtain just the results 
To just get the CSV files needed for the dashboards
1. Run `setup/compress_and_decompress_tableau_csvs.py`
2. Open `tableau/**`

### iii. Run Entire Project
To run the whole project from scratch, run code from these directories in the following order
1. `setup\**`
2. `preprocessing\**`
3. `merging\merge_all.ipynb`
4. `merging\column_groups.ipynb`
5. `analysis\**`
6. `postprocessing\**`
7. `tableau\**`
