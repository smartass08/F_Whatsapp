 # Meetings Channel
 
 [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/ksdfg/Meetings-Channel/graphs/commit-activity)
![GitHub contributors](https://img.shields.io/github/contributors/ksdfg/Meetings-Channel)
![GitHub last commit](https://img.shields.io/github/last-commit/ksdfg/Meetings-Channel)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 
![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/ksdfg/Meetings-Channel) 
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed-raw/ksdfg/Meetings-Channel) 
[![GitHub](https://img.shields.io/github/license/ksdfg/meetings-channel)](https://github.com/ksdfg/meetings-channel/blob/master/LICENSE)
 
 A small project which sends links to telegram from whatsapp chats and email.
 
 #### Requirements:
  1) Docker and docker-compose
  2) Whatsapp account (duh?)
  3) Email account (duh?)
 
 #### Steps for running:
  1) Make a copy of `sample_config.ini` and name it `settings.ini` / Rename `sample_config.ini` to `config.ini`
  2) Fill the `settings.ini` file (DON'T  USE QUOTES OR DOUBLE QUOTATION MARKS, thx)
  4) `docker build -t meetings-channel:latest`
  3) `docker-compose up` 
  4) If running first time - Wait for the QR code to show up in the `qrs` directory (filename will be shown in output) and scan the QR code. (This only is required once and that is on first run)
  
 #### Limitations:
  1) Can't select individual chats, So it works globally. (My understanding of python is very low right now and I'm sorry for that)
  2) Needs docker to run because the wrapper library refuses to work properly without it.

 #### Filtering text
  1) You can set `Filter-Mode` to `blacklist` or `whitelist` if you want to not send messages with certain text in them, or only send messages which contain certain text.
  2) The default behaviour will just send all messages
  3) Depending on what you set `Filter-Mode` as, you should set `Blacklist` or `Whitelist` as a comma separated list of strings to be checked for

#### Please feel free to PR and help me improve this.
