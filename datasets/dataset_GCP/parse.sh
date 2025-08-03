#!/bin/bash

# Description to prepend
description="Description:

Following is a problem description of Graph Coloring Problem. It contains two section.

1. Problem's data description
2. The adjacency list representation of that specific problem.

Please calculate the best solution for this problem, which is the minimum number of colors needed to color the graph such that no two adjacent nodes have the same color.
"

# Process all files ending with .desc.txt
find . -type f -name "*.desc.txt" | while read -r file; do
    echo "Processing $file"

    # Remove [METADATA] section
    # Use awk to skip lines between [METADATA] and the next section header (e.g., [GCP_DATA_INFO] or similar)
    awk '
    BEGIN {skip=0}
    /^\[METADATA\]/ {skip=1; next}
    /^\[.*\]/ && skip==1 {skip=0}
    skip==0 { print }
    ' "$file" > "${file}.tmp"

    # Prepend the new description
    {
        echo "$description"
        echo
        cat "${file}.tmp"
    } > "$file"

    # Cleanup
    rm "${file}.tmp"
done


# Find all files ending with .ans.txt
find . -type f -name "*.ans.txt" | while read -r file; do
    echo "Truncating to first line: $file"
    
    # Keep only the first line
    head -n 1 "$file" > "${file}.tmp"

    # Overwrite original file
    mv "${file}.tmp" "$file"
done

