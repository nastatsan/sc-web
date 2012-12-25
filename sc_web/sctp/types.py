# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------------
This source file is part of OSTIS (Open Semantic Technology for Intelligent Systems)
For the latest info, see http://www.ostis.net

Copyright (c) 2012 OSTIS

OSTIS is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OSTIS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with OSTIS. If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
"""

# -----------------------------------------
class sctpCommandType:
    
    SCTP_CMD_UNKNOWN            = 0x00 # unkown command
    SCTP_CMD_CHECK_ELEMENT      = 0x01 # check if specified sc-element exist
    SCTP_CMD_GET_ELEMENT_TYPE   = 0x02 # return sc-element type
    SCTP_CMD_ERASE_ELEMENT      = 0x03 # erase specified sc-element
    SCTP_CMD_CREATE_NODE        = 0x04 # create new sc-node
    SCTP_CMD_CREATE_LINK        = 0x05 # create new sc-link
    SCTP_CMD_CREATE_ARC         = 0x06 # create new sc-arc
    SCTP_CMD_GET_ARC_BEGIN      = 0x07 # return begin element of sc-arc
    SCTP_CMD_GET_ARC_END        = 0x08 # return end element of sc-arc
    SCTP_CMD_GET_LINK_CONTENT   = 0x09 # return content of sc-link
    SCTP_CMD_FIND_LINKS         = 0x0A # return sc-links with specified content
    SCTP_CMD_ITERATE_ELEMENTS   = 0x0B # return base teamplate iteration result
    
    SCTP_CMD_FIND_ELEMENT_BY_SYSITDF = 0xa0 # return sc-element by it system identifier
    
    SCTP_CMD_SHUTDOWN           = 0xfe # disconnect client from server

class sctpResultCode:
    
    SCTP_RESULT_OK              = 0x00 #
    SCTP_RESULT_FAIL            = 0x01 #
    SCTP_RESULT_ERROR_NO_ELEMENT= 0x02 # sc-element wasn't founded
    
class sctpIteratorType:
    SCTP_ITERATOR_3F_A_A = 0
    SCTP_ITERATOR_3A_A_F = 1
    SCTP_ITERATOR_3F_A_F = 2
    SCTP_ITERATOR_5F_A_A_A_F = 3
    SCTP_ITERATOR_5_A_A_F_A_F = 4
    SCTP_ITERATOR_5_F_A_F_A_F = 5
    SCTP_ITERATOR_5_F_A_F_A_A = 6
    SCTP_ITERATOR_5_F_A_A_A_A = 7
    SCTP_ITERATOR_5_A_A_F_A_A = 8

class ScElementType:
    # sc-element types
    sc_type_node        =   0x1
    sc_type_link        =   0x2
    sc_type_edge_common =   0x4
    sc_type_arc_common  =   0x8
    sc_type_arc_access  =   0x10

    # sc-element constant
    sc_type_const       =   0x20
    sc_type_var         =   0x40

    # sc-element positivity
    sc_type_arc_pos     =   0x80
    sc_type_arc_neg     =   0x100
    sc_type_arc_fuz     =   0x200

    # sc-element premanently
    sc_type_arc_temp    =   0x400
    sc_type_arc_perm    =   0x800

    # struct node types
    sc_type_node_tuple  =   (0x80 | sc_type_node)
    sc_type_node_struct =   (0x100 | sc_type_node)
    sc_type_node_role   =   (0x200 | sc_type_node)
    sc_type_node_norole =   (0x400 | sc_type_node)
    sc_type_node_class  =   (0x800 | sc_type_node)
    sc_type_node_abstract   =   (0x1000 | sc_type_node)
    sc_type_node_material   =   (0x2000 | sc_type_node)

    sc_type_arc_pos_const_perm  =   (sc_type_arc_access | sc_type_const | sc_type_arc_pos | sc_type_arc_perm)

    # type mask
    sc_type_element_mask    =   (sc_type_node | sc_type_link | sc_type_edge_common | sc_type_arc_common | sc_type_arc_access)
    sc_type_constancy_mask  =   (sc_type_const | sc_type_var)
    sc_type_positivity_mask =   (sc_type_arc_pos | sc_type_arc_neg | sc_type_arc_fuz)
    sc_type_permanency_mask =   (sc_type_arc_perm | sc_type_arc_temp)
    sc_type_node_struct_mask=   (sc_type_node_tuple | sc_type_node_struct | sc_type_node_role | sc_type_node_norole | sc_type_node_class | sc_type_node_abstract | sc_type_node_material)
    sc_type_arc_mask        =   (sc_type_arc_access | sc_type_arc_common | sc_type_edge_common)


class ScAddr:
    
    def __init__(self, _seg, _offset):
        self.seg = _seg
        self.offset = _offset
        
    def __str__(self):
        return "sc-addr: %d, %d" % (self.seg, self.offset)
    
    def __eq__(self, other):
        return self.seg == other.seg and self.offset == other.offset