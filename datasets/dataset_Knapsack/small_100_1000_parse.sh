#!/bin/bash

# use it inside ./small_100_1000
for i in {1..100}; do
    file="q${i}.desc.txt"

    # Skip if file doesn't exist
    if [[ ! -f "$file" ]]; then
        echo "File $file not found, skipping."
        continue
    fi

    # Extract the 12th line
    line12=$(sed -n '12p' "$file")

    # Extract number using basic shell and sed
    weight=$(echo "$line12" | sed -n 's/^total weight: \([0-9][0-9]*\)$/\1/p')

    if [[ -z "$weight" ]]; then
        echo "No valid 'total weight' found in $file, skipping."
        continue
    fi

    # Create new file with the modification
    awk -v weight="$weight" '
        NR == 9 {
            print "\nPlease note that the total weight is *" weight "*, maximize the value without exceeding the total weight.";
        }
        NR != 12 {
            print;
        }
    ' "$file" > tmpfile && mv tmpfile "$file"

    echo "Updated $file"
done

