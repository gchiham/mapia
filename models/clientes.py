# -*- encoding: utf-8 -*-
from odoo import models, fields, api

class Clientes(models.Model):
    _inherit = "res.partner"

    contrato_ids = fields.One2many("mapia.management.loan", "afiliado_id", "Financiamientos")
    x_iden = fields.Char("Identidad")
    rtn = fields.Char("RTN")
