#!/usr/bin/env sh
Levy_Langley=/Users/caleblevy/galaxy-lab/langley
scp heiles:~/langley/File_Managing_Functions.py ${Levy_Langley}
echo 'Managing Functions'
scp heiles:~/langley/Pickle_Data.py ${Levy_Langley}
echo 'Pickle_Data'
scp heiles:~/langley/Load_Raw_Data.py ${Levy_Langley}
echo 'Load_Raw_Data'
scp heiles:~/langley/Envelope_Functions.py ${Levy_Langley}
echo 'Envelope_Functions'
scp heiles:~/langley/Plotting_Wrappers.py ${Levy_Langley}
echo 'Plotting_Wrappers'
scp heiles:~/langley/Smooth_Data.py ${Levy_Langley}
echo 'Smooth_Data'
scp heiles:~/langley/Combine_Data.py ${Levy_Langley}
echo 'Combine_Data'

scp heiles:~/langley/readme_caleb ${Levy_Langley}
echo 'readme_caleb'
scp heiles:~/langley/Data_Specification.txt ${Levy_Langley}
echo 'Data_Specification'

scp heiles:~/langley/pklio.py ${Levy_Langley}
scp heiles:~/langley/data/grid.pkl ${Levy_Langley}/data