
--
-- Database connection settings
--
DBHOST = '127.0.0.1'
DBNAME = 'newfiesdb'
DBUSER = 'newfiesuser'
DBPASS = 'password'
DBPORT = 5432

--
-- Select the TTS engine, value : flite, acapela, msspeak
--
TTS_ENGINE = 'flite'

--
-- Acapela and MSSpeak TTS Settings
-- MSSpeak only needs APPLICATION_LOGIN(client_id)
-- and APPLICATION_PASSWORD(client_secret).
-- ACCOUNT_LOGIN is ignored for MSSpeak
--
ACCOUNT_LOGIN = 'EVAL_VAAS'
APPLICATION_LOGIN = 'EVAL_YYYYYYY'
APPLICATION_PASSWORD = 'XXXXXXXX'

--
-- For MSSpeak comment out Acapela SERVICE_URL
-- and uncomment other SERVICE_URL parameter
--
-- SERVICE_URL = 'http://api.microsofttranslator.com/V2/Http.svc/Speak'
SERVICE_URL = 'http://vaas.acapela-group.com/Services/Synthesizer'

--
-- Acapela Specific Settings
--
QUALITY = '22k'  -- 22k, 8k, 8ka, 8kmu
ACAPELA_GENDER = 'W'
ACAPELA_INTONATION = 'NORMAL'
ACAPELA_LANG = 'EN'

--
-- Microsoft Speak Specific Settings
--
MSSPEAK_LANGUAGE = 'EN'
