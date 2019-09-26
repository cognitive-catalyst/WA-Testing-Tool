
import os
import sys


def copy_project_asset_file_to_python_env(project=project, asset_filename='asset_file_in_project', python_env_target_dir='python environemnt target directory'):
    filename_with_path=python_env_target_dir+'/'+asset_filename
    #print(os.listdir(python_env_target_dir))
    
    print('Copying file {0} from project assets to python environment'.format(asset_filename))
    file_from_project=project.get_file(asset_filename)
    file_to_write_local = open(filename_with_path, 'wb')
    file_to_write_local.write(file_from_project.read())
    file_to_write_local.close()
    file_from_project.close()

    print('Done.')
    print('Target directory listing: ')
    print(os.listdir(python_env_target_dir))
    print('File: ')
    print(os.stat(filename_with_path))


def copy_python_env_file_to_project_asset(project=project, python_env_source_dir='python environemnt source directory', python_env_filename='python environment file name'):
    filename_with_path=python_env_source_dir+'/'+python_env_filename
    print('Source directory listing: ')
    print(os.listdir(python_env_source_dir))
    print('File: ')
    print(os.stat(filename_with_path))
    print('Copying file {0} from python environment to project assets'.format(python_env_filename))
    file_data=open(filename_with_path, 'rb')
    project.save_data(data=file_data.read(),file_name=python_env_filename,overwrite=True)
    file_data.close() 
    print('Done.')
    #print('Directory listing: ' + os.listdir(python_env_source_dir)





def copy_python_env_data_results_zip_to_project_asset(project=project, data_results_zip_filename='zip file name'):
    
    #create a zip file of the data directory
    print('Verify data directoy was created/exists')
    print('Data directory listing: ')
    print(os.listdir(WA_TOOL_DATA_DIR_W_PATH))
  
    # !echo $WA_TOOL_INSTALL_DIR_W_PATH/$WA_TOOL_RESULTS_TARGZ_FILE $WA_TOOL_DATA_DIR_W_PATH

    print('Creating data zip file...')
    #subprocess.call(["tar", "-cvf", WA_TOOL_RESULTS_TARGZ_FILE, WA_TOOL_DATA_DIR_W_PATH])
    !tar -czvf $WA_TOOL_INSTALL_DIR_W_PATH/$WA_TOOL_RESULTS_TARGZ_FILE $WA_TOOL_DATA_DIR_W_PATH

    print('Verify .tar.gz file was created...')
    #check for the file in the list
    print('Directory listing. Check for the zip file: ')
    print(os.listdir(WA_TOOL_INSTALL_DIR_W_PATH))
    print('Zip file: ')
    print(os.stat(WA_TOOL_INSTALL_DIR_W_PATH+'/'+WA_TOOL_RESULTS_TARGZ_FILE))

    #copy thezip file to project asset
    print('Copying data zip file to project asset.')
    copy_python_env_file_to_project_asset(project, WA_TOOL_INSTALL_DIR_W_PATH, WA_TOOL_RESULTS_TARGZ_FILE)


def copy_test_input_files_from_assets_to_python_env():
    
    #Depending on the test type copy  input files from the project asset to the local python env
    
    #If kfold no files needed
    #If blind or test we need test_input_file
    
    if ( PARAMS['mode'].lower() == 'kfold'):
        #do nothing
        print("No input files needed to copy for kfold.")
    if ( PARAMS['mode'].lower() == 'blind'):   
        # copy PARAMS['test_input_file'] to python env        
        print("Copying input file for blind test to python env...")
        copy_project_asset_file_to_python_env(project, PARAMS['test_input_file'], WA_TOOL_DATA_DIR_W_PATH)       
    if ( PARAMS['mode'].lower() == 'test'):   
        # copy PARAMS['test_input_file'] to python env
        print("Copying input file for standard test to python env...")
        copy_project_asset_file_to_python_env(project, PARAMS['test_input_file'], WA_TOOL_DATA_DIR_W_PATH)       

    ##TBD TBD  Not using the feature.
    #Add this to PARAMS
    #'previous_blind_out' : 'NA', #; Previous blind test output file or NA. 'prev-test-out.csv | 'NA'
    #if ( PARAMS['previous_blind_out'].lower() != 'na'):   
        #PARAMS['previous_blind_out']
        #print("Copying previous_blind_out input file to python env...")
        #copy_project_asset_file_to_python_env(project, PARAMS['previous_blind_out'], WA_TOOL_DATA_DIR_W_PATH)       

            
    if ( PARAMS['partial_credit_table'].lower() != 'na'):   
        #PARAMS['partial_credit_table']
        print("Copying partial_credit_table input file to python env...")
        copy_project_asset_file_to_python_env(project, PARAMS['partial_credit_table'], WA_TOOL_DATA_DIR_W_PATH)
        
        


def write_config_file_to_python_env():
    # Reads the basic user configution
    # Add the advanced configurations
    # Writes / or refreshes the configuration file to the file system where WA tool can read from
    #Some are common/fixed, some utilized from user input, and some are set based on conditions 
    
    config = configparser.ConfigParser()

    config['DEFAULT'] = {
        'mode': PARAMS['mode'],
        'workspace_id': PARAMS['workspace_id'],
        'temporary_file_directory': WA_TOOL_DATA_DIR_W_PATH, # './data', #PARAMS['temporary_file_directory'],
        #'test_output_path' : WA_TOOL_DATA_DIR_W_PATH+'/'+PARAMS['test_output_file'], #'/test-out.csv', - 
        #'test_input_file' :  WA_TOOL_DATA_DIR_W_PATH+'/'+PARAMS['test_input_file'], #  './data/'+PARAMS['test_input_file'],
        'fold_num' : PARAMS['fold_num'],
        'keep_workspace_after_test' : 'no', #PARAMS['keep_workspace_after_test'],
        'weight_mode' : PARAMS['weight_mode'],
        'max_test_rate' : PARAMS['max_test_rate'],
        'conf_thres' : PARAMS['conf_thres']
    }

        
    config['ASSISTANT CREDENTIALS'] = {
        'username': PARAMS['username'],
        'password': PARAMS['password'],
        'iam_apikey': PARAMS['password'], #PARAMS['iam_apikey'],
        'url' : PARAMS['url']

    }

    if ( PARAMS['mode'].lower() == 'kfold'):
        #config['DEFAULT']['test_output_path']= WA_TOOL_DATA_DIR_W_PATH+'/test-out-kfold.csv' #This is not needed for kfold. 
        config['DEFAULT']['out_figure_path']= WA_TOOL_DATA_DIR_W_PATH+'/kfold-figure.png'
        #config['DEFAULT']['kfold_figure_title']="Kfold Test" #There is no exposed variable for this. only for blind test
    
    if ( PARAMS['mode'].lower() == 'test'):
        config['DEFAULT']['test_input_file']= WA_TOOL_DATA_DIR_W_PATH+'/'+PARAMS['test_input_file'] #  './data/'+PARAMS['test_input_file'],
        config['DEFAULT']['test_output_path']= WA_TOOL_DATA_DIR_W_PATH+'/test-out.csv'
        

    if ( PARAMS['mode'].lower() == 'blind'):
        config['DEFAULT']['test_input_file']= WA_TOOL_DATA_DIR_W_PATH+'/'+PARAMS['test_input_file'] #  './data/'+PARAMS['test_input_file'],
        config['DEFAULT']['test_output_path']= WA_TOOL_DATA_DIR_W_PATH+'/blind-test-out.csv'
        config['DEFAULT']['out_figure_path']= WA_TOOL_DATA_DIR_W_PATH+'/blind-figure.png'
        config['DEFAULT']['blind_figure_title']="Blind Test with Golden Intent"

    ##TBD TBD  Not using the feature.
    #Add this to PARAMS
    #'previous_blind_out' : 'NA', #; Previous blind test output file or NA. 'prev-test-out.csv | 'NA'    
    #if previous blind output is provided add the line to the config file; otherwise don't add
    #if ( PARAMS['previous_blind_out'].lower() != 'na'):   
    #    config['DEFAULT']['previous_blind_out']= WA_TOOL_DATA_DIR_W_PATH+'/'+PARAMS['previous_blind_out'] # './data/'+PARAMS['previous_blind_out'],

    #if partial_credit_table is used add the line to the config file; otherwise don't add
    if ( PARAMS['partial_credit_table'].lower() != 'na'):   
        config['DEFAULT']['partial_credit_table']= WA_TOOL_DATA_DIR_W_PATH+'/'+PARAMS['partial_credit_table'] #'./data/'+PARAMS['partial_credit_table'],
    
    print('Writing config file...')
    with open(WA_TOOL_CONFIG_FILE_W_PATH, 'w') as configfile:
        config.write(configfile)
    configfile.close() 
    print('Done.')
    
