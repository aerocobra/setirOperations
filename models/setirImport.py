# -*- coding: utf-8 -*-
#setirOperation.py
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models, _
from openerp import tools
from pygments.lexer import _inherit
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import exceptions
from setirDefinitions import *


class setirImport ( models.Model):
	_name	= "setir.import"

	name		=	fields.Char			(	string		= u"Importación")

	binaryFile	=	fields.Binary		(	string		= "Arcvhivo a importar")
	strFile		=	fields.Char			(	string		= "Nomber del archivo")
	
	eImportType	=	fields.Selection	(	string		= u"Tipo importación",
											selection	= IMPORT_TYPE)

	
