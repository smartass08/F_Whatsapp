 ## A noob script which sends links to telegram from whatsapp chats and email
 
 
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



#### Please feel free to PR and help me improve this.
