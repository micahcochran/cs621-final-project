# Legal Text Website

CS 621 - Web Application Development Project<br>
Project Title: Legal Text Website <br>
Due: 2022-08-05<br>
Final Project<br>

## Description
This is software that updates the usability and look of the Alabama Constitution's website.  For more information look [Legal Text Website](https://www.micahcochran.net/projects/legal-text/) on my website.

## Team
Micah Cochran
Everything was my work, unless specified.  This is noted below in [Attribution](#attribution), but this was more fully explained in my project report.

## Installation
There are two methods to install Vagrant (preferred) and bare metal.

First step is to download the software from GitHub.

Either by (1) cloning the repo:
```bash
git clone https://github.com/micahcochran/cs621-final-project.git legal-text
```
OR (2) [download the ZIP file](https://github.com/micahcochran/cs621-final-project/archive/refs/heads/main.zip)

### Vagrant
Vagrant is the preferred way to install the Legal Text website.

System Requirements: 
* Vagrant (developed on version 2.2.6)
* a hypervisor - developed using Virtualbox  (developed on version 6.1.34)


### From the console
Go to the console and run the following commands
```bash
vagrant up
```

Note: If it complains about there being a newer version of the box run `vagrant box update` to update the box before installation.


The vagrant box will start and run the Legal Text website.
Open your browser to http://localhost:5000/ Alternatively, use the private
network address at http://192.168.59.10:5000/   

## Installation - Bare metal

System Requirements:
* Python 3.7+
* Pip
* MongoDB (developed on version 3.6.8)
* ~~Anaconda~~
* venv

If you are using Ubuntu Linux 20.04 LTS, you can run this command to install all of the prereqs:
```base
apt-get install -y python3 python3-pip python3-venv mongodb mongodb-server mongodb-clients mongo-tools
```

Later version of Ubuntu/Debian Linux do not include MonogoDB, so those have to be installed using other repositories.  You will want to install MongoDB Community Edition.
<https://www.mongodb.com/docs/manual/administration/install-community/>

Go to terminal to the directory where the legal-text/ folder is located. Make a virtual environment (venv) and install the python libraries.

```base
cd legal-text/
python3 -m venv lt-env
conda activate lt-env
pip install -r requirements.txt
```

Restore the MongoDB database from files:
```bash
mongorestore --db=legal_text ./mongo-backup/dump/legal_text/
```

To run the web application:
```bash
./legal-text.py
```

Open your browser to http://localhost:5000/


## Notes
The Vagrant image uses Ubuntu 20.04 (end of life in April of 2025).  At development time, Ubuntu LTS 22.04 had some issues installing MongoDB. Docker was investigated, but ran into a slightly more complicated configuration when using official MongoDB docker image.  (Vagrant is Virtual Machine software, where Docker is containerization.  These are similar, but Docker would be preferred for website software. )

The parsing code, `parse_constitution.py`, scrape the text from the Alabama Constitution website.  It used the BeatifulSoup library to help with parses the HTML and store it in MongoDB.  Unfortunately, the parsing code has been lost, but the MongoDB dumps from tha code are in the project [/mongo-backup/dump/legal_text/](/mongo-backup/dump/legal_text/).

## Attribution
* Fonts are hosted by Google Fonts: 
   * Libre Baskerville and Merriweather. These are serif fonts mainly intended to display legal text.
   * Inter.  This is a san-serif font mainly for settings.
   * These fonts are licensed under the SIL Open Font License (OFL)
* Graphics
   * Favicon - [Book icons created by Freepik - Flaticon](https://www.flaticon.com/free-icon/open-book_167755), this is free to use with attribution.
      * Used https://www.favicon-generator.org/ to generate favicons for multiple platforms.
   * link icon - [Chain icons created by Freepik - Flaticon](https://www.flaticon.com/premium-icon/link_530742)
