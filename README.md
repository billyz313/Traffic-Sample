# Traffic-Sample - Solution Showcase

[![Python: 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IMapApps: Development](https://img.shields.io/badge/IMapApps-Development-green)](https://imapapps.com)

The purpose of this repository is to demonstrate different methods for displaying traffic flow data on a web application. This `showcase` branch contains three distinct approaches to solving the same problem. Each method is contained within its own dedicated directory for clarity and ease of use.

## Available Solutions

Explore the different solutions by navigating to their respective directories. Each directory contains the complete code for that method, along with its own `README.md` file that provides specific instructions for setup and usage.

* **`display-single-csv`**: This method demonstrates how to display traffic data from a single CSV file. It's a straightforward approach ideal for static data visualization.

* **`display-rotating-from-csv`**: This solution shows how to handle a series of CSV files, rotating through them to provide a dynamic, time-based visualization of traffic flow. This is useful for demonstrating changes over time from a static data source.

* **`display-rotating-from-db`**: This is the final and most robust solution, demonstrating how to display dynamic, rotating traffic data directly from a database. This approach is well-suited for applications that require live updates or are integrated with a larger data management system. The `README.md` in this directory contains the full setup instructions for the complete application, including how to import data and manage the server.

## Getting Started

To get the main application up and running, please refer to the detailed instructions in the `display-rotating-from-db` directory's `README.md` file. The setup process, which includes creating the environment and database, is applicable to all three solutions, although data import methods may vary.

### Setup and Installation (from the main branch)

For a quick reference on setting up the core environment, here are the commands you would typically run from the root of the repository:

1.  **Clone the Repository**:
    ```commandline
    git clone git@github.com:billyz313/Traffic-Sample.git
    ```

2.  **Create and Activate the Conda Environment**:
    ```commandline
    conda env create -f environment.yml
    conda activate Traffic_sample
    ```

3.  **Run Migrations and Create a Superuser**:
    ```shell
    cd Traffic-Sample
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py collectstatic
    ```

4.  **Import Data**:
    Refer to the `README.md` within each solution's directory for specific data import instructions.

---

### Authors

-   [Billy Ashmall (NASA/USRA)](https://github.com/billyz313)