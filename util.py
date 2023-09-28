
import logging
import requests

# from odoo.addons.component.core import Component
from odoo import models, api, _
# from odoo.addons.queue_job import job

from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)


class VoodooUtility:

    # _abstract = True
    # _register = False

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
        
    # @staticmethod
    # def notify_error(selfy, error_message):

    #     ICPSudo = selfy.env['ir.config_parameter'].sudo()

    #     # Get the current time
    #     now = datetime.now()

    #     # Define the rate limit (e.g., 1 message every minute)
    #     rate_limit = timedelta(minutes=1)

    #     # Retrieve the last error timestamp from ir.config_parameter
    #     last_error_timestamp = ICPSudo.get_param('voodoo.error_timestamp')

    #     if last_error_timestamp:
    #         last_error_timestamp = datetime.strptime(last_error_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    #     # Check if the last message was sent more than the rate limit ago
    #     if not last_error_timestamp or now - last_error_timestamp > rate_limit:
    #         # Send the message to the current user
    #         general_channel = selfy.env['mail.channel'].sudo().search([('name', '=', 'general')], limit=1)
    #         if general_channel:
    #             # Post a message to the General channel
    #             _logger.info("Posted to general!")
    #             general_channel.message_post(body=error_message, subject=error_message, 
    #                                         message_type='comment', subtype_xmlid="mail.mt_comment")
    #         # Update the timestamp of the last error message sent
    #         ICPSudo.set_param('voodoo.error_timestamp', str(now))
    #     else:
    #         _logger.error("Too soon for another warning to user.")

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





                arrow = VoodooUtility.getArrow(location)  # note this is singular--> ie an object!
                data['arrow']=arrow

                if name:
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

                    data['statica']='various'
                    data['staticb']='items'

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


            try:
                VoodooUtility.voodooDeviceCall(selfy,deviceid,data)
            except Exception as e:
                _logger.error(f"VoodooDeviceCall exception: {str(e)}")



