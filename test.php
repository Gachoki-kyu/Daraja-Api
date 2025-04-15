<?php
$consumerKey = 'your_consumer_key';
$consumerSecret = 'your_consumer_secret';
$access_token_url = 'https://sandbox.safaricom.com/oauth/v1/generate?grant_type=client_credentials';
$headers = ['Content-Type:application/json; charset=utf-8'];
$curl = curl_init($access_token_url);
curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($curl, CURLOPT_HEADER, false);
curl_setopt($curl, CURLOPT_USERPWD, $consumerKey . ':' . $consumerSecret);
$result = curl_exec($curl);
$status = curl_getinfo($curl, CURLINFO_HTTP_CODE);
$result = json_decode($result);
echo $access_token = $result->access_token;
curl_close($curl);

// stk push
<?php
include 'accessToken.php'
date_default_timezone_set('Africa/Nairobi');
$processrequesturl = 'https://sandbox.safaricom.com/mpesa/stkpush/v1/processrequest';
$businessshortcode = '174379';
$callbackurl = 'https://example.com/callback';
$passkey = 'your_passkey';
$timestamp = date('YmdHis');
$password = base64_encode($businessshortcode . $passkey . $timestamp);
$phone = ''
$amount = 1;
$accountReference = 'test123';
$transactionDescription = 'Payment for testing';
$stkpushheader = ['Content-Type:application/json', 'Authorization:Bearer ' . $access_token];
$curl = curl_init();
curl_setopt($curl, CURLOPT_URL, $processrequesturl);
curl_setopt($curl, CURLOPT_HTTPHEADER, $stkpushheader);
$curl_post_data = [
    'BusinessShortCode' => $businessshortcode,
    'Password' => $password,
    'Timestamp' => $timestamp,
    'TransactionType' => 'CustomerPayBillOnline',
    'Amount' => $amount,
    'PartyA' => $phone,
    'PartyB' => $businessshortcode,
    'PhoneNumber' => $phone,
    'CallBackURL' => $callbackurl,
    'AccountReference' => $accountReference,
    'TransactionDesc' => $transactionDescription
];

$data_string = json_encode($curl_post_data);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($curl, CURLOPT_POST, true);
curl_setopt($curl, CURLOPT_POSTFIELDS, $data_string);
$curl_response = curl_exec($curl);

// callback
<?php
header('Content-Type: application/json');
$stkCallback = file_get_contents('php://input');
$logfile = 'stkpush_response.json';
$log = fopen($logfile, 'a');
fwrite($log, $stkCallback);
fclose($log);

$data = json_decode($stkCallback, true);
$merchantRequestID = $data['Body']['stkCallback']['MerchantRequestID'];
$checkoutRequestID = $data['Body']['stkCallback']['CheckoutRequestID'];
$resultCode = $data['Body']['stkCallback']['ResultCode'];
$resultDesc = $data['Body']['stkCallback']['ResultDesc'];
$amount = $data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'];
$mpesaReceiptNumber = $data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'];
$transactionDate = $data['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value'];
$phoneNumber = $data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'];

//check if the payment was successful


// query
<?php
date_default_timezone_set('Africa/Nairobi');
$query_url = 'https://sandbox.safaricom.com/mpesa/transactionstatus/v1/query';
$shortcode = '174379';
$timestamp = date('YmdHis');
$passkey = 'your_passkey';
$password = base64_encode($shortcode . $passkey . $timestamp);
$checkoutRequestID = 'your_checkout_request_id';
$queryheader = ['Content-Type:application/json', 'Authorization:Bearer ' . $access_token];
$curl = curl_init();
curl_setopt($curl, CURLOPT_URL, $query_url);
curl_setopt($curl, CURLOPT_HTTPHEADER, $queryheader);
$curl_post_data = array(
    'BusinessShortCode' => $shortcode,
    'Password' => $password,
    'Timestamp' => $timestamp,
    'CheckoutRequestID' => $checkoutRequestID,
);
$data_string = json_encode($curl_post_data);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($curl, CURLOPT_POST, true);
curl_setopt($curl, CURLOPT_POSTFIELDS, $data_string);
$curl_response = curl_exec($curl);
$data_to = json_decode($curl_response, true);

if (isset($data_to->Resultcode)) {
    $resultCode = $data_to->Resultcode;
    if ($resultCode == 0) {
        // Payment was successful
        $message = "Transaction was successful";
    } elseif ($resultCode == 1) {
        // Payment failed
        $message = "Insufficient funds";
    } elseif ($resultCode == 1032) {
        // Payment pending
        $message = "Transaction canceled by user";
    } else {
        // Unknown result code
        $message = "Timeout completing transaction";
    }
    
}
echo $message;