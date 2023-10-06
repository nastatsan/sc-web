const scHelper = null;
const scKeynodes = null;
const currentYear = new Date().getFullYear();

const SCgEditMode = {
    SCgModeSelect: 0,
    SCgModeEdge: 1,
    SCgModeBus: 2,
    SCgModeContour: 3,
    SCgModeLink: 4,
    SCgViewOnly: 5,

    /**
     * Check if specified mode is valid
     */
    isValid: function (mode) {
        return (mode >= this.SCgModeSelect) && (mode <= this.SCgViewOnly);
    }
};

const SCgViewMode = {
    DefaultSCgView: 0,
    DistanceBasedSCgView: 1,

    /**
     * Check if specified mode is valid
     */
    isValid: function (mode) {
        return (mode >= this.DefaultSCgView) && (mode <= this.DistanceBasedSCgView);
    }
};

// backward compatibility [scg_just_view <- scg_view_only]
const editModes = {
    'scg_just_view': SCgEditMode.SCgViewOnly,
    'scg_view_only': SCgEditMode.SCgViewOnly,
};

const viewModes = {
    'default_scg_view': SCgViewMode.DefaultSCgView,
    'distance_based_scg_view': SCgViewMode.DistanceBasedSCgView,
};

const ScModes = {
    'scg': 'format_scg_json',
    'scn': 'format_scn_json',
};

function ScClientCreate() {
    let res, rej;
    let scClient = new sc.ScClient(serverHost);
    return new Promise((resolve, reject) => {
        res = resolve(scClient);
        rej = reject;
    });
}

SCWeb.core.Main = {
    editMode: 0,
    viewMode: 0,
    window_types: [],
    idtf_modes: [],
    menu_commands: {},
    default_cmd_str: "ui_menu_view_full_semantic_neighborhood",

    /**
     * Initialize sc-web core and ui
     * @param {Object} params Initialization parameters.
     * There are required parameters:
     * - menu_container_id - id of dom element, that will contain menu items
     */
    init: function (params) {
        return new Promise((resolve) => {
            const self = this;
            SCWeb.core.Server._initialize();
            ScClientCreate().then(function (client) {
                window.scClient = client;
                window.scHelper = new ScHelper(window.scClient);
                window.scKeynodes = new ScKeynodes(window.scHelper);

                window.scKeynodes.init().then(function () {
                    window.scHelper.init().then(function () {
                        SCWeb.ui.TaskPanel.init().then(function () {
                            SCWeb.core.Server.init(function (data) {
                                self.parseUrl(data, params).then(resolve);
                            });
                        });
                    });
                });
            });
        })
    },

    parseUrl: async function (data, params) {
        const url = parseURL(window.location.href);

        url.searchObject.view_mode = viewModes[url.searchObject.view_mode] ?? SCgViewMode.DefaultSCgView;

        // backward compatibility [mode <- edit_mode]
        url.searchObject.edit_mode = url.searchObject.edit_mode ? url.searchObject.edit_mode : url.searchObject.mode;
        url.searchObject.edit_mode = editModes[url.searchObject.edit_mode] ?? SCgEditMode.SCgModeSelect;

        this.menu_commands = data.menu_commands;
        this.user = data.user;
        data.menu_container_id = params.menu_container_id;

        SCWeb.core.Translation.fireLanguageChanged(this.user.current_lang);

        if (!url.searchObject || !SCWeb.core.Main.pageShowedForUrlParameters(url.searchObject)) {
            SCWeb.core.Main.showDefaultPage(params).then(null);
        }

        await Promise.all([SCWeb.ui.Core.init(data),
            SCWeb.core.ComponentManager.init(),
            SCWeb.core.Translation.update()
        ]);
        const addrs = await SCWeb.core.Server.resolveScAddr(["format_scg_json", "lang_en"]);

        const renderScg = (question, lang = addrs["lang_en"]) => {
            SCWeb.core.Translation.setLanguage(lang);
            $('#create-fragment-input').val('');
            const commandState = new SCWeb.core.CommandState(undefined, undefined, addrs["format_scg_json"], lang);
            SCWeb.ui.WindowManager.activateWindow(question, commandState);
        }
        window.renderScg = renderScg;
        window.onInitializationFinished?.();

    },

    pageShowedForUrlParameters(urlObject) {
        return SCWeb.core.Main.questionParameterProcessed(urlObject)
            || SCWeb.core.Main.systemIdentifierParameterProcessed(urlObject)
            || SCWeb.core.Main.commandParameterProcessed(urlObject);
    },

    questionParameterProcessed(urlObject) {
        const question = urlObject['question'];
        if (question) {
            /// @todo Check question is really a question
            const commandState = new SCWeb.core.CommandState(question, null, null);
            SCWeb.ui.WindowManager.appendHistoryItem(question, commandState);
            return true;
        }
        return false;
    },

    systemIdentifierParameterProcessed(urlObject) {
        // const lang = urlObject['lang'];
        // const window_lang = window.scKeynodes[lang];
        // if (window_lang) SCWeb.core.Translation.fireLanguageChanged(window_lang);

        // const sysId = urlObject['sys_id'];
        // if (!sysId) return false;
        // //SCWeb.core.Main.doDefaultCommandWithSystemIdentifier(sysId);

        // const fmt = ScModes[urlObject['format']];
        // const self = this;
        // SCWeb.core.Server.resolveScAddr([sysId, fmt, self.default_cmd_str]).then(function (result) {
        //     const sys_id_addr = result[sysId];
        //     const fmt_addr = result[fmt];
        //     self.default_cmd = result[self.default_cmd_str];
        //     self.doCommandWithFormat(self.default_cmd, [sys_id_addr], fmt_addr);
        //     //await SCWeb.core.Main.doDefaultCommandWithFormat([sys_id_addr], fmt_addr);
        // });

        // const viewMode = Number(urlObject['view_mode']);
        // const editMode = Number(urlObject['edit_mode']);

        // SCWeb.core.Main.viewMode = viewMode ?? 0;
        // SCWeb.core.Main.editMode = editMode ?? 0;

        // // backward compatibility [scg_structure_view_only <- full_screen_scg]
        // const fullScreenView = urlObject['full_screen_scg']
        //     ? urlObject['full_screen_scg']
        //     : urlObject['scg_structure_view_only'];
        // const hideTools = urlObject['hide_tools'];
        // const hideBorders = urlObject['hide_borders'];

        // if (fullScreenView) {
        //     this.initFullScreenView(hideTools, hideBorders);
        // }
        // return true;
        const sys_id = urlObject['sys_id'];
        if (sys_id) {
            SCWeb.core.Main.doDefaultCommandWithSystemIdentifier(sys_id);
            window.history.replaceState(null, null, window.location.pathname);
            return true;
        }
    },

    initFullScreenView(hideTools, hideBorders) {
        $('#window-header-tools').hide();
        $('#static-window-container').hide();
        $('#header').hide();
        $('#footer').hide();
        $('#window-container').css({ 'padding-right': '', 'padding-left': '' });

        this.waitForElm('.sc-contour').then(() => {
            $('#window-container').children().children().children().children().hide();
            $('.sc-contour').css({ 'height': '100%', 'width': '100%', 'position': 'absolute',
                "background-color": "none", "border": "0", "padding": "0px", "border-radius": "0px" });
            $('.scs-scn-view-toogle-button').hide().click();
            $('.sc-window').css({ "padding": "0px", "overflow": "hidden" });
            $('.panel-body').css({ "padding": "0px", "overflow": "hidden" });
            $('.scs-scn-element').css("cursor", "auto !important");
            $("[id*='tools-']").parent().css({ "height": "100%", "width": "100%" });
            $("[id*='tools-']").parent().parent().css("height", "100%");

            if (hideBorders) {
                $('.sc-contour').css({ 'border': 'none' });
                $('.panel-default').css({ 'border-color': '#FFFFFF' });
                $('.main-container').css({ 'padding-left': '0', 'padding-right': '0' });
            }
        });

        this.waitForElm('.scg-tools-panel').then(() => {
            if (hideTools) {
                $('.scg-tools-panel').css({ 'display': 'block' });
            }
        });
    },

    waitForElm(selector) {
        return new Promise(resolve => {
            if (document.querySelector(selector)) {
                return resolve(document.querySelector(selector));
            }

            const observer = new MutationObserver(() => {
                if (document.querySelector(selector)) {
                    resolve(document.querySelector(selector));
                    observer.disconnect();
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    },

    commandParameterProcessed(urlObject) {
        const command_identifier = urlObject['command_id'];
        if (command_identifier) {
            const parameters = Object.keys(urlObject);
            const args = [];
            for (let param of parameters) {
                if (/^arg/gi.test(param)) {
                    args.push(urlObject[param]);
                }
            }
            SCWeb.core.Main.doCommandByIdentifier(command_identifier, args);
            return true;
        }
        return false;
    },

    showDefaultPage: async function (params) {
        function start(a) {
            SCWeb.core.Main.doDefaultCommand([a]);
            if (params.first_time)
                $('#help-modal').modal({ "keyboard": true });
        }

        let argumentAddr = window.scKeynodes['ui_start_sc_element'];
        const last_page_cmd_args = [getCookie('last_page_cmd_args')]
        let first_last_page_cmd_arg = last_page_cmd_args[0];
        if (first_last_page_cmd_arg) {
            first_last_page_cmd_arg = parseInt(first_last_page_cmd_arg);
            if ((await window.scClient.checkElements([new sc.ScAddr(first_last_page_cmd_arg)]))[0]) {
                argumentAddr = first_last_page_cmd_arg;
            }
        }

        start(argumentAddr);

        $('.copyright').text(`Copyright © 2012 - ${currentYear} OSTIS`);
    },

    /**
     * Returns sc-addr of preferred output language for current user
     */
    getDefaultExternalLang: function () {
        return this.user.default_ext_lang;
    },

    /**
     * Initiate user interface command
     * @param {String} cmd_addr sc-addr of user command
     * @param {Array} cmd_args Array of sc-addrs with command arguments
     */
    doCommand: function (cmd_addr, cmd_args) {
        SCWeb.core.Arguments.clear();
        SCWeb.core.Server.doCommand(cmd_addr, cmd_args, function (result) {
            if (result.question !== undefined) {
                const commandState = new SCWeb.core.CommandState(cmd_addr, cmd_args);
                SCWeb.ui.WindowManager.appendHistoryItem(result.question, commandState);
                setCookie('last_page_cmd_args', cmd_args);
            } else if (result.command !== undefined) {
            } else {
                alert("There are no any answer. Try another request");
            }
        });
    },

    /**
     * Initiate user interface command
     * @param {String} cmd_identifier system identifier of user command
     * @param {Array} cmd_args system identifiers of command arguments
     */
    doCommandByIdentifier: function (cmd_identifier, cmd_args) {
        const self = this;
        SCWeb.core.Arguments.clear();
        SCWeb.core.Server.resolveScAddr([cmd_identifier].concat(cmd_args)).then(function (result) {
            const cmd_addr = result[cmd_identifier];
            const resolved_args = [];
            cmd_args.forEach(function (argument) {
                resolved_args.push(result[argument]);
            })
            self.doCommand(cmd_addr, resolved_args);
        })
    },

    doCommandWithPromise: function (command_state) {
        return new Promise(function (resolve, reject) {
            SCWeb.core.Server.doCommand(command_state.command_addr, command_state.command_args, function (result) {
                if (result.question !== undefined) {
                    resolve(result.question)
                } else if (result.command !== undefined) {

                } else {
                    reject("There are no any answer. Try another request");
                }
            })
        });
    },

    getTranslatedAnswer: function (command_state) {
        return new Promise(function (resolve) {
            SCWeb.core.Main.doCommandWithPromise(command_state).then(function (question_addr) {
                SCWeb.core.Server.getAnswerTranslated(question_addr, command_state.format, command_state.lang, function (answer) {
                    resolve(answer.link);
                })
            })
        })
    },

    /**
     * Initiate user natural language command
     * @param {String} query Natural language query
     */

    doTextCommand: function (query) {
        SCWeb.core.Server.textCommand(query, function (result) {
            if (result.question !== undefined) {
                const commandState = new SCWeb.core.CommandState(null, null, null);
                SCWeb.ui.WindowManager.appendHistoryItem(result.question, commandState);
            } else if (result.command !== undefined) {

            } else {
                alert("There are no any answer. Try another request");
            }
        });
    },

    /**
     * Initiate default user interface command
     * @param {Array} cmd_args Array of sc-addrs with command arguments
     */
    doDefaultCommand: function (cmd_args) {
        if (!this.default_cmd) {
            const self = this;
            SCWeb.core.Server.resolveScAddr([this.default_cmd_str]).then(function (addrs) {
                self.default_cmd = addrs[self.default_cmd_str];
                if (self.default_cmd) {
                    self.doCommand(self.default_cmd, cmd_args);
                }
            });
        } else {
            this.doCommand(this.default_cmd, cmd_args);
        }
    },

    /**
     * Initiate default user interface command
     * @param {string} sys_id System identifier
     */
    doDefaultCommandWithSystemIdentifier: function (sys_id) {

        const fmt_addr = 'format_scg_json';
        SCWeb.core.Server.resolveScAddr([sys_id, fmt_addr]).then(function (addrs) {
            const resolvedId = addrs[sys_id];
            const resolvedFmtId = addrs[fmt_addr];
            if (resolvedId) {
                SCWeb.core.Main.doDefaultCommandWithFormat([resolvedId], resolvedFmtId);
            } else {
                SCWeb.core.Main.doDefaultCommandWithSystemIdentifier('ui_start_sc_element');
            }
        });
        // SCWeb.core.Server.resolveScAddr([sys_id]).then(function (addrs) {
        //     const resolvedId = addrs[sys_id];
        //     if (resolvedId) {
        //         SCWeb.core.Main.doDefaultCommand([resolvedId]);
        //     } else {
        //         SCWeb.core.Main.doDefaultCommandWithSystemIdentifier('ui_start_sc_element');
        //     }
        // });
    },

    /**
    * Initiate user interface command
    * @param {String} cmd_addr sc-addr of user command
    * @param {Array} cmd_args Array of sc-addrs with command arguments
    */
    doCommandWithFormat: function (cmd_addr, cmd_args, fmt_addr) {
        SCWeb.core.Server.doCommand(cmd_addr, cmd_args, function (result) {
            if (result.question !== undefined) {
                const commandState = new SCWeb.core.CommandState(cmd_addr, cmd_args, fmt_addr);
                SCWeb.ui.WindowManager.appendHistoryItem(result.question, commandState);
            } else {
                alert("There are no any answer. Try another request");
            }
        });
    },

    /**
     * Initiate default user interface command
     * @param {Array} cmd_args Array of sc-addrs with command arguments
     */
    doDefaultCommandWithFormat: function (cmd_args, fmt_addr) {
        if (!this.default_cmd) {
            var self = this;
            SCWeb.core.Server.resolveScAddr([this.default_cmd_str], function (addrs) {
                self.default_cmd = addrs[self.default_cmd_str];
                if (self.default_cmd) {
                    self.doCommandWithFormat(self.default_cmd, cmd_args, fmt_addr);
                }
            });
        } else {
            this.doCommandWithFormat(this.default_cmd, cmd_args, fmt_addr);
        }
    }
};

