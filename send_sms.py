url = "https://www.fast2sms.com/dev/bulk"


payload = "sender_id=FSTSMS&message={}&language=english&route=p&numbers={}"

headers = {
    'authorization': "0bZiT83nohmp7IqHvrQGxEXuAJcCFOg6YULkN4tWldaS2Dez5Vmfu0ZI1pgl8NUcCMHWARG5Kq3t9exS",
    'cache-control': "no-cache",
    'content-type': "application/x-www-form-urlencoded"
    }

# response = requests.request("POST", url, data=payload.format(msg,number), headers=headers)

# print(response.text)