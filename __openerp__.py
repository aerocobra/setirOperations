# -*- coding: utf-8 -*-
# © 2017 Igor V. Kartashov
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": 'SETIR Operation',
    "version": "9.0.1.0",
    "summary": "módulo operaciones para SETIR",
    "description": """
            		i-vk
            		v9.0.1.0
            		Operaciones para SETIR
                	""",
    "author": "Igor V. Kartashov",
    "license": "AGPL-3",
    "website": "http://crm.setir.es",
    "category": "Operations",
    "depends": [
				'base',
				'crm',
				'sale',
				'website_quote',
                'mail',
				],
    "data": [
		"views/setirOperations.xml",
        "views/setirOperationForm.xml",
        "data/data.xml",
        "security/ir.model.access.csv",
        ],
    "installable": True,
    "application": True,
	"auto_install": False,
    "price": 0.00,
    "currency": "EUR"
}