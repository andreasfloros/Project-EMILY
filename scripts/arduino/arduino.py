from tkinter.constants import COMMAND
from imports import *

def check_platform():
	return platform.system() #check whether running windows/linux/macOS




def Windows_Check_Path():
	all_lines = []
	split_list = []
	command = "echo %PATH%"
	with subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, universal_newlines=True) as process:
		for line in process.stdout:
			all_lines.append(line.strip())
		all_lines = all_lines[0]
		decoded_line = all_lines.split(";")
		for elements in decoded_line:
			elements = elements.split("\\")
			for element in elements:
				split_list.append(element)
		if("arduino-cli" in split_list):
			sys.stdout.write("CLI has already been added to path.\n")
			return True
		else:
			sys.stdout.write("CLI has not been found in the path.\n")
			return False




def Linux_Check_Path():
	user = Linux_Darwin_Get_User()
	if(os.path.exists("/home/"+user+"/arduino-cli/arduino-cli")):
		sys.stdout.write("CLI file is in the right folder.\n")
		return True
	sys.stdout.write("CLI has either not been downloaded or not in the right folder.\n")
	return False




def Darwin_Check_Path():
	user = Linux_Darwin_Get_User()
	arduino_folder_path = "/Users/" + user + "/arduino-cli"
	folder_exists = os.path.exists(arduino_folder_path)
	if (not folder_exists):
		return False
	folder_contents = (os.listdir(arduino_folder_path))
	if("arduino-cli" not in folder_contents):
		return False
	return True




def Download_CLI(platform_name, path, app):
	downloadCLI_64bit_windows = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"
	downloadCLI_64bit_linux = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz"
	downloadCLI_64bit_darwin = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_64bit.tar.gz"

	sys.stdout.write("Downloading ...\n")
	sys.stdout.write("Platform detected: " + platform_name + '\n')
	if (platform_name == "Windows"):
		#Download the appropriate file from the URL
		requests.get(downloadCLI_64bit_windows)
		urlretrieve(downloadCLI_64bit_windows, "ArduinoCLI.zip")

		sys.stdout.write("Extracting contents...\n")
		#Extract contents of the zip file
		with zipfile.ZipFile("ArduinoCLI.zip","r") as zip_ref:
			zip_ref.extractall()

		#Moving CLI
		destination_path = path.split("\\")[0] + "\\arduino-cli"
		source_path = os.path.join(path, "arduino-cli.exe")
		if not os.path.exists(destination_path):
			os.makedirs(destination_path)
		else:
			sys.stdout.write("Folder called 'arduino-cli' already exists in base directory!\n")
		destination_path_file = os.path.join(destination_path, "arduino-cli.exe")
		if not os.path.exists(destination_path_file):
			shutil.move(source_path, destination_path_file)

		else:
			sys.stdout.write("Arduino-cli has already been moved to this folder\n")

		#Adding CLI to the user path variable
		sys.stdout.write("In the environment variables window that opens, please double click on path." + '\n')
		sys.stdout.write("Then click on 'New' and simply pase '{}' and press enter.".format(destination_path) + '\n')
		sys.stdout.write("Click the checkbox on the UI and then close the environment window.\n")

		command_open_environment_variables = "rundll32 sysdm.cpl,EditEnvironmentVariables"
		proc = subprocess.Popen(command_open_environment_variables, shell=True)
		proc.communicate()

	elif(platform_name == "Linux"):
		requests.get(downloadCLI_64bit_linux)
		urlretrieve(downloadCLI_64bit_linux, "ArduinoCLI.tar.gz")
		tar = tarfile.open("ArduinoCLI.tar.gz", "r:gz")
		sys.stdout.write("Extracting contents...\n")
		tar.extractall()
		tar.close()

		#Moving CLI file
		user = Linux_Darwin_Get_User()
		sys.stdout.write("User detected: " + user + "\n")
		arduino_folder_path = "/home/" + user + "/arduino-cli"
		commmand_dir = "mkdir /home/" + user +"/arduino-cli"
		command_mov = "mv arduino-cli /home/" + user + "/arduino-cli"
		folder_exists = os.path.exists(arduino_folder_path)
		if(folder_exists):
			folder_contents = (os.listdir(arduino_folder_path))
		if (not folder_exists):
			proc = subprocess.Popen(commmand_dir + "; " + command_mov, shell=True)
			proc.communicate()
		elif ((folder_exists) and ("arduino-cli" not in folder_contents)):
			proc = subprocess.Popen(command_mov, shell=True)
			proc.communicate()

	else:
		requests.get(downloadCLI_64bit_darwin)
		urlretrieve(downloadCLI_64bit_darwin, "ArduinoCLI.tar.gz")
		tar = tarfile.open("ArduinoCLI.tar.gz", "r:gz")
		sys.stdout.write("Extracting contents...\n")
		tar.extractall()
		tar.close()

		#Moving CLI
		user = Linux_Darwin_Get_User()
		sys.stdout.write("User detected: " + user + "\n")
		arduino_folder_path = "/Users/" + user + "/arduino-cli"
		command_dir = "mkdir /Users/" + user + "/arduino-cli"
		command_mov = "mv arduino-cli " + arduino_folder_path
		folder_exists = os.path.exists(arduino_folder_path)
		if(folder_exists):
			folder_contents = (os.listdir(arduino_folder_path))
		if(not folder_exists):
			proc = subprocess.Popen(command_dir + "; " + command_mov, shell = True)
			proc.communicate()
		elif((folder_exists) and ("arduino-cli" not in folder_contents)):
			proc = subprocess.Popen(command_mov, shell=True)
			proc.communicate()


def Download_Arduino_Dependencies(platform_name, app):
	sys.stdout.write("Downloading arduino dependencies...\n")
	dependencies_list = ["Arduino_TensorFlowLite", "Arduino_CMSIS-DSP"]
	if(platform_name == "Windows"):
		command_arduino_dependencies_download = 'arduino-cli lib download '
		command_arduino_dependencies_install= 'arduino-cli lib install '
		for x in dependencies_list:
			command_temp = [command_arduino_dependencies_download + x, command_arduino_dependencies_install + x]
			for command in command_temp:
				with subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True) as process:
					for line in process.stdout:
						sys.stdout.write(line + '\n')

	elif(platform_name == "Linux"):
		user = Linux_Darwin_Get_User()
		command_arduino_dependencies_download = 'export PATH="/home/' + user + '/arduino-cli:$PATH";arduino-cli lib download '
		command_arduino_dependencies_install = 'export PATH="/home/' + user + '/arduino-cli:$PATH";arduino-cli lib install '
		for x in dependencies_list:
			command_temp = [command_arduino_dependencies_download + x, command_arduino_dependencies_install + x]
			for command in command_temp:
				with subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True) as process:
					for line in process.stdout:
						sys.stdout.write(line + '\n')

	else:
		user = Linux_Darwin_Get_User()
		command_arduino_dependencies_download = 'export PATH="/Users/' + user + '/arduino-cli:$PATH"; arduino-cli lib download '
		command_arduino_dependencies_install = 'export PATH="/Users/' + user + '/arduino-cli:$PATH"; arduino-cli lib download '
		for x in dependencies_list:
			command_temp = [command_arduino_dependencies_download + x, command_arduino_dependencies_install + x]
			for command in command_temp:
				with subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True) as process:
					for line in process.stdout:
						sys.stdout.write(line + '\n')


def Get_Details(platform_name, app):
	sys.stdout.write("Getting board details..." + '\n')
	if(platform_name == "Windows"):
		command_board_list = "arduino-cli board list"
		with subprocess.Popen(command_board_list, stdout=subprocess.PIPE, universal_newlines=True) as process:
			for line in process.stdout:
				line = line.strip()
				if("No boards found." in line):
					app.menu_label.configure(text = "Could not retrieve board details, try again.")
					raise Exception("")
				if("arduino" in line):
					line = line.split(" ")
					fqbn = line[-2]
					com = line[0]
					core = line[-1]
					print("FQBN: ", fqbn, "COM: ", com,"Core: ", core)
					return fqbn, com, core

			app.menu_label.configure(text = "Could not retrieve board details, try again.")
			raise Exception("")

	elif(platform_name == "Linux"):
		user = Linux_Darwin_Get_User()
		command_board_list = 'export PATH="/home/' + user + '/arduino-cli:$PATH";arduino-cli board list'
		with subprocess.Popen(command_board_list, stdout=subprocess.PIPE, universal_newlines=True, shell=True) as process:
			for line in process.stdout:
				line = line.strip()
				if("No boards found." in line):
					app.menu_label.configure(text = "Could not retrieve board details, try again.")
					raise Exception("")
				if("arduino" in line):
					line = line.split(" ")
					fqbn = line[-2]
					com = line[0]
					core = line[-1]
					print("FQBN: ", fqbn, "COM: ", com,"Core: ", core)
					return fqbn, com, core

			app.menu_label.configure(text = "Could not retrieve board details, try again.")
			raise Exception("")

	else:
		user = Linux_Darwin_Get_User()
		command_board_list = 'export PATH="/Users/' + user + '/arduino-cli:$PATH"; arduino-cli board list'
		with subprocess.Popen(command_board_list, stdout=subprocess.PIPE, universal_newlines=True, shell=True) as process:
			for line in process.stdout:
				if("arduino" in line):
					line = line.split(" ")
					fqbn = line[-2]
					com = line[0]
					core = line[-1]
					print("FQBN: ", fqbn, "COM: ", com,"Core: ", core)
					return fqbn, com, core
			app.menu_label.configure(text = "Could not retrieve board details, try again.")
			raise Exception("")

def Windows_Run_Batch(fqbn, com, core, file_name, app):
	sys.stdout.write("Downloading core...\n")

	command_install_core = "arduino-cli core install " + core
	command_compile = "arduino-cli compile --fqbn " + fqbn + " " + file_name
	sys.stdout.write("Downloading dependencies... \n")
	command_list = [command_install_core, command_compile]
	for command in command_list:
		with subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True) as process:
			for line in process.stdout:
				sys.stdout.write(line + '\n')

	sys.stdout.write("Finished compiling, starting the uploading process...\n")

	command_upload = "arduino-cli upload -p " + com + " --fqbn " + fqbn + " " + file_name
	all_lines = []
	with subprocess.Popen(command_upload, stdout=subprocess.PIPE, universal_newlines=True) as process:
		for line in process.stdout:
			line = line[:-1]
			line = line.strip()
			all_lines.append(line)
			print(line)
	if(len(all_lines)>0):
		app.menu_label.configure(text = "Finished compiling and uploading!")
		sys.stdout.write("\nFinished Compiling and Uploading!\n")
	else:
		app.menu_label.configure(text = "There was an error!")
		sys.stdout.write("ERROR during uploading! Please close the UI and run it again\n")




def Linux_Darwin_Get_User():
	with subprocess.Popen("id -un", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as process:
		for line in process.stdout:
			user = line.decode("utf-8").strip()
	return user


def Linux_Run_Shell(fqbn, com, core, file_name, app):
	print(fqbn, com, core)
	all_line = []
	user = Linux_Darwin_Get_User()
	command = 'export PATH="/home/' + user + '/arduino-cli:$PATH";sudo chmod a+rw ' + com + ';arduino-cli core install '+core+'; arduino-cli compile --fqbn ' + fqbn + ' ' + file_name + '; arduino-cli upload -p ' + com + ' --fqbn ' + fqbn + ' ' + file_name
	with subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True) as process:
		for line in process.stdout:
			line = line[:-1]
			all_line.append(line.strip())
			print(line.strip())
	if(len(all_line)>0):
		app.menu_label.configure(text = "Finished compiling and uploading!")

	else:
		app.menu_label.configure(text = "There was an error!")
		sys.stdout.write("There was an error!\n")



def Darwin_Run_Shell(fqbn, com, core, file_name, app):
	user = Linux_Darwin_Get_User()
	all_lines = []
	path_change = 'export PATH="/Users/' + user + '/arduino-cli:$PATH"'
	core_install = "arduino-cli core install " + core + " "
	compile = 'arduino-cli compile --fqbn ' + fqbn + " " + file_name
	upload = 'arduino-cli upload -p ' + com + ' --fqbn ' + fqbn + " " + file_name

	command = path_change + "; " + core_install
	with subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True) as process:
		for line in process.stdout:
			line = line[:-1]
			all_lines.append(line.strip())
			print(line.strip())

	command = path_change + "; " + compile
	with subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True) as process:
		for line in process.stdout:
			line = line[:-1]
			all_lines.append(line.strip())
			print(line.strip())

	command = path_change + "; " + upload

	with subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True) as process:
		for line in process.stdout:
			line = line[:-1]
			all_lines.append(line.strip())
			print(line.strip())

	if(len(all_lines)>0):
		app.menu_label.configure(text = "Finished compiling and uploading!")
		sys.stdout.write("Compiled and Uploaded!\n")
	else:
		app.menu_label.configure(text = "There was an error!")
		sys.stdout.write("There was an error!\n")


def Start_Process(cli_is_installed, platform_name, app, file_name):

	if(not cli_is_installed):
		sys.stdout.write("Starting process to install CLI\n")
		Download_CLI(platform_name, wd, app)

	fqbn, com, core = Get_Details(platform_name, app)
	Download_Arduino_Dependencies(platform_name, app)

	if(platform_name == "Windows"):
		Windows_Run_Batch(fqbn, com, core, file_name, app)

	elif(platform_name == "Linux"):
		Linux_Run_Shell(fqbn, com, core, file_name, app)

	elif(platform_name == "Darwin"):
		Darwin_Run_Shell(fqbn, com, core, file_name, app)


def Move_h(source_path, platform_name, curr_path, app, file_name):
	h_name = "model.h"
	if(platform_name == "Windows"):
		source_path = source_path.replace("/", "\\")
	destination_path = os.path.join(curr_path, file_name, h_name)
	if not os.path.exists(destination_path):
		shutil.copy(source_path, destination_path)
	else:
		os.remove(destination_path)
		shutil.copy(source_path, destination_path)

	#adding include statement
	dummy = os.path.join(curr_path, file_name, "dummy.ino")
	original_ino = os.path.join(curr_path, file_name, file_name+".ino")
	line_add = '#include "' + h_name +'"'
	line_there = False

	#checking if the line is already present
	with open(original_ino, "r") as read_obj:
		for line in read_obj:
			if(h_name in line):
				line_there = True

	if(not line_there):
		with open(original_ino, "r") as read_obj, open(dummy, "w") as write_obj:
			write_obj.write(line_add + "\n")
			for line in read_obj:
				write_obj.write(line)
		os.remove(original_ino)
		os.rename(dummy, original_ino)

def check_cli(platform_name, app):
	if(platform_name == "Windows"):
			cli_is_installed = Windows_Check_Path()
	elif(platform_name == "Linux"):
		cli_is_installed = Linux_Check_Path()
	else:
		cli_is_installed = Darwin_Check_Path()
	return cli_is_installed


def send_to_arduino(app):
	try:
		app.menu_label.configure(text = "Converting and uploading model...")
		h_path = app.browse_model_entry.get()
		platform_name = check_platform()

		if(platform_name != "Darwin" and platform_name != "Linux" and platform_name != "Windows"):
			app.menu_label.configure(text = "OS not supported")
			raise Exception("OS Not supported")
		if(h_path and h_path.split(".")[-1] == "h"): # this will run if there is any path available, maybe check for the extension?
			Move_h(h_path, platform_name, wd, app, file_name="arduino_inference_script")
		else:
			app.menu_label.configure(text = "Please select a valid .h file")
			return
		cli_is_installed = check_cli(platform_name, app)
		file_name = os.path.join('"' + wd, 'arduino_inference_script"')
		Start_Process(cli_is_installed, platform_name, app, file_name)

	except:
		return