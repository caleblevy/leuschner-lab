#!/usr/bin/env sh
Levy_Langley=/Users/caleblevy/galaxy-lab/langley
scp ${Levy_Langley}/File_Managing_Functions.py heiles:~/langley
echo 'Managing Functions'
scp ${Levy_Langley}/Pickle_Data.py heiles:~/langley
echo 'Pickle_Data'
scp ${Levy_Langley}/Load_Raw_Data.py heiles:~/langley
echo 'Load_Raw_Data'
scp ${Levy_Langley}/Envelope_Functions.py heiles:~/langley
echo 'Envelope_Functions'
scp ${Levy_Langley}/Plotting_Wrappers.py heiles:~/langley
echo 'Plotting_Wrappers'
scp ${Levy_Langley}/Smooth_Data.py heiles:~/langley
echo 'Smooth_Data'
scp ${Levy_Langley}/Combine_Data.py heiles:~/langley
echo 'Combine_Data'

scp ${Levy_Langley}/readme_caleb heiles:~/langley
echo 'readme_caleb'
scp ${Levy_Langley}/Data_Specification.txt heiles:~/langley
echo 'Data_Specification'
