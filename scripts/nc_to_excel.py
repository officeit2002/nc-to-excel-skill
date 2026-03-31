#!/usr/bin/env python3
"""
NC to Excel Converter

Converts NetCDF (.nc) file data to Excel (.xlsx) format.
Handles multi-dimensional arrays by flattening them into tabular format
with coordinate columns.

Usage:
    python nc_to_excel.py <input.nc> <output.xlsx> [--variable VAR_NAME]

Arguments:
    input.nc      Path to the NetCDF file
    output.xlsx   Path for the output Excel file
    --variable    Optional: specify which variable to export (defaults to main data variable)
"""

import argparse
import sys
import os
import netCDF4 as nc
import pandas as pd
import numpy as np


def find_main_variable(ds):
    """Find the main data variable (largest non-coordinate variable)."""
    coord_vars = set()
    for name, var in ds.variables.items():
        if var.dimensions == (name,):
            coord_vars.add(name)
    
    main_var = None
    max_size = 0
    for name, var in ds.variables.items():
        if name not in coord_vars and var.ndim > 0:
            size = np.prod(var.shape)
            if size > max_size:
                max_size = size
                main_var = name
    
    return main_var


def get_fill_value(var):
    """Get the fill/missing value for a variable."""
    for attr_name in ['_FillValue', 'missing_value', 'FillValue']:
        if hasattr(var, attr_name):
            return getattr(var, attr_name)
    return None


def get_column_name(var):
    """Generate a meaningful column name from variable attributes."""
    if hasattr(var, 'long_name'):
        return var.long_name
    if hasattr(var, 'standard_name'):
        return var.standard_name
    return var.name


def convert_nc_to_excel(input_path, output_path, variable_name=None):
    """Convert a NetCDF file to Excel format."""
    
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    print(f"Reading NetCDF file: {input_path}")
    ds = nc.Dataset(input_path, 'r')
    
    print(f"Description: {getattr(ds, 'description', 'N/A')}")
    print(f"Dimensions: {dict(ds.dimensions)}")
    
    # Identify coordinate and data variables
    coord_vars = {}
    data_vars = {}
    
    for name, var in ds.variables.items():
        if var.dimensions == (name,):
            coord_vars[name] = var[:]
        else:
            data_vars[name] = var
    
    # Determine which variable to export
    if variable_name:
        if variable_name not in data_vars:
            print(f"Error: Variable '{variable_name}' not found.")
            print(f"Available variables: {list(data_vars.keys())}")
            ds.close()
            sys.exit(1)
        target_var = data_vars[variable_name]
    else:
        main_var = find_main_variable(ds)
        if main_var is None:
            print("Error: No data variable found.")
            ds.close()
            sys.exit(1)
        target_var = data_vars[main_var]
        print(f"Using main variable: {main_var}")
    
    # Get fill value
    fill_value = get_fill_value(target_var)
    
    # Build DataFrame
    print(f"Processing variable: {target_var.name}")
    print(f"Shape: {target_var.shape}")
    print(f"Dimensions: {target_var.dimensions}")
    
    # Create meshgrid for coordinates
    coord_arrays = []
    coord_names = []
    for dim_name in target_var.dimensions:
        if dim_name in coord_vars:
            coord_names.append(dim_name)
            coord_arrays.append(coord_vars[dim_name])
    
    if len(coord_arrays) == 1:
        # 1D data
        data = target_var[:]
        df = pd.DataFrame({
            coord_names[0]: coord_arrays[0],
            get_column_name(target_var): data
        })
    elif len(coord_arrays) == 2:
        # 2D data
        lon, lat = np.meshgrid(coord_arrays[1], coord_arrays[0])
        data = target_var[:]
        
        # Handle fill values
        if fill_value is not None:
            data = np.where(data == fill_value, np.nan, data)
        data = np.where(np.abs(data) > 1e20, np.nan, data)
        
        df = pd.DataFrame({
            coord_names[1]: lon.flatten(),
            coord_names[0]: lat.flatten(),
            get_column_name(target_var): data.flatten()
        })
    elif len(coord_arrays) == 3:
        # 3D data (e.g., time, lat, lon)
        data = target_var[:]
        
        # Handle fill values
        if fill_value is not None:
            data = np.where(data == fill_value, np.nan, data)
        data = np.where(np.abs(data) > 1e20, np.nan, data)
        
        # Create coordinate arrays for all dimensions
        dim0, dim1, dim2 = np.meshgrid(
            coord_arrays[0], coord_arrays[1], coord_arrays[2], indexing='ij'
        )
        
        df = pd.DataFrame({
            coord_names[0]: dim0.flatten(),
            coord_names[1]: dim1.flatten(),
            coord_names[2]: dim2.flatten(),
            get_column_name(target_var): data.flatten()
        })
    else:
        print(f"Warning: {len(coord_arrays)}D data not fully supported. Exporting flattened data.")
        data = target_var[:]
        if fill_value is not None:
            data = np.where(data == fill_value, np.nan, data)
        data = np.where(np.abs(data) > 1e20, np.nan, data)
        df = pd.DataFrame({
            get_column_name(target_var): data.flatten()
        })
    
    # Add units to column name if available
    col_name = get_column_name(target_var)
    if hasattr(target_var, 'units'):
        df.rename(columns={col_name: f"{col_name} ({target_var.units})"}, inplace=True)
    
    # Write to Excel
    print(f"Writing to Excel: {output_path}")
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    # Summary
    print(f"\nConversion complete!")
    print(f"Output file: {output_path}")
    print(f"Total rows: {len(df)}")
    print(f"Valid values: {df.iloc[:, -1].notna().sum()}")
    print(f"Missing values: {df.iloc[:, -1].isna().sum()}")
    
    ds.close()
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Convert NetCDF to Excel')
    parser.add_argument('input', help='Input .nc file path')
    parser.add_argument('output', help='Output .xlsx file path')
    parser.add_argument('--variable', '-v', help='Variable name to export')
    
    args = parser.parse_args()
    convert_nc_to_excel(args.input, args.output, args.variable)


if __name__ == '__main__':
    main()
