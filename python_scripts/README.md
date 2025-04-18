Use these steps if you want to download the historical data on the VM and load it to the BigQuery table.

Python 3 comes preinstalled on the VM type chosen in the [Create a VM instance](../README.md#create-a-vm-instance) subsection.
You can check this with
   ```bash
    which python
    # or
    python3 --version  # the default version is Python 3.8.10
   ```

### Install pip
You need to install pip to be able to install the requiered packages.
   ```bash
    # Update package list
    sudo apt update

    # Install pip for Python 3
    sudo apt install -y python3-pip

    # Verify the installation 
    pip --version
   ```


### Create a virtual environment and install the packages
virtualenv allows you to create a virtual environment with your chosen python version. Ensure you have virtualenv installed by using pip.
   ```bash
    pip install virtualenv
   ```

Add the folder where virtualenv was installed to PATH.
   ```bash
    # Open your shell config file
    nano ~/.bashrc

    # Add this line at the bottom
    export PATH="$HOME/.local/bin:$PATH"  # Control + X and Y to save

    # Reload the shell
    source ~/.bashrc

    # Test that it was added
    which virtualenv
   ```

Create a python virtual environment and install the packages from `requirements.txt` file.
   ```bash
    # Create the environment
    virtualenv -p python3.8 venv

    # Activate it
    source venv/bin/activate

    # Install the packages
    pip install -r python_scripts/requirements.txt
   ```