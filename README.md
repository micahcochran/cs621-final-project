# Legal Text Website

CS 621 - Web Application Development Project<br>
Project Title: Legal Text Website <br>
Due: 2022-08-05<br>
Final Project<br>


## Team
Micah Cochran
Everything was my work unless specified.  This is noted below in [Attribution](#attribution), but this was more fully explained in my project report.

## Installation
There are two methods to install Vagrant (preferred) and bare metal.

First step is to download the software from GitHub.

Either by (1) cloning the repo:
```bash
git clone https://github.com/micahcochran/cs621-final-project.git
```
OR (2) [download the ZIP file](https://github.com/micahcochran/cs621-final-project/archive/refs/heads/main.zip)

### Vagrant
Vagrant is the preferred way to install the Legal Text website.

System Requirements: 
* Vagrant (developed on version 2.2.6)
* a hypervisor - I used Virtualbox  (developed on version 6.1.34)


### From the console
Go to the console and run the following commands
```bash
vagrant up
```

Vagrant will prompt for a network interface to bridge to.

```bash
vagrant ssh
```

That should give you a secure shell into an Ubuntu 20.04 Virtual Machine. Do the following to run.

```bash
cd legal-text/
./legal-text.py
```

Open your browser to http://192.168.59.10:5000/  This is the private network
port.  Other ports have also been left open, so those might also work.

## Installation - Bare metal

System Requirements:
* Python 3.7+
* Pip
* MongoDB (developed on version 3.6.8)
* Anaconda

Go to terminal to the directory where the legal-text/ folder is located.

```base
conda create -n lt-env python=3.10
conda activate lt-env
cd legal-text/
pip install -r requirements.txt
```

To run the web application:
```bash
./legal-text.py
```

Open your browser to http://localhost:5000/


## Vagrant notes
The Vagrant image uses Ubuntu 20.04, which has an end of life in April of 2025.  This is because at the time of development Ubuntu LTS 22.04 had some issues installing MongoDB.

## Project Notes
The parsing code, `parse_constitution.py`, scrape the text from the Alabama Constitution website.  It used the BeatifulSoup library to help with parses the HTML and store it in MongoDB.  Unfortunately, the parsing code has been lost, but the MongoDB dumps from tha code are in the project [/mongo-backup/dump/legal_text/].

## Attribution
* Fonts are hosted by Google Fonts: 
   * Libre Baskerville and Merriweather. These are serif fonts mainly intended to display legal text.
   * Inter.  This is a san-serif font mainly for settings.
   * These fonts are licensed under the SIL Open Font License (OFL)
* Graphics
   * Favicon - [Book icons created by Freepik - Flaticon](https://www.flaticon.com/free-icon/open-book_167755), this is free to use with attribution.
      * Used https://www.favicon-generator.org/ to generate favicons for multiple platforms.
   * link icon - [Chain icons created by Freepik - Flaticon](https://www.flaticon.com/premium-icon/link_530742)
