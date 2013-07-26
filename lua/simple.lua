
-- answer the call
session:answer();

-- sleep a second
session:sleep(1000);

-- play a file (8s)
session:streamFile("/usr/local/freeswitch/sounds/en/us/callie/voicemail/8000/vm-tutorial_change_pin.wav");

-- play a file (8s)
session:streamFile("/usr/local/freeswitch/sounds/en/us/callie/voicemail/8000/vm-tutorial_change_pin.wav");

-- hangup
session:hangup();
