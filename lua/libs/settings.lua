
--
-- Database connection settings
--
DBHOST = '127.0.0.1'
DBNAME = 'newfiesdb'
DBUSER = 'newfiesuser'
DBPASS = 'password'
DBPORT = 5432

--
-- Select the TTS engine, value : flite, acapela
--
TTS_ENGINE = 'flite'

--
-- Acapela TTS Settings
--
ACCOUNT_LOGIN = 'EVAL_VAAS'
APPLICATION_LOGIN = 'EVAL_YYYYYYY'
APPLICATION_PASSWORD = 'XXXXXXXX'

SERVICE_URL = 'http://vaas.acapela-group.com/Services/Synthesizer'
QUALITY = '22k'  -- 22k, 8k, 8ka, 8kmu
ACAPELA_GENDER = 'W'
ACAPELA_INTONATION = 'NORMAL'
ACAPELA_LANG = 'EN'
