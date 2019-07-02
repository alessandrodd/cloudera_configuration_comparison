# Cloudera Configuration Comparison
Simple script to compare two clusters configurations

## Requirements
- python 3
- requests library (almost always included in python distributions)

# Usage
1) Copy config.example.ini to config.ini
2) Edit config.ini:
   1) specify only the services that you want to compare
   2) set credentials for the two clusters
3) Execute python compare.py