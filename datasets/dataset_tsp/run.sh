# unzip the ./ALL_tsp.tar.gz file 
# and unzip all the .gz files in ./ALL_tsp.tar.gz to all_tsp directory

#!/bin/bash
mkdir -p all_tsp
# Create a .gitkeep in the all_tsp directory
touch all_tsp/.gitkeep
tar -xzf ALL_tsp.tar.gz -C all_tsp
find all_tsp -name "*.gz" -exec gunzip {} \;
echo "Unzipping completed. All files are now in the all_tsp directory."

# Make a ignore directory in the all_tsp directory
mkdir -p all_tsp/ignore
# Move the "brg180.tsp" and "brg180.opt.tour" files to the ignore directory
mv all_tsp/brg180.tsp all_tsp/ignore/
mv all_tsp/brg180.opt.tour all_tsp/ignore/

# Create the parsed_output directory
mkdir -p ./parsed_output
mkdir -p ./parsed_output/small
mkdir -p ./parsed_output/medium
mkdir -p ./parsed_output/large
mkdir -p ./parsed_output/very_large

# Create a .gitkeep file in the parsed_output directory
touch ./parsed_output/.gitkeep
# Create a .gitkeep file in the parsed_output/large directory
mkdir -p ./parsed_output/large
touch ./parsed_output/large/.gitkeep

# python ./parser.py