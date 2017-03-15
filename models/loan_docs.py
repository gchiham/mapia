# -*- encoding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp import models, fields, api


class MapiaLoandocumento(models.Model):
    _name = "mapia.management.tipo.documento"

    name = fields.Char("Nombre de tipo de documento")
    prestamo_id = fields.Many2one("mapia.management.loan", "Prestamo")
    documento = fields.Binary('Documento Adjunto')
    estado = fields.Selection(
        [('ingresado', 'Ingresado'),('proceso', 'Proceso de validacion'),('validada', 'Validado')], string='Estado de documento', default='ingresado')
    nota = fields.Text("Nota")
