# CfTools - scripts for CodeForces
`cftools` is a collection of scripts for [CodeForces](https://codeforces.com) that uses the [CodeForces API](https://codeforces.com/apiHelp).

## ✨ Scripts
`cftools` currently include the following scripts:

* **Comulative AC count**
    - Count how many problems were solved since a specific date.

* **Daily ACs**
    - Finds problems solved on each day along with their rating.

* **Range rank**
    - In an official contest, where did you rank among the contestants within a given rating range around your rating (the rating at the time of participating).

* **Unsolved Contest Problems**
    - Find unsolved problems from contests with at least one submission. Why? Because you don't want to spoil nice unsolved virtuals. Handles div1/div2 contests where a problem occurs in both.

* **Virtual Performance**
    - Calculate rank/delta/performance of virtual/unofficial/offical contests.

* **What if?**
    - What If CodeForces virtual contests / unofficial participations were official? Calculates new ratings using deltas and simulates the past `n` contests.
 
## 📦 Installation
`cftools` can be *installed* in two different ways.
* You can download a pre-compiled binary from the [releases page](https://github.com/willthbill/cftools/releases).
* You can clone this repository and set up the development environment (see the [development section](#Development)). Then it should be as easy as running `pipenv run cftools`.

On linux you may optionally create an alias for the `cftools` executable, or add its location to the `PATH` variable.

## 🚀 Usage
* Run the executable
```
./cftools
```
* If you are using the development environment then check out the [pipenv development workflow section](#pipenv-development-environment).

When running `cftools` it will ask you to choose a script, and the script will guide you from there.

## 💻 Development 
The following sections explain the various parts of the project from a development perspective.

### Prerequisites
* `pipenv`
* `python3`
* `bash`

### Directory Structure**
* `src` should contain all source code, including scripts.
    - `src/lib` contains library code for interacting with the CodeForces API.
    - `src/apps` contains a directory for each script.
* `scripts` contains devops scripts.

### Pipenv Development Environment

`cftools` is written in `python` and uses `pipenv`.
Install `python` dependencies using:
```bash
$ pipenv install
```
Run `cftools` without building using:
```bash
$ pipenv run cftools
```
Run a specific script directory without building using (see `Pipfile` for script-names in the `[scripts]` section):
```bash
pipenv run <script-name>
``` 
To add a pip-package to the environment use:
```
pipenv install <package-name>
```
You may also activate the `pipenv` environment using
```
pipenv shell
```
Then you can run any python file directly.

### Building

* Run `pipenv run build`.
* `_dist` will then contain an executable for each script and `cftools`.
* `bin` will contain the `cftools` executable.

### Creating a Script
* Scripts should preferably be written in python, however scripts may be written in any language (see `src/main.py` and `scripts/build.sh`).
* When adding a script you should create a directory in `src/apps` with the script name, and the files used by the script should be placed within this directory.
* Then you should add a pipenv-script in the Pipfile's `[scripts]` section to run the script using pipenv (this applies to scripts in other languages as well).
* In order to run the script through `cftools` you should add an entry in the `scripts` list in `src/main.py`, each entry is a tuple of the form (name, function/command, description, credit).
* Lastly, you can add a line in `scripts/build.sh` for building the script into an single executable.

## 🔥 Contribution
Feel free to contribute a script (remember to give yourself credit), bug fixes or other things. Submit a pull request with the change.

`cftools` is created and maintained by William Bille Meyling (cf: [WillTheBill](https://codeforces.com/profile/WillTheBill), github: willthbill)
