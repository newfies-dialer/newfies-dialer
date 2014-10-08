from newfies_dialer import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.utils.importlib import import_module
import datetime


def init_session(session_key):
    """
    Initialize same session as done for ``SessionMiddleware``.
    """
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(session_key)


def main():
    """
    Read all available users and all available not expired sessions. Then
    logout from each session.
    """
    now = datetime.datetime.now()
    request = HttpRequest()
    sessions = Session.objects.filter(expire_date__gt=now)
    users = dict(User.objects.values_list('id', 'username'))

    print('Found %d not-expired session(s).' % len(sessions))

    for session in sessions:
        user_id = session.get_decoded().get('_auth_user_id')
        # username = session.get_decoded().get('_auth_user_id')
        request.session = init_session(session.session_key)
        logout(request)

        # print('    Successfully logout %r user.' % username)
        print('Successfully logout %s user.' % users[user_id])

if __name__ == '__main__':
    main()
