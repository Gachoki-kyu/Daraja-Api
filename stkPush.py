import requests
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
from datetime import datetime
import pytz
import accessToken # Assuming access_token is defined in accessToken.py
# Note: The access_token import is commented out to avoid errors in this standalone script.
app = FastAPI()

# Simulate `include 'accessToken.php';` by defining or importing access_token
  # Replace this with the token you got earlier


class STKpushRequest(BaseModel):
    phone: str
    amount: int



def get_timestamp():
    tz = pytz.timezone('Africa/Nairobi')
    return datetime.now(tz).strftime('%Y%m%d%H%M%S')

# Required parameters
process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
business_short_code = '174379'
passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
callback_url = 'https://523a-41-139-239-91.ngrok-free.app/stkcallback'
phone = '254799054755'  # e.g. '2547XXXXXXXX'
amount = 1
account_reference = 'bena'
transaction_description = 'Payment for testing'

@app.post("/stkpush")
def initiate_stk_push(request: STKpushRequest):
    # Generate password (base64 encoded string)
    timestamp = get_timestamp()
    data_to_encode = business_short_code + passkey + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()
    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {accessToken.access_token}'
    }

    # Construct the request body
    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": business_short_code,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_description
    }

    # Make the request
    response = requests.post(process_request_url, json=payload, headers=headers)

    # Output the response
    return JSONResponse(content=response.json(), status_code=response.status_code)
@app.post("/stkcallback")
async def stk_callback(request: Request):
    body = await request.body()
    log_file = 'stkpush_response.json'
    
    # Append the callback JSON to a file
    with open(log_file, 'ab') as log:
        log.write(body + b'\n')  # Add newline for readability
    try:
        # Parse data fields from callback
        callback = data['Body']['stkCallback']
        merchant_request_id = callback.get('MerchantRequestID')
        checkout_request_id = callback.get('CheckoutRequestID')
        result_code = callback.get('ResultCode')
        result_desc = callback.get('ResultDesc')

        # Extract metadata only if payment was successful
        if result_code == 0:
            metadata = callback.get('CallbackMetadata', {}).get('Item', [])
            amount = metadata[0]['Value']
            receipt_number = metadata[1]['Value']
            transaction_date = metadata[3]['Value']
            phone_number = metadata[4]['Value']

            # Here you could insert into a DB or trigger something else
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Payment was successful",
                    "merchantRequestID": merchant_request_id,
                    "receipt": receipt_number,
                    "amount": amount,
                    "phone": phone_number,
                    "checkoutRequestID": checkout_request_id
                }
            )
        else:
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "Payment failed", "reason": result_desc}
            )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Callback processing failed: {str(e)}"}
        )
# MPESA Transaction Status Query
# Required parameters

MPESA_SHORTCODE = '174379'
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
MPESA_QUERY_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
CHECKOUT_REQUEST_ID = "ws_CO_15042025100510683799054755"# This should be set to the CheckoutRequestID you received in the callback

@app.get("/mpesa/transaction-status")
def query_transaction_status():

    # Set timezone to Africa/Nairobi
    timezone = pytz.timezone("Africa/Nairobi")
    timestamp = datetime.now(timezone).strftime("%Y%m%d%H%M%S")

    # Encode password
    data_to_encode = MPESA_SHORTCODE + MPESA_PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {accessToken.access_token}"
    }

    # Payload
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": CHECKOUT_REQUEST_ID
    }

    # Make the request
    response = requests.post(MPESA_QUERY_URL, headers=headers, json=payload)
    result = response.json()

    # Handle result
    result_code = result.get("ResultCode")
    if result_code == 0:
        message = "Transaction was successful"
    elif result_code == 1:
        message = "Insufficient funds"
    elif result_code == 1032:
        message = "Transaction canceled by user"
    else:
        message = "Timeout completing transaction"

    return {"message": message, "result": result}