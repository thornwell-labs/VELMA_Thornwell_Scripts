"""
Runs a sequence of VELMA simulations from the command line. Builds the Java
command for the VELMA simulator (parallel or single mode) and runs it for a
series of XML configuration files, e.g. one per downscaling factor.
"""

import subprocess

parallel_flag = True
allocated_memory = "-Xmx8G"
jar_path = "path/to/JVelma_dev-test_v005.jar"
xml_path = "path/to/VELMA_Watersheds/Nisqually/Data_Inputs30m/resampled/xmls/WA_Nisqually30m_28Feb2025_resampled_"
max_processes = 3

# Function to build VELMA command and run as a sub-process
def run_velma(parallel_flag, allocated_memory, jar_path, xml_path, max_processes=1):
    if parallel_flag:
        command = ["java", allocated_memory, "-cp", jar_path, "gov.epa.velmasimulator.VelmaParallelCmdLine", xml_path,
                  f"--maxProcesses={max_processes}"]
    else:
        command = ["java", allocated_memory, "-cp", jar_path, "gov.epa.velmasimulator.VelmaSimulatorCmdLine", xml_path]
    
    command_str = ' '.join(command)
    try:
        subprocess.run(command_str, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        print(f"VELMA failed for XML file: {xml_path}")

# for xml_number in range(5, 10):
#     print(f'Running VELMA downscaled {xml_number}x')
#     xml_name = f'{xml_path}{xml_number}.xml'
#     run_velma(parallel_flag=parallel_flag, allocated_memory=allocated_memory, jar_path=jar_path, xml_path=xml_name, max_processes=max_processes)

allocated_memory = "-Xmx5G"
max_processes = 3
for xml_number in range(10, 15):
    print(f'Running VELMA downscaled {xml_number}x')
    xml_name = f'{xml_path}{xml_number}.xml'
    run_velma(parallel_flag=parallel_flag, allocated_memory=allocated_memory, jar_path=jar_path, xml_path=xml_name, max_processes=max_processes)