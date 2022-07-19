# -*- coding: utf-8 -*-
from typing import List

import tornado.web
import json

from sc_client import client
from sc_client.constants import sc_types
from sc_client.models import ScIdtfResolveParams, ScTemplate, ScAddr, ScConstruction
from sc_client.sc_keynodes import ScKeynodes

import decorators

from keynodes import KeynodeSysIdentifiers

from . import api_logic as logic
import time
from . import base


# -------------------------------------------


class ContextMenu(base.BaseHandler):
    # @tornado.web.asynchronous
    def get(self):
        keynodes = ScKeynodes()
        keynode_ui_main_menu = keynodes[KeynodeSysIdentifiers.ui_main_menu.value]

        # try to find main menu node
        cmds = []
        logic.find_atomic_commands(keynode_ui_main_menu, cmds)

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(cmds))


class CmdDo(base.BaseHandler):
    # @tornado.web.asynchronous
    def post(self):
        cmd_addr = ScAddr(int(self.get_argument(u'cmd', None)))
        # parse arguments
        first = True
        arg = ScAddr(0)
        arguments = []
        idx = 0
        while first or arg.is_valid():
            arg_hash = self.get_argument(u'%d_' % idx, None)
            if arg_hash is not None:
                arg = ScAddr(int(arg_hash))
                # check if sc-element exist
                if client.check_elements(arg)[0].is_valid():
                    arguments.append(arg)
                else:
                    return logic.serialize_error(404, "Invalid argument: %s" % arg)
            first = False
            idx += 1

        keys = ScKeynodes()
        result = logic.do_command(cmd_addr, arguments, self)
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(result))


class QuestionAnswerTranslate(base.BaseHandler):
    # @tornado.web.asynchronous
    def post(self):
        question_addr = ScAddr(int(self.get_argument(u'question', None)))
        format_addr = ScAddr(int(self.get_argument(u'format', None)))

        keynodes = ScKeynodes()
        keynode_system_element = keynodes[KeynodeSysIdentifiers.system_element.value]
        ui_rrel_source_sc_construction = keynodes[KeynodeSysIdentifiers.ui_rrel_source_sc_construction.value]
        ui_command_translate_from_sc = keynodes[KeynodeSysIdentifiers.ui_command_translate_from_sc.value]
        ui_command_initiated = keynodes[KeynodeSysIdentifiers.ui_command_initiated.value]

        # try to find answer for the question
        wait_time = 0
        wait_dt = 0.1

        answer = logic.find_answer(question_addr)
        while not answer:
            time.sleep(wait_dt)
            wait_time += wait_dt
            if wait_time > tornado.options.options.event_wait_timeout:
                return logic.serialize_error(self, 404, 'Timeout waiting for answer')

            answer = logic.find_answer(question_addr)

        if not answer:
            return logic.serialize_error(self, 404, 'Answer not found')

        answer_addr = answer[0].get(2)

        # try to find translation to specified format
        result_link_addr = logic.find_translation_with_format(answer_addr, format_addr)

        # if link addr not found, then run translation of answer to specified format
        if not result_link_addr.is_valid():
            construction = ScConstruction()
            construction.create_node(sc_types.NODE_CONST, 'trans_cmd_addr')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynode_system_element, 'trans_cmd_addr')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, 'trans_cmd_addr', answer_addr, 'arc_addr')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynode_system_element, 'arc_addr')
            construction.create_edge(
                sc_types.EDGE_ACCESS_CONST_POS_PERM, ui_rrel_source_sc_construction, 'arc_addr', 'arc_addr_2')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynode_system_element, 'arc_addr_2')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, 'trans_cmd_addr', format_addr, 'arc_addr_3')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynode_system_element, 'arc_addr_3')
            ui_rrel_output_format = keynodes[KeynodeSysIdentifiers.ui_rrel_output_format.value]
            construction.create_edge(
                sc_types.EDGE_ACCESS_CONST_POS_PERM, ui_rrel_output_format, 'arc_addr_3', 'arc_addr_4')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynode_system_element, 'arc_addr_4')
            construction.create_edge(
                sc_types.EDGE_ACCESS_CONST_POS_PERM, ui_command_translate_from_sc, 'trans_cmd_addr', 'arc_addr_5')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynode_system_element, 'arc_addr_5')
            construction.create_edge(
                sc_types.EDGE_ACCESS_CONST_POS_PERM, ui_command_initiated, 'trans_cmd_addr', 'arc_addr_6')
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynode_system_element, 'arc_addr_6')

            result = client.create_elements(construction)

            # now we need to wait translation result
            wait_time = 0
            translation = logic.find_translation_with_format(answer_addr, format_addr)
            while not translation.is_valid():
                time.sleep(wait_dt)
                wait_time += wait_dt
                if wait_time > tornado.options.options.event_wait_timeout:
                    return logic.serialize_error(self, 404, 'Timeout waiting for answer translation')

                translation = logic.find_translation_with_format(answer_addr, format_addr)

            if translation is not None:
                result_link_addr = translation

        # if result exists, then we need to return it content
        if result_link_addr is not None:
            result = json.dumps({"link": result_link_addr.value})

        self.set_header("Content-Type", "application/json")
        self.finish(result)


class LinkFormat(base.BaseHandler):

    # @tornado.web.asynchronous
    def post(self):

        # parse arguments
        first = True
        arg = ScAddr(0)
        arguments = []
        idx = 0
        while first or arg.is_valid():
            arg_str = u'%d_' % idx
            arg_hash = self.get_argument(arg_str, None)
            if arg_hash is not None:
                arg = ScAddr(int(arg_hash))
                arguments.append(arg)
            first = False
            idx += 1

        keys = ScKeynodes()
        keynode_nrel_format = keys[KeynodeSysIdentifiers.nrel_format.value]
        keynode_format_txt = keys[KeynodeSysIdentifiers.format_txt.value]

        result = {}
        for arg in arguments:

            # try to resolve format
            template = ScTemplate()
            template.triple_with_relation(
                arg,
                sc_types.EDGE_D_COMMON_VAR,
                sc_types.NODE_VAR,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                keynode_nrel_format
            )
            format_result = client.template_search(template)
            if format_result:
                result[arg.value] = format_result[0].get(2).value
            else:
                result[arg.value] = keynode_format_txt.value

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(result))


@decorators.class_logging
class Languages(base.BaseHandler):
    # @tornado.web.asynchronous
    def get(self):
        langs = logic.get_languages_list()

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(langs))


@decorators.class_logging
class LanguageSet(base.BaseHandler):
    # @tornado.web.asynchronous
    def post(self):
        lang_addr = ScAddr(int(self.get_argument(u'lang_addr', None)))

        keys = ScKeynodes()

        sc_session = logic.ScSession(self, keys)
        sc_session.set_current_lang_mode(lang_addr)

        self.finish()


class IdtfFind(base.BaseHandler):
    def initialize(self, sys, main, common):
        self.sys = sys
        self.main = main
        self.common = common

    @decorators.method_logging
    # @tornado.web.asynchronous
    def get(self):
        result = {'main': [], 'common': [], 'sys': []}

        # get arguments
        substr = self.get_argument('substr', None)

        def appendSorted(array, data):
            if data not in array:
                if len(array) > 0:
                    idx = 0
                    max_n = tornado.options.options.idtf_search_limit
                    inserted = False
                    for idx in range(len(array)):
                        if len(array[idx][1]) > len(data[1]):
                            array.insert(idx, data)
                            inserted = True
                            break
                        idx = idx + 1

                    if not inserted and len(array) < max_n:
                        array.append(data)

                    if len(array) > max_n:
                        array.pop()
                else:
                    array.append(data)

        for i in self.main:
            if substr in i[1]:
                appendSorted(result['main'], i)
        for i in self.common:
            if substr in i[1]:
                appendSorted(result['common'], i)
        for i in self.sys:
            if substr in i[1]:
                appendSorted(result['sys'], i)

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(result))


@decorators.class_logging
class IdtfResolve(base.BaseHandler):
    # @tornado.web.asynchronous
    def post(self):
        result = None

        # get arguments
        idx = 1
        arguments = []
        arg = ''
        while arg is not None:
            arg = self.get_argument(u'%d_' % idx, None)
            if arg is not None:
                arguments.append(arg)
            idx += 1

        sc_session = logic.ScSession(self)
        used_lang = sc_session.get_used_language()

        result = {}
        # get requested identifiers for arguments
        for addr_str in arguments:
            addr = int(addr_str)
            addr = ScAddr(addr)
            if not addr.is_valid():
                self.clear()
                self.set_status(404)
                self.finish('Can\'t parse sc-addr from argument: %s' % addr_str)

            found = False

            idtf_value = logic.get_identifier_translated(addr, used_lang)
            if idtf_value:
                result[addr_str] = idtf_value

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(result))


@decorators.class_logging
class AddrResolve(base.BaseHandler):
    # @tornado.web.asynchronous
    def post(self):

        # parse arguments
        first = True
        arg = None
        arguments = []
        idx = 0
        while first or (arg is not None):
            arg_str = u'%d_' % idx
            arg = self.get_argument(arg_str, None)
            if arg is not None:
                arguments.append(arg)
            first = False
            idx += 1

        res = {}
        resolve_keynodes_params = map(lambda x: ScIdtfResolveParams(idtf=x, type=None), arguments)
        addrs = client.resolve_keynodes(*resolve_keynodes_params)
        for i in range(len(addrs)):
            addr = addrs[i]
            if addr is not None:
                res[arguments[i]] = addr.value

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(res))


@decorators.class_logging
class InfoTooltip(base.BaseHandler):
    # @tornado.web.asynchronous
    def post(self):

        # parse arguments
        first = True
        arg = None
        arguments = []
        idx = 0
        while first or arg is not None:
            arg_str = u'%d_' % idx
            arg = self.get_argument(arg_str, None)
            if arg is not None:
                arguments.append(arg)
            first = False
            idx += 1

            sc_session = logic.ScSession(self)

            res = {}
            for addr in arguments:
                tooltip = logic.find_tooltip(ScAddr(int(addr)), sc_session.get_used_language())
                res[addr] = tooltip

            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps(res))


@decorators.class_logging
class User(base.BaseHandler):
    _keynodes = ScKeynodes()

    # @tornado.web.asynchronous
    def get(self):
        # get user sc-addr
        sc_session = logic.ScSession(self)
        user_addr = sc_session.get_sc_addr()

        if sc_session.email:
            is_authenticated = True
        else:
            is_authenticated = False

        roles = []

        if is_authenticated:
            user_kb_node = sc_session.get_user_kb_node_by_email()
            if user_kb_node.is_valid():
                roles = self.get_user_roles(user_kb_node)

        result = {
            'sc_addr': user_addr.value,
            'is_authenticated': is_authenticated,
            'current_lang': sc_session.get_used_language().value,
            'default_ext_lang': sc_session.get_default_ext_lang().value,
            'email': sc_session.email,
            'roles': roles
        }

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(result))

    def get_user_roles(self, user_kb_node: ScAddr) -> List[str]:
        roles = [KeynodeSysIdentifiers.nrel_authorised_user.value]

        manager_template = ScTemplate()
        manager_template.triple_with_relation(
            sc_types.NODE_VAR,
            sc_types.EDGE_D_COMMON_VAR,
            user_kb_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            self._keynodes[KeynodeSysIdentifiers.nrel_manager.value]
        )
        is_manager_role_exist = bool(client.template_search(manager_template))

        admin_template = ScTemplate()
        admin_template.triple_with_relation(
            sc_types.NODE_VAR,
            sc_types.EDGE_D_COMMON_VAR,
            user_kb_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            self._keynodes[KeynodeSysIdentifiers.nrel_administrator.value]
        )
        is_admin_role_exist = bool(client.template_search(manager_template))

        expert_template = ScTemplate()
        expert_template.triple_with_relation(
            sc_types.NODE_VAR,
            sc_types.EDGE_D_COMMON_VAR,
            user_kb_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            self._keynodes[KeynodeSysIdentifiers.nrel_expert.value]
        )
        is_expert_role_exist = bool(client.template_search(expert_template))

        if is_admin_role_exist:
            roles.append(KeynodeSysIdentifiers.nrel_administrator.value)
        if is_manager_role_exist:
            roles.append(KeynodeSysIdentifiers.nrel_manager.value)
        if is_expert_role_exist:
            roles.append(KeynodeSysIdentifiers.nrel_expert.value)

        return roles
