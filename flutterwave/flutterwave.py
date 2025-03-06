import environ

env = environ.Env()

environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')
PUBLIC_KEY = env('PUBLIC_KEY')

from rave_python import Rave, RaveExceptions, Misc
rave = Rave(PUBLIC_KEY, SECRET_KEY, usingEnv = False)

# Payload with pin
payload = {
  "cardno": "5531886652142950",
  "cvv": "564",
  "expirymonth": "09",
  "expiryyear": "32",
  'email': "begati19@gmail.com",
  'amount': "10",
#   'otp': "12345",
  'pin': "3310",
}

try:
    res = rave.Card.charge(payload)

    if res["suggestedAuth"]:
        arg = Misc.getTypeOfArgsRequired(res["suggestedAuth"])

        if arg == "pin":
            Misc.updatePayload(res["suggestedAuth"], payload, pin="3310")
        if arg == "address":
            Misc.updatePayload(res["suggestedAuth"], payload, address= {"billingzip": "07205", "billingcity": "Hillside", "billingaddress": "470 Mundet PI", "billingstate": "NJ", "billingcountry": "US"})
        
        res = rave.Card.charge(payload)

    if res["validationRequired"]:
        rave.Card.validate(res["flwRef"], "12345")  # Assuming '12345' is the OTP received

    res = rave.Card.verify(res["txRef"])
    print(res["transactionComplete"])

except RaveExceptions.CardChargeError as e:
    print(e.err["errMsg"])
    print(e.err["flwRef"])

except RaveExceptions.TransactionValidationError as e:
    print(e.err)
    print(e.err["flwRef"])

except RaveExceptions.TransactionVerificationError as e:
    print(e.err["errMsg"])
    print(e.err["txRef"])