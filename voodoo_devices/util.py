
import logging
import requests

from odoo import models, api, _

from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)


class VoodooUtility:


    @staticmethod
    def getArrow(location):
        if location.voodoo_device_orientation=='below':
            return 'top'
        elif location.voodoo_device_orientation=='above':
            return 'bottom'
        elif location.voodoo_device_orientation=='right':
            return 'left'
        elif location.voodoo_device_orientation=='left':
            return 'right'
        elif location.voodoo_device_orientation=='belowright':
            return 'topleft'
        elif location.voodoo_device_orientation=='belowleft':
            return 'topright'
        elif location.voodoo_device_orientation=='aboveright':
            return 'bottomleft'
        else: # location.voodoo_device_orientation=='aboveleft':
            return 'bottomright'
        
    @staticmethod
    def renew_credentials(selfy):
        _logger.info("Renewing Credentials")

        ICPSudo = selfy.env['ir.config_parameter'].sudo()

        endpoint_url=ICPSudo.get_param('voodoo.endpoint_url')
        username=ICPSudo.get_param('voodoo.username')
        password=ICPSudo.get_param('voodoo.password')

        if not endpoint_url.endswith('/'):
            endpoint_url = endpoint_url + '/'

        endpoint = endpoint_url+"user/login/"

        login_data = {"username": username, "password": password}
        
        client = requests.Session()
        response = client.post(endpoint, json=login_data)
        
        _logger.info("login response: "+str(response.status_code))

        z = response.json()
        token = z.get('token')
        session = response.cookies['sessionid']
        ICPSudo.set_param('voodoo.session', session or '')
        ICPSudo.set_param('voodoo.token', token or '')


        if response.status_code == 200:
            # _logger.info("session is "+session)
            # _logger.info("token is "+token)
            return (session,token)
        else:
            response.raise_for_status()
        
    

    @staticmethod
    def voodooDeviceCall(selfy,deviceID, data):
        _logger.info("Device Call")

        ICPSudo = selfy.env['ir.config_parameter'].sudo()


        endpoint_url=ICPSudo.get_param('voodoo.endpoint_url')
        session=ICPSudo.get_param('voodoo.session')
        token=ICPSudo.get_param('voodoo.token')

        if not endpoint_url.endswith('/'):
            endpoint_url = endpoint_url + '/'
        if not session or not token:
            (session,token) = VoodooUtility.renew_credentials(selfy)
        else:
            # _logger.info("Using session "+session)
            # _logger.info("Using token "+token)
            pass

        client = requests.Session()
            # Try making the POST request
        response = client.post(
            endpoint_url+"device/"+deviceID+"/", 
            json=data, 
            headers= {'referer': endpoint_url,'x-csrf-token': token,}, 
            cookies={'sessionid': session,'csrftoken':token}
        )
        _logger.info("first device post response: "+str(response.status_code))

        # Check if the request was unsuccessful due to authentication issues
        if response.status_code == 401:  # Assuming 401 is the status code for unauthorized
            # Attempt to renew credentials
            (session,token) = VoodooUtility.renew_credentials(selfy)
            # session=ICPSudo.get_param('voodoo.session')
            # token=ICPSudo.get_param('voodoo.token')

            response = client.post(
                endpoint_url+"device/"+deviceID+"/", 
                json=data, 
                headers= {'referer': endpoint_url,'x-csrf-token': token,}, 
                cookies={'sessionid': session,'csrftoken':token}
            )
            _logger.info("second device post response: "+str(response.status_code))

        # Check if the final request was successful

        response.raise_for_status()
        return
                    


    @staticmethod
    def redoStatics(selfy, device_ids):
        _logger.info("Redoing statics")

        for deviceid in device_ids:


            if not deviceid:
                continue

            _logger.info("redoing statics for: "+str(deviceid))

            data = {}
            matching_locations = selfy.env['stock.location'].search([('voodoo_device_id', '=', deviceid)])
            if len(matching_locations)==0:
                _logger.info("not in any location")
                data['statica'] = ''
                data['staticb'] = ''
                data['staticc'] = ''
                data['staticd'] = ''
                data['statice'] = ''
                data['locationoverride'] = 'Unassigned'
            elif len(matching_locations)>1:
                _logger.info("multiple locations")
                data['statica'] = 'Various'
                data['staticb'] = ''
                data['staticc'] = ''
                data['staticd'] = ''
                data['statice'] = ''
                data['locationoverride'] = 'Multiple locations'
            else:
                #it's a single location
                location  = matching_locations
                # Get all stock.quant records pointing to this location
                quants = selfy.env['stock.quant'].search([('location_id', '=', location.id)])

                # Initialize variables to store the product default_code, main variant identifier, and total quantity
                name = None
                total_quantity = 0

                # Iterate through the quants to analyze the product name and sum up the quantities
                for quant in quants:
                    if name is None:
                        name = quant.product_id.display_name

                    else:
                        
                        if name != quant.product_id.display_name:
                            name = None
                            break

                    # Add up the quantity of the current quant
                    total_quantity += quant.quantity



                lname = location.complete_name
                
                while len(lname) > 26:
                    # Find the index of the first '\' character
                    index = lname.find('/')
                    
                    # Check if '\' was found
                    if index != -1:
                        # Remove the first chunk including '\' from the original string
                        lname = lname[index + 1:]
                    else:
                        # No '\' found, break to avoid an infinite loop
                        break
                
                if len(lname)>0 and len(lname)<=26:
                    data['locationoverride'] = lname
                else:
                    data['locationoverride'] = 'Bad Location Name!'

                arrow = VoodooUtility.getArrow(location)  # note this is singular--> ie an object!
                data['arrow']=arrow

                if name and total_quantity>0:
                    _logger.info("one location and one inventory type")
                    if ' - ' in name:
                        statica, staticb = name.split(' - ', 1)
                        data['statica'] = statica
                        data['staticb'] = staticb
                    elif '] ' in name:
                        statica,staticb = name.split('] ',1)
                        data['statica'] = statica+']'
                        data['staticb'] = staticb
                    else:
                        data['statica'] = name
                        
                    if total_quantity % 1 == 0:
                        data['quantity']= int(total_quantity)
                    else:
                        data['staticc'] = 'Qty: '+ str(total_quantity)

                    
                else:
                    _logger.info("one location but multiple inventory types")

                    data['statica']=lname
                    data['staticb']='\\bc'+str(deviceid)
                

                


            try:
                VoodooUtility.voodooDeviceCall(selfy,deviceid,data)
            except Exception as e:
                _logger.error(f"VoodooDeviceCall exception: {str(e)}")



    @staticmethod
    def processMove(selfy,move):
        name = move.product_id.display_name

        # Check if the source location has a voodoo_device_id
        dev_id = move.location_id.voodoo_device_id
        if dev_id:
            arrow = VoodooUtility.getArrow(move.location_id)

            data = {}
            data['command']='flash'
            data['arrow']=arrow

            if selfy.env.user.voodoo_name and selfy.env.user.voodoo_name!='':
                data['line1'] = selfy.env.user.voodoo_name

            data['line2']="PICK"

            # if ' - ' in name:
            #     line1, line2 = name.split(' - ', 1)
            #     data['line3'] = line1
            #     data['line4'] = line2
            # else:
            #     data['line3'] = name
            data['line3'] = name

            if move.product_uom_qty % 1 == 0:
                data['quantity']= int(move.product_uom_qty)
            else:
                data['line4'] = 'Qty: '+ str(move.product_uom_qty)
            
            data['nonce'] = '{"moveid":' + str(move.id) +'}'
            data['color'] = selfy.env.user.voodoo_device_color
            
            if selfy.env.user.voodoo_device_beep!='disabled':
                data['sound'] = selfy.env.user.voodoo_device_beep

            if selfy.env.user.voodoo_seconds and selfy.env.user.voodoo_seconds>0:
                data['seconds'] = selfy.env.user.voodoo_seconds

            selfy.with_delay(priority=0,max_retries=1).enqueue_voodooDeviceCall(dev_id,data)

        
        # Check if the destination location has a voodoo_device_id
        dev_id = move.location_dest_id.voodoo_device_id
        if dev_id:
            arrow = VoodooUtility.getArrow(move.location_dest_id)

            data = {}
            data['command']='flash'
            data['arrow']=arrow

            if selfy.env.user.voodoo_name and selfy.env.user.voodoo_name!='':
                data['line1'] = selfy.env.user.voodoo_name


            data['line2']="PUT"

            # if ' - ' in name:
            #     line1, line2 = name.split(' - ', 1)
            #     data['line3'] = line1
            #     data['line4'] = line2
            # else:
            #     data['line3'] = name
            data['line3'] = name

            if move.product_uom_qty % 1 == 0:
                data['quantity']= int(move.product_uom_qty)
            else:
                data['line4'] = 'Qty: '+ str(move.product_uom_qty)
                
            data['nonce'] = '{"moveid":' + str(move.id) +'}'
            data['color'] = selfy.env.user.voodoo_device_color

            if selfy.env.user.voodoo_device_beep!='disabled':
                data['sound'] = selfy.env.user.voodoo_device_beep

            if selfy.env.user.voodoo_seconds and selfy.env.user.voodoo_seconds>0:
                data['seconds'] = selfy.env.user.voodoo_seconds

            selfy.with_delay(priority=0,max_retries=1).enqueue_voodooDeviceCall(dev_id,data)