from odoo import http
from odoo.http import request
import json
import logging
import hmac

_logger = logging.getLogger(__name__)


class ExternalRpcController(http.Controller):
    """
    Generic external callback endpoint with X-API-KEY auth.

    Expected headers:
      X-API-KEY: <shared secret>

    Expected JSON body (example):
      {
        "qty": 3,
        "acknack": true,
        "nonce": "{\"moveid\": 123}"
      }
    """

    # ---------------------------
    # Helpers
    # ---------------------------
    @staticmethod
    def _to_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return val.strip().lower() in {"1", "true", "t", "yes", "y", "on", "ack", "ok"}
        return False

    @staticmethod
    def _to_float(val):
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return None
            try:
                return float(s)
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_move_id_from_nonce(nonce):
        """
        Accepts nonce as:
          - dict: {"moveid": 123}
          - JSON string: '{"moveid":123}'
          - numeric string: "123"
          - int/float: 123
        """
        if nonce is None:
            return None

        if isinstance(nonce, dict):
            mid = nonce.get("moveid")
            try:
                return int(mid) if mid is not None else None
            except (TypeError, ValueError):
                return None

        if isinstance(nonce, (int, float)):
            try:
                return int(nonce)
            except (TypeError, ValueError):
                return None

        if isinstance(nonce, str):
            s = nonce.strip()
            if not s:
                return None

            if s.startswith("{") and s.endswith("}"):
                try:
                    obj = json.loads(s)
                    if isinstance(obj, dict):
                        mid = obj.get("moveid")
                        return int(mid) if mid is not None else None
                except Exception:
                    pass

            try:
                return int(s)
            except ValueError:
                return None

        return None

    @staticmethod
    def _get_payload(kwargs):
        """
        Tries:
          1) request.jsonrequest (if available)
          2) raw body JSON parse
          3) kwargs fallback
        """
        # 1) JSON dispatcher payload
        jr = getattr(request, "jsonrequest", None)
        if isinstance(jr, dict):
            payload = dict(jr)
        else:
            payload = {}

        # 2) raw body fallback
        if not payload:
            try:
                raw = request.httprequest.get_data(cache=False, as_text=True) or ""
                if raw:
                    obj = json.loads(raw)
                    if isinstance(obj, dict):
                        payload = obj
            except Exception:
                pass

        # 3) kwargs fallback (do not overwrite payload keys)
        if kwargs:
            for k, v in kwargs.items():
                payload.setdefault(k, v)

        return payload

    @staticmethod
    def _consteq(a, b):
        """Constant-time compare for secrets."""
        if a is None or b is None:
            return False
        return hmac.compare_digest(str(a), str(b))

    @staticmethod
    def _get_expected_api_key():
        """
        Pull from Odoo system parameter:
          key: voodoo_devices.external_api_key
        Set via Settings > Technical > Parameters > System Parameters
        """
        icp = request.env["ir.config_parameter"].sudo()
        return icp.get_param("voodoo_devices.external_api_key", default="")

    def _is_replay(self, nonce_value):
        """
        Optional replay detection hook.
        Return True to reject duplicates.
        Current implementation: disabled (always False).

        If you want strict replay protection, create a small model storing
        nonce + timestamp and reject duplicates in a time window.
        """
        _ = nonce_value
        return False

    # ---------------------------
    # Route
    # ---------------------------
    @http.route(
        "/external_rpc/receive",
        type="http",
        auth="public",          # Public endpoint + API key auth
        methods=["POST"],
        csrf=False
    )
    def receive_call_back(self, **kwargs):
        try:
            # 1) API key check
            provided_api_key = request.httprequest.headers.get("X-API-KEY")
            expected_api_key = self._get_expected_api_key()

            if not expected_api_key:
                _logger.error("Webhook API key is not configured (voodoo_devices.external_api_key).")
                return request.make_json_response(
                    {"status": "error", "message": "Server not configured"},
                    status=500
                )

            if not self._consteq(provided_api_key, expected_api_key):
                return request.make_json_response(
                    {"status": "error", "message": "Unauthorized"},
                    status=401
                )

            # 2) Parse payload
            data = self._get_payload(kwargs)

            qty = self._to_float(data.get("qty"))
            ack = self._to_bool(data.get("acknack"))
            nonce_raw = data.get("nonce")
            move_id = self._extract_move_id_from_nonce(nonce_raw)

            # 3) Optional replay guard
            if self._is_replay(nonce_raw):
                return request.make_json_response(
                    {"status": "error", "message": "Replay detected"},
                    status=409
                )

            # 4) Business rules
            if not ack:
                return request.make_json_response({
                    "status": "success",
                    "message": "ACK not asserted; quantity not updated"
                })

            if qty is None or qty <= 0:
                return request.make_json_response({
                    "status": "success",
                    "message": "Invalid/non-positive qty; quantity not updated"
                })

            if not move_id:
                return request.make_json_response(
                    {"status": "error", "message": "Missing or invalid moveid in nonce"},
                    status=400
                )

            move = request.env["stock.move"].sudo().browse(move_id)
            if not move.exists():
                return request.make_json_response(
                    {"status": "error", "message": f"Move not found: {move_id}"},
                    status=404
                )

            # Odoo version note:
            # Some versions use qty_done on move lines; keeping your original field by request.
            move.write({"quantity_done": qty})

            return request.make_json_response({
                "status": "success",
                "message": "Quantity updated successfully",
                "move_id": move_id,
                "quantity_done": qty
            })

        except Exception as e:
            _logger.exception("external_rpc.receive failed")
            return request.make_json_response(
                {"status": "error", "message": "Unexpected server error", "detail": str(e)},
                status=500
            )


# COOKIE_FILE=$(mktemp) && wget --save-cookies $COOKIE_FILE --post-data 'login=your_login&password=your_password' 
# --keep-session-cookies http://your-odoo-instance-url/web/session/authenticate && wget --load-cookies $COOKIE_FILE --post-data 
# '{"jsonrpc": "2.0", "method": "call", "params": {"json_data": "{\"nonce\": \"{\\\"moveId\\\":1}\", \"qty\": 10}"} }' 
# --header='Content-Type: application/json' -O- http://your-odoo-instance-url/external_rpc/receive && rm $COOKIE_FILE