# -*- encoding: utf-8 -*-
##############################################################################

{
    "name": "Mapia Loan",
    "version": "1.0",
    "depends": [
    "base",
        "account",
		"product",
		"hr"
    ],
    "author": "Cesar Alejandro Rodriguez",
    "category": "Sale",
    "description": """Loan Management """,
    'data': [
		"views/loan_management_menu.xml",
		"views/loan_type_view.xml",
		"views/loan_plazo_view.xml",
		"views/loan_interes_view.xml",
		"views/loan_view .xml",
		"views/loan_cuota_view.xml",
		"views/loan_docs_view.xml",
		"views/contracto_sale_sequence.xml",
		"views/cliente_view.xml",
    ],
    #'update_xml' : [
     #       'security/groups.xml',
      #      'security/ir.model.access.csv'
    #],
    'demo': [],
    'installable': True,
}
