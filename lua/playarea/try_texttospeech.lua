--
-- run example texttospeech
--

package.path = package.path .. ";/usr/share/newfies-lua/?.lua";
package.path = package.path .. ";/usr/share/newfies-lua/libs/?.lua";


local LFS_Caching = require 'texttospeech'
local inspect = require "inspect"


local ROOT_DIR = '/usr/share/newfies-lua/'
local TTS_DIR = ROOT_DIR..'tts/'
text = "Let's see if this works for us. Give a try!"
output_file = tts(text, TTS_DIR)
print("output_file => "..tostring(output_file))

text = ""
output_file = tts(text, TTS_DIR)
print("output_file => "..tostring(output_file))

-- print("\n\nGet Lenght Audio")
-- res = audio_lenght('/usr/share/newfies/usermedia/recording/recording-103-35225576.wav')
-- print(res)
