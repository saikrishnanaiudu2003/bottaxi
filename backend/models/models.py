from mongoengine import *

class Users(Document):
    userUniqueId=IntField(default=00)
    phone_number= StringField()
    userName= StringField()
    userEmail= StringField()
    isNewUser= BooleanField(default=True)
    last_login= StringField()
    last_logout= StringField()
    last_login_ip= StringField()
    last_logout_ip= StringField()
    mobileInformation= ListField()
    created_on= DateTimeField()
    status=IntField(default=0)
    device_info = ListField()  # To store device information

class otpChecking(Document):
    phone_number= StringField()
    otp_code= StringField()
    attempts=IntField(default=0)
    otp_verified=BooleanField(default=True)
    created_on= DateTimeField()

class captains(Document):
    userUniqueId=IntField(default=00)
    userId=ReferenceField("Users")
    captainName=StringField()
    captainEmail=StringField()
    captainMobileNumber=StringField()
    captainLanguage=StringField()
    captainCity=StringField()
    isNewCaptain=BooleanField(default=True)
    captainActive=IntField(default=0)
    status=IntField(default=0)
    created_on= DateTimeField()
    last_login= StringField()
    last_logout= StringField()
    last_login_ip= StringField()
    last_logout_ip= StringField()
    mobileInformation= ListField()

class captainData(Document):
    userId=ReferenceField("Users")
    captainId=ReferenceField("captains")
    vehicleImage=StringField()
    aadharImage=StringField()
    drivingLicenseImage=StringField()
    captainImage=StringField()
    vechicleRegsterCardImage=StringField()
    vechicleImages=ListField()
    vehicleType=StringField()
    vechicleNumberPlate=StringField()
    captainAdress=StringField()

class vehicles(Document):
    userId=ReferenceField("Users")
    captainsId=ReferenceField("captains")
    vehicleUniqueId=IntField(default=0)
    # vehicleName=StringField()
    vehicleNumber=StringField()
    vehicleType=StringField()
    vechicleImages=ListField()

    


    