#!/bin/bash

# Loop to execute the command 20 times
for i in {1..2}
do
  echo "Running iteration $i..."
  python simulator.py --player_1 student_agent --player_2 random_agent --board_size=6 > /Users/trinhnhathuy/pythonProject/COMP424-Project-test/output.txt
done

echo "20 games done!"
