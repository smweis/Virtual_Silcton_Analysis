# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 10:53:55 2020

@author: stevenweisberg

This script will take as input a data directory containing text files
generated by the Silcton Standalone pointing task and output 
a directory with csv files, each of which is one participant's data coded for pointing error.

To run this, put your output text files into one folder (and no other text files). 

The easiest way to run this is to open your terminal or Powershell and run
this script as a command line argument. 

All you need to do is pass arguments to point to your data_directory and the output directory. 

Optionally, you can pass 'true' as a third argument if you would also like to return the buggy scoring. 

python code_pointing.py [data_directory] [output_directory]

"""
import datetime
import pandas as pd
import numpy as np
import os


def get_files(data_dir):
# Get all pointing files within data directory
    dir_files = os.listdir(data_dir)
    file_names = [x for x in dir_files if 'txt' in x]
    full_file_names = []
    for file in file_names:
        full_file_names.append(data_dir + os.path.sep + file)
    
    return full_file_names
    
def good_pointing_calculation(actual,guess):
    diff = abs(actual - guess)
    if diff > 180:
        diff = 360-diff
    return diff

def bad_pointing_calculation(actual,guess):
    guess = abs(guess)
    actual = abs(actual)
    diff = abs(actual - guess)
    if diff > 180:
        diff = 360-diff
    return diff
    
def vector_subtraction(point_from,target,facing):
    #vector subtraction logic from here:
    #https://stackoverflow.com/questions/21483999/using-atan2-to-find-angle-between-two-vectors
    vector1 = np.subtract(facing,point_from) # center the facing and target points
    vector2 = np.subtract(target,point_from)
    # Now calculate the signed angle between them as the difference between arctans (y,x)
    angle = np.arctan2(vector1[1],vector1[0]) - np.arctan2(vector2[1],vector2[0])
    angle = np.rad2deg(angle)

    # Correct for being the wrong side of 180
    if angle > 180:
        corrected_angle = angle - 360
    elif angle < -180:
        corrected_angle = 360 + angle
    else:
        corrected_angle = angle

    return corrected_angle

def get_silcton_data():
        
    # This section of code will re-calculate the angles from the original coordinates
    # from seeds.rb on website (original coordinates, negative Y)
    # Note - there was an irregularity in the website where the Y-values were POSITIVE.
    # These have been changed to negative to allow for proper angle calculations.
    # This made no difference in the original trigonometry, but must be adjusted now.
    
    building_names = [['Batty House','Lynch Station','Harris Hall','Harvey House',
    'Golledge Hall','Snow Church','Sauer Center','Tobler Museum']] * 2
    
    batty_buildings = ['Batty House','Lynch Station','Harris Hall','Harvey House']
    golledge_buildings = ['Golledge Hall','Snow Church','Sauer Center','Tobler Museum']
    
    index = pd.MultiIndex.from_product(building_names,names=['start_landmark','target_landmark'])
    
    
    
    data = {'Batty House': [0,63,-292,91,-309],
            'Lynch Station':[1,67,-169,158,-222],
            'Harris Hall':[2,268,-262,284,-251],
            'Harvey House':[3,310,-498,300,-488],
            'Golledge Hall':[4,635,-303,628,-255],
            'Snow Church':[5,731,-262,692,-258],
            'Sauer Center':[6,683,-69,687,-141],
            'Tobler Museum':[7,536,-189,536,-197]}
    
    landmarks_df = pd.DataFrame.from_dict(data, orient='index',
                           columns=['visit_order',
                           'front_door_pixel_x',
                           'front_door_pixel_y',
                           'pointing_location_pixel_x',
                           'pointing_location_pixel_y'])
    
    # The unsigned answers.
    unsigned_actual_direction = [np.nan,47.32798389,37.5286373,93.19423766,51.76768154,48.19947553,30.3316951,37.30802198,
    		   130.6542463,np.nan,7.021704671,48.19593801,3.323863738,8.968174613,29.20903342,17.95076442,
    		   83.35216568,114.5627943,np.nan,2.146796904,77.71082192,84.7281122,110.6574336,99.95984558,
    		   46.54689912,32.28246429,4.196894849,np.nan,64.9530254,66.19140238,46.29205396,42.14615863,
    		   173.5694617,173.9683139,176.2022806,139.9309368,np.nan,1.204134401,76.21088344,147.0284471,
    		   90.64700942,79.44851915,88.09346154,119.6929579,125.8431145,np.nan,0.279262352,63.69277617,
    		   6.744508622,17.76205492,4.240040564,23.09134403,51.85616181,89.63525726,np.nan,2.713388186,
    		   171.0086651,156.2355625,173.2852643,147.248191,67.30353066,38.78279809,20.69981416,np.nan]
    
    df = pd.DataFrame(unsigned_actual_direction, index=index, columns=['unsigned_actual_direction'])

    # Initialize columns
    df['actual_direction'] = recalculate_answers(landmarks_df)
    df.dropna(subset=['unsigned_actual_direction'],inplace=True)
    
    return df, batty_buildings, golledge_buildings

def recalculate_answers(landmarks_df):
        
    # Initialize answers list
    recalculated_answers = []
    
    # This loop goes through each landmark and calculates the pointing error.
    for i,j in enumerate(landmarks_df.index):
        # if the point_from location is at the end of the route
        # the facing direction is toward the previous diamond
        # otherwise it's toward the next diamond
        if i in (3,7):
            face = i - 1
        else:
            face = i + 1
    
        # Create two 2D vectors,
        # point_from = the point for the landmark that judgment was made from
        # facing = the point of the gem for the facing landmark.
        point_from = [landmarks_df['pointing_location_pixel_x'][j],landmarks_df['pointing_location_pixel_y'][j]]
        facing = [landmarks_df['pointing_location_pixel_x'][face],landmarks_df['pointing_location_pixel_y'][face]]
    
        # Loop through each landmark, skipping if the landmark is the one that trial was made from.
        for x,y in enumerate(landmarks_df.index):
            if x == i:
                value = np.nan
            else:
                target = [landmarks_df['front_door_pixel_x'][y],landmarks_df['front_door_pixel_y'][y]]
                value= vector_subtraction(point_from,target,facing)
    
    
            recalculated_answers.append(value)
    
    return recalculated_answers



def code_pointing(data_dir, output_dir, incorrect_angles=False, validate=False):
    
    
    # If we are validating, it is excpected this file is in the original git repository.
    if validate:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'validation')
        output_dir = data_dir
    
        
        
    # Get list of data file names
    data_files = get_files(data_dir)
    
    #open input file, read as data
    for i,j in enumerate(data_files):
    
        # Get constants about Silcton    
        df, batty_buildings, golledge_buildings = get_silcton_data()
        
        with open (j, "r") as my_file:
            try:
                print(f'Loading data for {j}')
                participant_data = pd.read_csv(my_file)
            except: 
                participant_data = pd.read_csv(data_files[i],error_bad_lines=False,skiprows=5)
                # Get participant ID
                participant_id = pd.read_csv(data_files[i],nrows=2)
                participant_id = participant_id.iloc[1,0].split(' ')[-1]
                df['participant'] = participant_id
                print('Success!')
                print('Header lines expected. Skipped 2 lines.')
                
        for index,row in participant_data.iterrows():
            point_from = row['pointingDiamondIndex']
            point_to = row['targetBuildingIndex']
            
            if point_from in batty_buildings and point_to in batty_buildings:
                df.loc[(point_from,point_to),'within_between'] = 'within_a'
            elif point_from in golledge_buildings and point_to in golledge_buildings:
                df.loc[(point_from,point_to),'within_between'] = 'within_b'
            else:
                df.loc[(point_from,point_to),'within_between'] = 'between'
                
            df.loc[(point_from,point_to),'participant_response'] = row['pointingAngle']
            df.loc[(point_from,point_to),'point_order'] = index
        
        
        # Calculate correct absolute error
        df['correct_absolute_error'] = [good_pointing_calculation(x,y) 
                                        for x, y in zip(df['actual_direction'], 
                                                        df['participant_response'])]
        
        columns = ['participant','start_landmark',
                   'target_landmark','point_order',
                   'participant_response','actual_direction',
                   'correct_absolute_error','within_between']

        
        # Calculate INCORRECT absolute error (if user wants it)
        if incorrect_angles:
            df['do_not_use_incorrect_absolute_error'] = [bad_pointing_calculation(x,y) 
                                                         for x, y in zip(df['unsigned_actual_direction'],
                                                                         df['participant_response'])]
            columns.append('do_not_use_incorrect_absolute_error')
            
        # Save output
        to_save_name = output_dir+os.path.sep+'standalone_pointing_' + participant_id + '.csv'
    
        if os.path.isfile(to_save_name):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            to_save_name = output_dir+os.path.sep+'standalone_pointing_output_'+ participant_id +'_'+timestamp+'.csv'
            
        
        # Reorder and clean up
        df.reset_index(inplace=True)
        df = df[columns]
        
        df.to_csv(to_save_name,index=False)
        
        return df

if __name__ == "__main__":
    import sys
    
    incorrect_angles = sys.argv[3].lower() == 'true'
    validate = sys.argv[4].lower() == 'true'
    
    df = code_pointing(sys.argv[1],sys.argv[2],incorrect_angles,validate)
    