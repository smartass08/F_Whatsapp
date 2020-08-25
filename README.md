 ## A noob script which sends google meet links to telegram from whatsapp chats
 
 
 #### Requirements:
  1) Docker and docker-compose
  2) Whatsapp account (duh?)
 
 #### Steps for running:
  1) Fill the config.ini file (DON'T  USE QUOTES OR DOUBLE QUOTATION MARKS, thx)
  2) `Docker-compose run` 
  3) If running first time - Use any VNC viewer to connect into `localhost:5900` (password is `secret`) and scan the QR code. (This only is required once and that is on first run)
  
 #### Limitations:
  1) Can't select individual chats, So it works globally. (My understanding of python is very low right now and I'm sorry for that)
  2) Needs docker to run because the wrapper library refuses to work properly without it.



#### Please feel free to PR and help me improve this.
