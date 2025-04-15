from fastapi import Request
import json

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
                    "phone": phone_number
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
