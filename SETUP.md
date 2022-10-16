# Documentation for DiaryLite:

### Link to [DiaryLite Walkthrough](https://youtu.be/lsJwG6u0Hec)


DiaryLite is built upon Flask and SQLAlchemy in VSCode. To set up DiaryLite to run for yourself:
### Prereqs:
* Download VSCode and install the python extension. 
* Install python version 3.9.1 from [python.org](http://python.org). 
* Restart VSCode to prompt it recognizing the new python version. On windows, make sure the python interpreter is located in your path which you can check by running `path` in your command prompt. 
### In VSCode
* Once in VSCode, open settings in the bottom left and enable text wrapping to view my code easier
* Create a new workspace by going to the top and choosing File > Open Workspace, and then create a new folder.
* Unzip the project folder name DiaryLite.zip
* Drag the DiaryLite folder into the new workspace
* cd into your workspace and DiaryLite
* On macOS execute `python3 -m venv env` and on Windows execute `py -3 -m venv env`
* Open the Command-Palette through View > Command Palette and type `Python: Select Interpreter` and then select the virtual environment that begins with ./env
* If you do not see one of those environments *(as I do not but that's what VSCode documentation suggested)* then just select Python 3.9.1 
* In the Command-Palette run `Terminal: Create New Integrated Terminal`
* Execute `source env/bin/activate` on macOS or `env\Scripts\Activate.ps1` on Windows while in your DiaryLite file to activate your environment
* You will know if you're in a virtual environment when the command prompt shows (env) at the beginning
* In the Command-Palette, type `Python: Select Linter` and select pylint, installing it if not already installed from VSCode
* In the .vscode file that has been created in the workspace make sure settings.json contains these lines: 
`
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
}
`
* Upgrade pip by executing `python -m pip install --upgrade pip` in your virtal environment 
* Preliminary installation of flask: execute `python -m pip install flask`
* Execute `pip install -r requirements.txt` in your virtual environment, installing all the needed libraries for DiaryLite
### In DiaryLite
* Now, **assuming you're in the DiaryLite with (env) in the command prompt**, you should be able to execute `flask run` to run DiaryLite. 
* Head to the link shown in the command prompt after executing `flask run` or type localhost:5000 in your browser
* Use the website as you please, once you look at the code you may notice (at least on my end) that there are more than 50 red errors that pylint has identified 
    * These errors are likely saying that the Instance of 'SQLAlchemy' has no _ member
    * I learned that, no matter how irritating, these errors were purely superficial and did not interfere with the execution of the program

#### Other than that, feel free to explore my code and website and I hope you find my code and project at least a fraction as interesting and fun as it was for me to make it!

##### Documentation instructed by [VSCode's Flask Guide](https://code.visualstudio.com/docs/python/tutorial-flask#_create-a-requirementstxt-file-for-the-environment)





