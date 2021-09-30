# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import Warning
from odoo import models, fields, api, _
import tempfile
import binascii
import xlrd
import urllib.request
import urllib3
import logging
import certifi

_logger = logging.getLogger(__name__)
# try:
#     import xlwt
# except ImportError:
#     _logger.debug('Cannot `import xlwt`.')
# try:
#     import cStringIO
# except ImportError:
#     _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class bi_import_product_image(models.Model):
    _name = "bi.import.product.image"
    _description = "Bi Import Product Image"

    model = fields.Selection([('template', 'Product Template'), ('product', 'Product')], string='Models', required=True)
    operation = fields.Selection([('create', 'Create Product'), ('update', 'Update Product')], string='Operations',
                                 required=True)
    file = fields.Binary('Select Excel File', required=True)
    update_by = fields.Selection([('id', 'ID'), ('name', 'Name'), ('code', 'Code')], string='Update By', default='name')

    def import_image(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        values = {}

        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        for row_no in range(sheet.nrows):
            val = {}
            if row_no <= 0:
                fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(
                    map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                        sheet.row(row_no)))

                if self.operation == 'update' and self.update_by == 'id':

                    if not line[0]:
                        _logger.error(_(' ID does not found in Excel'))
                    res = line[0].replace('.', '', 1).isdigit()
                    if not res:
                        _logger.error(_('Please provide correct Excel File With ID !'))
                    values.update({'id': int(float(line[0])),

                                   'image_1920': line[1],

                                   })
                    if values.get('image_1920') != '':
                        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
                        if "http://" in values.get('image_1920') or "https://" in values.get('image_1920'):
                            try:
                                img_url = values.get('image_1920')
                                img_link = http.request('GET', img_url)
                                thumbnail = base64.b64encode(img_link.data)
                                f = thumbnail
                            except:
                                _logger.error(_('Please provide correct URL for image !'))
                        else:
                            try:
                                with open(values.get('image_1920'), 'rb') as f:
                                    img = base64.b64encode(f.read())
                                    f = img
                            except IOError:
                                _logger.error(_('Could not find the image please make sure it is accessible !'+values.get('image_1920')))
                    else:
                        f = False

                elif self.operation == 'update' and self.update_by == 'name':

                    if not line[0]:
                        _logger.error(_(' Name does not found in Excel'))
                    values.update({
                        'name': line[0],

                        'image_1920': line[1],

                    })
                    if values.get('image_1920') != '':
                        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
                        if "http://" in values.get('image_1920') or "https://" in values.get('image_1920'):
                            try:
                                img_url = values.get('image_1920')
                                img_link = http.request('GET', img_url)
                                thumbnail = base64.b64encode(img_link.data)
                                f = thumbnail
                            except:
                                _logger.error(_('Please provide correct URL for image !'))
                        else:
                            try:
                                with open(values.get('image_1920'), 'rb') as f:
                                    img = base64.b64encode(f.read())
                                    f = img
                            except IOError:
                                _logger.error(_('Could not find the image please make sure it is accessible !')+values.get('image_1920'))
                    else:
                        f = False
                elif self.operation == 'update' and self.update_by == 'code':



                    if not line[0]:
                        _logger.error(_(' Code does not found in Excel'))
                    values.update({

                        'code': line[0],
                        'image_1920': line[1],

                    })
                    if values.get('image_1920') != '':
                        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
                        if "http://" in values.get('image_1920') or "https://" in values.get('image_1920'):
                            try:
                                img_url = values.get('image_1920')
                                img_link = http.request('GET', img_url)
                                thumbnail = base64.b64encode(img_link.data)
                                f = thumbnail
                            except:
                                _logger.error(_('Please provide correct URL for image !'))
                        else:
                            try:
                                with open(values.get('image_1920'), 'rb') as f:
                                    img = base64.b64encode(f.read())
                                    f = img
                            except IOError:
                                _logger.error(_('Could not find the image please make sure it is accessible !')+values.get('image_1920'))
                    else:
                        f = False

                elif self.operation == 'create':
                    if not line[0]:
                        _logger.error(_(' Name not found in Excel'))
                    values.update({
                        'code': line[1],
                        'name': line[0],
                        'image_1920': line[2],
                        'image_128': line[2],

                    })
                    if values.get('image_1920') != '':
                        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
                        if "http://" in values.get('image_1920') or "https://" in values.get('image_1920'):
                            try:
                                img_url = values.get('image_1920')
                                img_link = http.request('GET', img_url)
                                thumbnail = base64.b64encode(img_link.data)
                                f = thumbnail
                            except:
                                _logger.error(_('Please provide correct URL for image !'))
                        else:
                            try:
                                with open(values.get('image_1920'), 'rb') as f:
                                    img = base64.b64encode(f.read())
                                    f = img
                            except IOError:
                                _logger.error(_('Could not find the image please make sure it is accessible !')+values.get('image_1920'))
                    else:
                        f = False

                if self.model == 'template':
                    model = self.env['product.template']
                else:
                    model = self.env['product.product']

                if self.operation == 'create':

                    model.create({
                        'name': values.get('name'),
                        'default_code': values.get('code'),
                        'image_1920': f
                    })
                else:
                    if self.update_by == 'id':
                        if not values.get('id'):
                            _logger.error(_('ID does not found in Excel'))
                        else:
                            prod_search = model.search([('id', '=', values.get('id'))])
                    elif self.update_by == 'name':
                        if not values.get('name'):
                            _logger.error(_('Name does not found in Excel'))
                        else:
                            prod_search = model.search([('name', '=', values.get('name'))])
                    elif self.update_by == 'code':
                        if not values.get('code'):
                            _logger.error(_('Code("Internal Reference  ") does not found in Excel'))
                        else:
                            prod_search = model.search([('default_code', '=', values.get('code'))])

                    if prod_search:
                        prod_search.write({'image_128': f,'image_1920':f,})
                        _logger.error('Importado !'+str(row_no))




        return True
