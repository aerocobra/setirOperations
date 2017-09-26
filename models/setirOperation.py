# -*- coding: utf-8 -*-
#setirOperation.py
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models
from openerp import tools
from pygments.lexer import _inherit
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import exceptions

class setirOperation ( models.Model):
    _name = "setir.operation"

    x_strName   = fields.Char ( string = "Operaci�n")
