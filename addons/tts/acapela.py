# -*- coding: utf-8 -*-
import sys
import hashlib

if sys.version_info < (3,0):
    import urllib as request
    parse = request
    import urllib2
    for method in dir(urllib2):
        setattr(request, method, getattr(urllib2, method))
    import cookielib as cookiejar
    
else:
    from http import cookiejar
    from urllib import parse, request


ACCOUNT_LOGIN = 'EVAL_XXXX'
APPLICATION_LOGIN = 'EVAL_XXXXXXX'
APPLICATION_PASSWORD = 'XXXXXXXX'

SERVICE_URL = 'http://vaas.acapela-group.com/Services/Synthesizer'
QUALITY = '22k' # 22k, 8k, 8ka, 8kmu
TTS_ENGINE = 'ACAPELA'


class Acapela(object):
    #Available voices list
    #http://www.acapela-vaas.com/ReleasedDocumentation/voices_list.php
    langs  = {
        'ES': {
            'W': {
                'NORMAL': 'ines',
            },
            'M': {
                'NORMAL': 'antonio',
            }
        },
        'BR': {
            'W': {
                'NORMAL': 'marcia',
            },
        },
        'EN': {
            'W': {
                'NORMAL': 'lucy',
            },
            'M': {
                'NORMAL': 'graham',
            },
        },
        'US': {
            'W': {
                'NORMAL': 'laura',
            },
            'M': {
                'NORMAL': 'heather',
            },
        },
        'FR': {
            'W': {
                'NORMAL': 'alice',
            },
            'M': {
                'NORMAL': 'antoine',
            },
        },
    }
    data = {}
    filename = None
    
    def __init__(self, text, lang, gender, intonation):
        """construct Acapela TTS"""
        key =  TTS_ENGINE + '-' + hashlib.md5(text + lang + gender + intonation).hexdigest()
        self.data = {
            'cl_env': 'FLASH_AS_3.0',
            'req_snd_id': key,
            'cl_login': ACCOUNT_LOGIN,
            'cl_vers': '1-30',
            'req_err_as_id3': 'yes',
            'req_voice': self.langs[lang][gender][intonation] + QUALITY,
            'cl_app': APPLICATION_LOGIN,
            'prot_vers': '2',
            'cl_pwd': APPLICATION_PASSWORD,
            'req_asw_type': 'STREAM',
        }
        self.filename = "%s-%s.mp3" % (key, lang)
        self.data['req_text'] = '\\vct=100\\ \\spd=160\\ %s' % text
        
    def run(self):
        """run will call acapela API and and produce audio"""
        encdata = parse.urlencode(self.data)
        request.urlretrieve(SERVICE_URL, self.filename, data=encdata)
        return self.filename
        
        

if __name__ == "__main__":

    #General settings for test
    gender = 'W'
    intonation = 'NORMAL'
    
    #Spanish
    lang = 'ES'
    text = "Newfies-Dialer es una aplicación de transmisión de voz diseñado y construido para automatizar la entrega de las llamadas telefónicas interactivas a contactos, clientes y público en general."
    tts_acapela = Acapela(text, lang, gender, intonation)
    output_filename = tts_acapela.run()
    print "Recorded TTS to %s" % output_filename
    
    #Portuguese
    lang = 'BR'
    text = "Newfies-Dialer é um aplicativo de transmissão de voz projetada e construída para automatizar a entrega de telefonemas interativos para contatos, clientes e público em geral."
    tts_acapela = Acapela(text, lang, gender, intonation)
    output_filename = tts_acapela.run()
    print "Recorded TTS to %s" % output_filename
    
    #French
    lang = 'FR'
    text = "Newfies-Dialer est une application de diffusion vocale conçu et construit pour automatiser la livraison des appels téléphoniques interactifs à des contacts, des clients et le public en général."
    tts_acapela = Acapela(text, lang, gender, intonation)
    output_filename = tts_acapela.run()
    print "Recorded TTS to %s" % output_filename
    
    #English
    lang = 'EN'
    text = "Newfies-Dialer is a voice broadcast application designed and built to automate the delivery of interactive phone calls to contacts, clients and the general public."
    tts_acapela = Acapela(text, lang, gender, intonation)
    output_filename = tts_acapela.run()
    print "Recorded TTS to %s" % output_filename
    
    
