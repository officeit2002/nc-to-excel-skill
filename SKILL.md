---
name: nc-to-excel-skill
description: Convert NetCDF (.nc) file data to Excel (.xlsx) format. Reads scientific NetCDF files, extracts variables with their dimensions and attributes, and exports tabular data to Excel spreadsheets. Use when working with oceanographic, meteorological, or climate data in NetCDF format that needs to be converted to Excel.
---

# NC to Excel Skill

Converts NetCDF (.nc) files to Excel (.xlsx) spreadsheets.

## When to Use

- User wants to read or inspect a .nc file
- User wants to convert NetCDF data to Excel format
- User needs to analyze scientific data (ocean, climate, meteorological) in spreadsheet software

## Workflow

### Step 1: Inspect the NetCDF File

First, read the file to understand its structure:

```python
import netCDF4 as nc

ds = nc.Dataset('path/to/file.nc', 'r')

for name, dim in ds.dimensions.items():
    print(f'{name}: {len(dim)}')

for name, var in ds.variables.items():
    print(f'{name}: dtype={var.dtype}, shape={var.shape}, dims={var.dimensions}')

for attr in ds.ncattrs():
    print(f'{attr}: {ds.getncattr(attr)}')

ds.close()
```

### Step 2: Execute the Conversion Script

Use the bundled script at `scripts/nc_to_excel.py`:

```bash
python scripts/nc_to_excel.py <input.nc> <output.xlsx> [--variable VAR_NAME]
```

Arguments:
- `input.nc` - Path to the NetCDF file
- `output.xlsx` - Path for the output Excel file
- `--variable VAR_NAME` - Optional: specify which variable to export

### Step 3: Confirm Output

Report to the user:
- File path of the generated Excel file
- Number of rows and columns
- Which variables/dimensions were included
- Any missing values or data quality notes

## Script Usage

The script `scripts/nc_to_excel.py` handles:
- Reading all dimensions and coordinate variables
- Flattening multi-dimensional arrays into tabular format
- Handling missing/fill values (converting to NaN)
- Creating meaningful column names from variable attributes
- Efficient processing of large datasets

## Dependencies

Requires: `netCDF4`, `pandas`, `openpyxl`, `numpy`

Install if missing: `pip install netCDF4 pandas openpyxl numpy`
