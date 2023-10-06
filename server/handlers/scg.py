# -*- coding: utf-8 -*-
import logging

import decorators
from . import base, api_logic as logic

logger = logging.getLogger()


@decorators.class_logging
class ScgHandler(base.BaseHandler):
    def initialize(self):
        self.public_url = self.application.settings.get('public_url')

    def get(self):
        session_key = self.get_secure_cookie("session_key")
        logger.info('self.request.cookies:', self.request.cookies )
        logger.info('session_key:', session_key)
        # if session_key is None:
        #     logger.warning('Session key is not valid')
        #     logger.info('Redirecting to /auth/login')
        #     self.redirect("/auth/login")
        # else:
        sc_session = logic.ScSession(self)
            # user_login = sc_session.get_user_login()
            # if user_login is not None and sc_session.is_session_key_valid():
            
            # logger.info('sc_session:', sc_session)

            # logger.info('self.public_url:', self.public_url)
            # if sc_session:
        self.render(
            "scg.html",
            has_entered=False,
            first_time=1,
            public_url=self.public_url,
        )
            # else:
            #     sc_session.logout_user()
            #     logger.info('Redirecting to /auth/login')
            #     self.redirect("/auth/login")
