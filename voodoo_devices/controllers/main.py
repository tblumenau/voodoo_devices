from odoo import http
from odoo.http import request
import json

class ExternalRpcController(http.Controller):

    @http.route('/external_rpc/receive', type='json', auth='user')
    def receive_call_back(self, **kwargs):
        
        data = json.loads(request.httprequest.data)
        qty = data.get('qty')
        ack = data.get('acknack')
        nonce = data.get('nonce')
        
        move_id = json.loads(nonce).get('moveid')
           
        if ack and qty>0:
            # Retrieve the stock.move record
            move = request.env['stock.move'].browse(move_id)
            
            # Update the done quantity
            move.write({'quantity_done': qty})

            return {"status": "success", "message": "Quantity updated successfully"}
        else:
            return {"status": "success", "message": "Quantity not updated"}



# COOKIE_FILE=$(mktemp) && wget --save-cookies $COOKIE_FILE --post-data 'login=your_login&password=your_password' 
# --keep-session-cookies http://your-odoo-instance-url/web/session/authenticate && wget --load-cookies $COOKIE_FILE --post-data 
# '{"jsonrpc": "2.0", "method": "call", "params": {"json_data": "{\"nonce\": \"{\\\"moveId\\\":1}\", \"qty\": 10}"} }' 
# --header='Content-Type: application/json' -O- http://your-odoo-instance-url/external_rpc/receive && rm $COOKIE_FILE