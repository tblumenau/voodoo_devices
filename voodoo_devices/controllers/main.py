from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class ExternalRpcController(http.Controller):
    """Robust external callback endpoint."""

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
        Accepts:
          - nonce as JSON string: '{"moveid":123}'
          - nonce as dict: {"moveid":123}
          - nonce as plain numeric string: "123"
          - nonce as int: 123
        """
        if nonce is None:
            return None

        # dict form
        if isinstance(nonce, dict):
            mid = nonce.get("moveid")
            try:
                return int(mid) if mid is not None else None
            except (TypeError, ValueError):
                return None

        # int/float form
        if isinstance(nonce, (int, float)):
            try:
                return int(nonce)
            except (TypeError, ValueError):
                return None

        # string form
        if isinstance(nonce, str):
            s = nonce.strip()
            if not s:
                return None

            # try JSON first
            if s.startswith("{") and s.endswith("}"):
                try:
                    obj = json.loads(s)
                    if isinstance(obj, dict):
                        mid = obj.get("moveid")
                        return int(mid) if mid is not None else None
                except Exception:
                    pass

            # fallback numeric string
            try:
                return int(s)
            except ValueError:
                return None

        return None

    @staticmethod
    def _get_payload():
        """
        Unified payload extraction:
          1) request.jsonrequest when available
          2) raw body JSON parse
          3) kwargs fallback
        Returns dict.
        """
        # 1) If JSON dispatcher/request provides jsonrequest
        jr = getattr(request, "jsonrequest", None)
        if isinstance(jr, dict):
            return jr

        # 2) Parse raw body for plain HTTP JSON posts
        try:
            raw = request.httprequest.get_data(cache=False, as_text=True) or ""
            if raw:
                obj = json.loads(raw)
                if isinstance(obj, dict):
                    return obj
        except Exception:
            pass

        # 3) Last resort
        return {}

    @http.route(
        "/external_rpc/receive",
        type="http",              # robust for external JSON webhooks
        auth="user",              # keep your current auth model
        methods=["POST"],
        csrf=False
    )
    def receive_call_back(self, **kwargs):
        try:
            data = self._get_payload()

            # Merge kwargs as fallback without clobbering explicit payload keys
            if kwargs:
                for k, v in kwargs.items():
                    data.setdefault(k, v)

            qty = self._to_float(data.get("qty"))
            ack = self._to_bool(data.get("acknack"))
            move_id = self._extract_move_id_from_nonce(data.get("nonce"))

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
                return request.make_json_response({
                    "status": "error",
                    "message": "Missing or invalid moveid in nonce"
                }, status=400)

            move = request.env["stock.move"].browse(move_id)
            if not move.exists():
                return request.make_json_response({
                    "status": "error",
                    "message": f"Move not found: {move_id}"
                }, status=404)

            # Keep your existing target field
            move.write({"quantity_done": qty})

            return request.make_json_response({
                "status": "success",
                "message": "Quantity updated successfully",
                "move_id": move_id,
                "quantity_done": qty
            })

        except Exception as e:
            _logger.exception("external_rpc.receive failed")
            return request.make_json_response({
                "status": "error",
                "message": "Unexpected server error",
                "detail": str(e),
            }, status=500)


# COOKIE_FILE=$(mktemp) && wget --save-cookies $COOKIE_FILE --post-data 'login=your_login&password=your_password' 
# --keep-session-cookies http://your-odoo-instance-url/web/session/authenticate && wget --load-cookies $COOKIE_FILE --post-data 
# '{"jsonrpc": "2.0", "method": "call", "params": {"json_data": "{\"nonce\": \"{\\\"moveId\\\":1}\", \"qty\": 10}"} }' 
# --header='Content-Type: application/json' -O- http://your-odoo-instance-url/external_rpc/receive && rm $COOKIE_FILE
