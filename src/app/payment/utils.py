def verify_payment(ref_id:str):
    paystack_url = settings.PAYMENT_URL
    url_path = paystack_url + f"transaction/verify/{ref_id}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(url_path, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data['status'], response_data['data']
    
    response_data = response.json()
    return response_data['status'], response_data['data'] 