from odoo import models, fields, api,_,exceptions
from odoo.exceptions import UserError, AccessError, ValidationError



class Registration(models.Model):
    _name = 'registration.registration'
    _description = 'egistration.registration'
    _inherit = ['mail.thread']

    @api.multi
    def print_report(self):
        return self.env.ref('formation.report_registration').report_action(self)
    
    @api.one
    def action_new(self):
        self.state = 'new'
        return True
    
    @api.one
    def action_done(self):
        if self.student_id :           
            self.state = 'done'
        else : raise UserError(_('Veuillez spécifier un étudiant.'))
        return True   

    @api.one
    def action_cancel(self):
        if self.state == 'done':
            raise UserError(_('Vous ne pouvez pas annuler une inscription validée!'))
        return True   
    
        
    @api.model
    @api.depends('code')
    def create(self, vals):
        if ('code' not in vals) or (vals.get('code')=='/'):
            vals['code'] = self.env['ir.sequence'].get('registration.registration')
        return super(Registration, self).create(vals) 
    
    @api.multi
    def write(self, vals):
        if not self.student_id:       
            vals['name'] = self.code
        else:vals['name'] = self.code + self.student_id.name
        return super(Registration, self).write(vals)
    
    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'name': 'copy(name)','code': 'copy -001'})
        return super(Registration, self).copy(default)


    @api.multi
    def unlink(self):
        for record in self:
            if record.state in 'done,cancel':
                raise UserError(_('You cannot delete records in done state.'))
        res = super(Registration, self).unlink()
        return res

    @api.one
    @api.depends('claim_ids')
    def _compute_claims(self):
        self.nbr = len(self.claim_ids)

    @api.constrains('student_id')
    def _check_something(self):
        for record in self:
            if record.student_id.age > 20:
                raise ValidationError("Revoir l'age de l'étudiant: %s" % record.student_id.age)

    @api.onchange('service_id')
    def onchange_service_id(self):
        if self.service_id:
            self.fees = self.service_id.list_price or False                    
            
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', default='/', readonly=True)
    start_date = fields.Date('Date début',help="Date",track_visibility='onchange')
    end_date = fields.Date('Date fin',help="Date")
    description=fields.Text(string='description', required=False, readonly=False)
    cycle_id = fields.Many2one('cycle.cycle', string='Cycle', track_visibility='onchange') 
    year_id = fields.Many2one('year.year', string='Année univ', track_visibility='onchange')
    claim_ids = fields.One2many('claim.claim', 'reg_id', string='Reclamation')
    student_id = fields.Many2one('res.partner', string='Etudiant',domain="[('student_ok', '=',True)]", track_visibility='onchange')
    state=fields.Selection([('new', 'Nouveau'), ('done', 'Validé'), ('paid', 'Payé'), ('cancel', 'Annulé')], string= 'Status', default='new',track_visibility='onchange')
    fees = fields.Float('Frais d\'inscription')
    service_id = fields.Many2one('product.template','Service')
    nbr = fields.Integer(compute='_compute_claims', string='#reclamation')
    order_ok = fields.Boolean('Commande générée')

    @api.multi
    def action_gererate_order(self): 
        if self.student_id and self.service_id and self.order_ok==False:    
            sale_order_id = self.env['sale.order'].create({ 'origin':self.name or False,
                                                            'partner_id' : self.student_id and self.student_id.id or False,
                                                            })
                   
            sale_order_line={
                                'product_id' :self.service_id.id,
                                'name' : self.service_id.name,
                                'product_uom_qty' : 1,
                                'order_id' : sale_order_id.id,
                                }    
            self.env['sale.order.line'].create(sale_order_line)  
            self.order_ok = True
        else : raise exceptions.except_orm(u'Attention !!', u'Veuillez choisir un étudiant !')
        return True
    
    
class Claim(models.Model):
    _name = 'claim.claim'
    _description = 'Reclamation'
    
    
    @api.one
    @api.depends('amount','hours_nbr')
    def _total_compute(self):
        if self.hours_nbr:
            self.total = self.amount * self.hours_nbr
        else :
            self.sum = self.amount + self.amount
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', default=lambda x: x.env['ir.sequence'].get('claim.claim'))
    start_date = fields.Date('Date début',help="Date")
    end_date = fields.Date('Date fin',help="Date")
    description=fields.Text(string='description', required=False, readonly=False)
    reg_id = fields.Many2one('registration.registration', string='Inscription')
    user_id = fields.Many2one('res.users',string='Responsable')
    state=fields.Selection([('new', 'Nouvelle'), ('done', 'Validé'), ('cancel', 'Annulée')], string= 'Status')
    priority=fields.Selection([('1', 'base'), ('2', 'normal'), ('3', 'hight')], string= 'Priorité')
    
    amount = fields.Float(string='Montant')
    hours_nbr = fields.Integer(string='#heurs')
    sum = fields.Float(string='Somme')
    total = fields.Float(compute='_total_compute',string='Total')
    
 
 
 
    
class Year(models.Model):
    _name = 'year.year'
    _description = 'year.year'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    start_date = fields.Date('Date début',help="Date")
    end_date = fields.Date('Date fin',help="Date")
    description=fields.Text(string='description', required=False, readonly=False)
    session_ids = fields.One2many('session.session','year_id',string='Session')
    
    
class Session(models.Model):
    _name = 'session.session'
    _description = ''
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    start_date = fields.Date('Date début',help="Date")
    end_date = fields.Date('Date fin',help="Date")
    description=fields.Text(string='description', required=False, readonly=False)
    year_id = fields.Many2one('year.year', string='Année univ')
    

class Cycle(models.Model):
    _name = 'cycle.cycle'
    _description = 'cycle.cycle'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    description=fields.Text(string='description', required=False, readonly=False)
    filiers_ids = fields.One2many('filiere.filiere','cycle_id', string='Filière') 
 
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.name + ' -- ' + record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result   

class Filier(models.Model):
    _name = 'filiere.filiere'
    _description = 'la filière'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    description=fields.Text(string='description', required=False, readonly=False)
    level_ids = fields.One2many('level.level','filiere_id', string='Niveau')
    cycle_id =fields.Many2one('cycle.cycle', string='Cycle')
        
class Level(models.Model):
    _name = 'level.level'
    _description = 'level.level'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    description=fields.Text(string='description', required=False, readonly=False)
    section_ids = fields.One2many('section.section','level_id', string='Section') 
    filiere_id =fields.Many2one('filiere.filiere', string='Filière')
        
class Section(models.Model):
    _name = 'section.section'
    _description = 'section.section'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    description=fields.Text(string='description', required=False, readonly=False)
    module_ids = fields.One2many('module.module','section_id', string='Module') 
    level_id = fields.Many2one('level.level', string='Niveau')


class Module(models.Model):
    _name = 'module.module' 
    _description = 'modules' 
    
    name = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    section_id = fields.Many2one('section.section',string='Section')
 
class Partner(models.Model):
    _inherit = 'res.partner' 
    
    student_ok = fields.Boolean(string='Est un étudiant')
    birthday = fields.Date(string='Date de naissance')
    age = fields.Integer(string='Age')
    reg_ids = fields.One2many('registration.registration','student_id', string='Inscription')
    bulletin_ids = fields.One2many('bulletin.bulletin','student_id', string='Bulletin de notes')

            

class Professor(models.Model):
    _inherit = 'hr.employee' 
    
    age = fields.Integer(string='Age')
    cin = fields.Char(string='CIN')
    teacher_ok = fields.Boolean(string='Est un professeur')
    speciality_id = fields.Many2one('speciality.speciality',string='Spécialité')
 
 
class Speciality(models.Model):
    _name = 'speciality.speciality' 
    _description = 'spécialité'
    
    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')    
    
    
class Bulletin(models.Model):
    _name = 'bulletin.bulletin' 

    @api.depends('note_ids')
    def _compute_average(self):
        if self.note_ids:
            average = 0
            for module in self.note_ids:
                average = average + module.average   
            self.average = round(average/len(self.note_ids))
                
    name = fields.Char(string='Nom', readonly=True, default=lambda x: x.env['ir.sequence'].get('bulletin.bulletin'))
    year_id = fields.Many2one('year.year',string='Année')
    session_id = fields.Many2one('session.session',string='Session')
    student_id = fields.Many2one('res.partner',string='Etudiant')
    average = fields.Float(compute='_compute_average',string='Moyenne générale')
    note_ids = fields.One2many('line.bulletin','bulletin_id', string='Notes')
    user_id = fields.Many2one('res.users',string='Responsable') 

class LineBulletin(models.Model):
    _name = 'line.bulletin' 

    @api.constrains('note_1','note_2')
    def _check_notes(self):
        if self.note_1 > 20 or self.note_1 < 0:
            raise ValidationError("Note erronée: %s" % self.note_1)
        elif self.note_2 > 20 or self.note_2 < 0:
            raise ValidationError("Note erronée: %s" % self.note_2)

    @api.onchange('note_1','note_2')
    def _onchange_notes(self):
        if self.note_1 and self.note_2:
            self.average = (self.note_1 + self.note_2)/2
                            
    name = fields.Char(string='Nom',readonly=True, default=lambda x: x.env['ir.sequence'].get('line.bulletin'))
    teacher_id = fields.Many2one('hr.employee',string='Professeur')
    module_id = fields.Many2one('module.module',string='Module')
    note_1 = fields.Float(string='Note 1')
    note_2 = fields.Float(string='Note 2')
    average = fields.Float(string='Moyenne')
    bulletin_id = fields.Many2one('bulletin.bulletin', string='Bulletin') 
    
    
    
    