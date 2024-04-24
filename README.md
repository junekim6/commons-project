# Welcome to the Commons Project

This repository contains the code for the main analysis of comments posted on regulations.gov.

Commons is an AI-driven tool created to help journalists and researchers better understand public comments on Federal regulation posted on Regulations.gov. It is part of the magic grant project [Commons](https://brown.columbia.edu/portfolio/commons/) funded by the Brown Institute of Media Technology. 

The tool can be accessed at [https://www.commons-project.com/](https://www.commons-project.com/).

## 1. Project Description
In the United States, federal agencies have the power to create, amend, and repeal rules, ones that have an enormous impact over the lives of citizens. As part of that process, the broader public is able to comment on proposed regulations before they’re finalized.

These public comments are critical to policy-making. They provide regulators with vital information from stakeholders that can change how they frame a rule, and they allow a forum for the public to voice their views, providing one of the main democratic components of the rulemaking process. Most agencies post these comments for the public to view on a site called Regulations.gov. But with thousands of comments posted in a single docket, the flow of information can be overwhelming and difficult to interpret.

We created Commons to help unlock the wealth of information in comments received by regulators and strengthen public awareness about the rulemaking process.

## 2. Content of the repository
The repository contains the following folders:

- `data_collection`: A set of scripts to collect data from regulations.gov API. 
- `data_analysis`: A set of scripts to analyze the data collected from regulations.gov.
- `requirements.txt`: A list of required packages to run the code.
- `structure.txt`: A description of the structure of the repository.
- `.env`: A file to store the API keys and login credentials needed to run the entire code. You need to add your own API keys.

For a complete overview of the repository, please refer to the `structure.txt` file.

## 3. Installation and setup
To install the required packages, run the following command in the terminal:

```bash
pip install -r requirements.txt
```

## 4. Usage
To run the code, you need to have a valid API key from regulations.gov. You can request an API key [here]().


## x. Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## Authors and acknowledgment

This repository is maintained by [June Kim](https://github.com/junekim6) and [Laura Bejder Jensen](https://github.com/laurabejder). Nate Rosenfield and Jana Cholakovska are also part of the team.

This project is part of the [Commons](https://brown.columbia.edu/portfolio/commons/) project funded by the Brown Institute of Media Innovation. The project is a collaboration between the [Graduate School of Journalism](https://brown.columbia.edu/) at Columbia University and the [School of Engineering](https://brown.stanford.edu/) at Stanford University.