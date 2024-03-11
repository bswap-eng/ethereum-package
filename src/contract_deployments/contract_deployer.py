import os
import subprocess
import re
import logging

contracts_root_folder = 'contracts'

logging.basicConfig(filename='/tmp/contract_deployer.log',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

def deploy_all_projects():
    # Get the list of project folders
    project_folders = [f for f in os.listdir(contracts_root_folder) if os.path.isdir(os.path.join(contracts_root_folder, f))]

    for project_folder in project_folders:
        project_path = os.path.join(contracts_root_folder, project_folder)
        contracts_folder = os.path.join(project_path, 'contracts')

        # Get the list of contract files in the folder
        contract_files = [f for f in os.listdir(contracts_folder) if f.endswith('.py') and f.startswith('deploy_')]

        # Check that each file has a 'deploy_<int>_' prefix
        regex = re.compile(r'^deploy_\d+_')
        for contract_file in contract_files:
            if not regex.match(contract_file):
                print(f"Project {project_folder}: Contract {contract_file} does not have a valid prefix.")
                continue

            # Extract the order number from the contract file name
            order_number = int(contract_file.split('_')[1])

            # Execute the contract as a subprocess
            contract_path = os.path.join(contracts_folder, contract_file)
            result = subprocess.run(['python', contract_path], capture_output=True, text=True)

            # Check the result and take further actions if needed
            if result.returncode == 0:
                print(f"Project {project_folder}: Contract {contract_file} (Order {order_number}) deployed successfully.")
                print("Response:", result.stdout)
            else:
                print(f"Project {project_folder}: Error deploying contract {contract_file} (Order {order_number}).")
                print("Error:", result.stderr)

if __name__ == '__main__':
    logging.info('Starting all contract deployments.')
    deploy_all_projects()
    logging.info('Finished all contract deployment.')