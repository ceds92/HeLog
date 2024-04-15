# HeLog
 Software to log data for the Monash University lHe plant

# Installation
1. Clone this repository
3. Download and install [Anaconda](https://docs.anaconda.com/free/anaconda/install/index.html)
4. Open Anaconda Prompt
5. In Anaconda Prompt, navigate to the repository directory ```cd <path-to-cloned-HeLog-folder>```
6. Create a virtual environment with the command: ```conda create --name HeLog```
7. Activate the environment: ```conda activate HeLog```
8. Install Python with: ```conda install python```
9. Install the HeLog code with: ```pip install .```
10. Navigate to the HeLog folder using ```cd HeLog``` (now you should be in the folder <path-to-repo>/HeLog/HeLog/)
11. Run the application with: ```bokeh serve --show app.py```

# Using
## Demo mode
You can test the program before hooking it up to the plant:
In app.py, change the ```demo``` parameter to ```True```:
 ```Python
  demo = True
 ```
Making this change will replace the He plant with a random number generator when you run the code. This lets you see what the plots look like without having to plug into the plant controller.

## Live mode
The other parameter to be aware of is the ```live``` parameter.
If ```live = False``` then data will be updated but changes to the databse file will not be saved.
If ```live = True``` then new data will be committed to the database file.

## Terminating
To terminate the program, press ```control + c``` in Anaconda Prompt to stop the program safely.
Closing the browser tab will not stop the program from running in the background.
You can close and open the browser tab without affecting the data logger.
If you accidentally close the browser tab, you can get back to the plot by going to http://localhost:5006/app in a new tab.
