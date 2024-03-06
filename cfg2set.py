#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# Author:      徐哲阳
# FileName:    cfg2set.py
# CreatedDate: 2024-03-06 11:48:03
# Contact:     <xuzheyangchn@foxmail.com>
# Description: Convert kernel config to vscode settings
# Usage:
#     设置本地 VSCode 配置文件: python3 cfg2set.py -l /path/to/kernel
#     设置远端 VSCode 配置文件: python3 cfg2set.py -s /path/to/kernel
#     设置项目 VSCode 配置文件: python3 cfg2set.py -p /path/to/kernel /path/to/project
'''

import os
import sys
import json
import argparse
import platform


def load_config(config_file):
	defines = [
		"__GNUC__",
		"__KERNEL__",
		"MODULE",
	]
	for line in config_file:
		if line.startswith("#"):
			continue

		line = line.replace('\n', '')
		if len(line) == 0:
			continue

		if '=y' in line:
			line = line.replace('=y', ' = 1')
		elif '=' in line:
			line = line.replace('=', ' = ')

		if '"' in line:
			line = line.replace('"', '\"')

		defines.append(line)

	includes = [
		"include/",
		"include/uapi",
		"include/generated",
		"arch/__ARCH__/include",
		"arch/__ARCH__/include/uapi",
		"arch/__ARCH__/include/generated/",
		"arch/__ARCH__/include/generated/uapi"
	]

	return defines, includes


def parse_arguments():
	parser = argparse.ArgumentParser(description="Convert kernel config to vscode settings")
	parser.add_argument("-p", "--project", help="convert to project settings.json", action="store_true")
	parser.add_argument("-s", "--server", help="convert to vscode-server (remote-ssh) settings.json", action="store_true")
	parser.add_argument("-l", "--local", help="convert to vscode settings.json", action="store_true")

	parser.add_argument("kernel", help="kernel source directory")
	parser.add_argument("project_directory", help="project top-level directory", nargs='?', default=None)
	args = parser.parse_args()
	if not args.kernel:
		parser.error("kernel source directory is required")
	elif args.project and (not args.kernel or not args.project_directory):
		parser.error("project settings need kernel source and project directory")
	elif args.local and (not args.kernel):
		parser.error("local settings need kernel source directory")
	elif args.server and (not args.kernel):
		parser.error("server settings need kernel source directory")

	if args.kernel:
		args.kernel = os.path.realpath(args.kernel)
		if args.kernel.endswith('/'):
			args.kernel = args.kernel[:-1]

	if args.project_directory:
		args.project_directory = os.path.realpath(args.project_directory)
		if args.project_directory.endswith('/'):
			args.project_directory = args.project_directory[:-1]

	return args


def parse_env():
	architecture = os.environ.get('ARCH')
	if not architecture:
		machine_type = platform.machine()
		if "aarch64" in machine_type:
			machine_type = "arm64"
		architecture = machine_type

	cross_compile = os.environ.get('CROSS_COMPILE')
	if not cross_compile:
		compiler = 'gcc'
	elif cross_compile.endswith('-'):
		compiler = cross_compile + 'gcc'

	full_compiler = ''
	paths = os.environ["PATH"].split(os.pathsep)
	for path in paths:
		tmp_compiler = os.path.join(path, compiler)
		if os.path.exists(tmp_compiler) and os.access(tmp_compiler, os.X_OK):
			full_compiler = tmp_compiler
			break;

	if not full_compiler:
		print("Compiler not found:", compiler, ", the environment variable does not contain a compiler")
		raise SystemExit

	return architecture, full_compiler


def main():
	args = parse_arguments()
	config_path = args.kernel + "/.config"
	if not os.path.exists(config_path):
		print("kernel config not found, please run 'make xxx_xxx_defconfig' first")
		sys.exit(1)

	if args.project:
		settings_path = args.project_directory + "/.vscode/c_cpp_properties.json"
	elif args.local:
		if sys.platform.startswith('win'): # Windows系统
			settings_path = os.path.expandvars(r'%APPDATA%\Code\User\settings.json')
		elif sys.platform.startswith('darwin'): # MacOS系统
			settings_path = os.path.expanduser('~/Library/Application Support/Code/User/settings.json')
		elif sys.platform.startswith('linux'): # Linux系统
			settings_path = os.path.expanduser('~/.config/Code/User/settings.json')
		else: # 其他系统
			print("Unsupported operating system")
			sys.exit(1)
	elif args.server:
		settings_path = os.path.expanduser("~/.vscode-server/data/Machine/settings.json")

	try:
		settings_base_path = os.path.dirname(settings_path)
		if not os.path.exists(settings_base_path):
			os.makedirs(settings_base_path)
	except OSError as e:
		if e.errno == os.errno.EEXIST and os.path.isdir(settings_base_path):
			print("Directory already exists:", settings_base_path)
		else:
			print("Failed to create directory:", settings_base_path)
		raise


	architecture, full_compiler = parse_env()
	with open(config_path, 'r') as config_file:
		defines, includes = load_config(config_file)

	for index in range(len(includes)):
		includes[index] = args.kernel + '/' + includes[index].replace("__ARCH__", architecture)
		if not os.path.exists(includes[index]):
			print("Include directory not found:", includes[index], ", please build the kernel first")

	includes.insert(0, "${workspaceFolder}/**")

	if os.path.exists(settings_path):
		with open(settings_path, 'r') as settings_file:
			settings_json = json.load(settings_file)
	elif args.project:
		settings_json = {
			"configurations": [
				{
					"name": "kernel",
					"includePath": [],
					"defines": [],
					"compilerPath": ""
				}
			],
			"version": 4
		}
	else:
		settings_json = {
			"C_Cpp.default.includePath": [],
			"C_Cpp.default.defines": [],
			"C_Cpp.default.compilerPath": ""
		}

	if args.project:
		settings_json["configurations"][0]["name"] = 'kernel'
		settings_json["configurations"][0]["includePath"] = includes
		settings_json["configurations"][0]["defines"] = defines
		settings_json["configurations"][0]["compilerPath"] = full_compiler

	elif args.local or args.server:
		settings_json["C_Cpp.default.includePath"] = includes
		settings_json["C_Cpp.default.defines"] = defines
		settings_json["C_Cpp.default.compilerPath"] = full_compiler


	with open(settings_path, 'w+') as settings_file:
		json.dump(settings_json, settings_file, indent=4)
		settings_file.write('\n')
		print("Settings saved to", settings_path)

if __name__ == "__main__":
	main()
