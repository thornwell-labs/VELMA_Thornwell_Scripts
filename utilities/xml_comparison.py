"""
Compares two VELMA configuration XML files and reports every parameter whose
value changed. Flattens each XML to tag-path/value pairs and writes the
differences (key, old value, new value) to a CSV.
"""

import xml.etree.ElementTree as ET
import csv

def parse_xml_to_dict(xml_path):
    """Parses an XML file into a dictionary of tag-value pairs (flat structure)."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    param_dict = {}

    def recursive_parse(element, path=""):
        for child in element:
            tag = child.tag
            key = f"{path}/{tag}" if path else tag
            if list(child):  # If it has children, recurse
                recursive_parse(child, key)
            else:  # Leaf node: get its text value
                param_dict[key] = child.text.strip() if child.text else ""

    recursive_parse(root)
    return param_dict

def compare_parameters(old_dict, new_dict):
    """Compares two dictionaries and returns a list of changes."""
    all_keys = set(old_dict.keys()).union(new_dict.keys())
    changes = []
    for key in sorted(all_keys):
        old_val = old_dict.get(key, "")
        new_val = new_dict.get(key, "")
        if old_val != new_val:
            changes.append((key, old_val, new_val))
    return changes

def write_changes_to_csv(changes, output_file):
    """Writes the list of changes to a CSV file."""
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Parameter", "Old Value", "New Value"])
        writer.writerows(changes)

# --- Usage ---
old_xml = "path/to/VELMA_Watersheds/Green/XML/WA_Green30m_9Apr2025_Hyak.xml"
new_xml = "path/to/VELMA_Watersheds/Green/XML/WA_Green30m_30Jun2025_Hyak.xml"
output_csv = "path/to/VELMA_Watersheds/Green/Analysis/30June_Green_parameter_changes.csv"

old_params = parse_xml_to_dict(old_xml)
new_params = parse_xml_to_dict(new_xml)
changes = compare_parameters(old_params, new_params)
write_changes_to_csv(changes, output_csv)

print(f"Done. {len(changes)} parameters changed. Output written to {output_csv}")
