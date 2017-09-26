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
	_name	= "setir.operation"

	name	= fields.Char ( string = "Operación")

class setirPMState ( models.Model):
	_name = "setir.pm.state"

	name            = fields.Char ( string = "Estado")
	strDescription  = fields.Char ( string = "Descripción")

class setirPMUnsubscribeReason ( models.Model):
	_name = "setir.pm.unsubscribe.reason"

	name            = fields.Char ( string = "Razón")

class setirPMBlockReason ( models.Model):
	_name = "setir.pm.block.reason"

	name            = fields.Char ( string = "Razón")

class setirPMStateHistory ( models.Model):
	_name = "setir.pm.state.history"
	
	idState	= fields.Many2one ( string			= "Estado",
								comodel_name	= "setir.pm.state")
	dtState	= fields.DateTime (	string	= "Fecha")	

class setirPMManagement ( models.Model):
	_name = "setir.pm.management"

	name    = fields.Char ( string = "Gestión")
	