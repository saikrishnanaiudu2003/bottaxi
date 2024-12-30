from common.utils import *
from models import *



users_route=APIRouter()
logger = logging.getLogger(__name__)

@users_route.get("/create")
async def create_user():
    return {"User Route"}


@users_route.post("/users_get_otp")
async def users_get_otp(request: Request):
    data_status = {"response": "", "status": "0"}
    
    try:
        body = await request.json()
        phone_number = body.get('phone_number')

        if not phone_number or not validate_phone_number(phone_number):
            data_status['response'] = "Phone number is required and must be valid."
            return data_status

        # otpChecking = client.get_collection("otpChecking")
        # existing_record = await otpChecking.objects({"phone_number": phone_number})

        otp_code = generate_random_otp()
        message = f"Your Verification Code: {otp_code}"
        print(otp_code)

        try:
            await send_otp(phone_number, otp_code)  
        except Exception as e:
            data_status['response'] = "Failed to send OTP"
            return data_status

        created_on = datetime.now()

        otp_check_id = None  

       
        otp_record = otpChecking(
            phone_number= phone_number,
            otp_code=str(otp_code),
            attempts= 0,
            created_on= created_on
        )
        result=otp_record.save()
        otp_check_id = str(result.id)  

        data_status = {
            "response": "OTP sent successfully",
            "status": "1",
            "otp_code": otp_code,
            "otpCheckId": otp_check_id  
        }

    except Exception as e:
        logger.exception("Internal server error occurred: %s", e)
        data_status['response'] = "Internal Server Error"
    
    return data_status

@users_route.post("/check_otp")
async def check_otp(request: Request):
    data_status = {"response": "", "status": "0"}
    
    try:
        body = await request.json()
        otp_code = body.get('otp_code')
        otp_check_id = body.get('otpCheckId')
        
        if not otp_code or not otp_check_id:
            data_status['response'] = "OTP code and OTP check ID are required."
            return data_status
        
        otp_record =otpChecking.objects(id=ObjectId(otp_check_id)).first()
        if not otp_record:
            data_status['response'] = "Invalid OTP check ID or OTP is already used."
            return data_status
        otp_creation_time = otp_record["created_on"]
        expiry_time = otp_creation_time + timedelta(seconds=60)

        if datetime.utcnow() > expiry_time:
            data_status["result"] = "OTP has expired"
            return data_status

        if otp_record["otp_code"] == str(otp_code):
            # otpChecking["id"]=otp_check_id
            otp_record["otp_verified"]=True
            data_status["response"] = 1
            data_status["result"] = "OTP verified successfully"
        else:
            data_status["result"] = "Invalid OTP code"
    
    except Exception as e:
        logger.exception("Internal server error occurred: %s", e)
        data_status['response'] = "Internal Server Error"

    return data_status

@users_route.post("/login")
async def login_user(request: Request):
    data_status = {"response": "", "status": "0"}
    
    try:
        body = await request.json()
        phone_number = body.get('phone_number')
        userName = body.get('userName')
        otp_check_id = body.get('otpCheckingId')
        email = body.get('email')
        lastLogin = body.get('lastLogin')
        last_login_ip = body.get('lastLogin')
        mobileInformation = body.get('mobileInformation')

        if not otp_check_id:
            data_status['response'] = "User OTP check ID is required."
            return data_status
        
        otp_record = otpChecking.objects(id=ObjectId(otp_check_id)).first()
        if not otp_record:
            data_status['response'] = "Invalid OTP check ID or OTP is already used."
            return data_status
        
        existing_user = Users.objects(phone_number=phone_number, status=1).first()

        if existing_user:
            existing_user.userName = userName
            existing_user.userEmail = email
            existing_user.isNewUser = False
            existing_user.save()

            userId=str(existing_user.id)
            get_token=create_token((userId))

            # Generate JWT Token
            # payload = {
            #     "sub": str(existing_user.id),
            #     "phone_number": existing_user.phone_number,
            #     "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            # }
            # token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

            return {
                "response": {
                    "userId":str(existing_user.id),
                    "userName": existing_user.userName,
                    "phone_number": existing_user.phone_number,
                    "status": existing_user.status,
                    "userEmail": existing_user.userEmail,
                    "isNewUser": existing_user.isNewUser
                },
                "token": get_token,
                "status": "1"
            }
        else:
            user_count = Users.objects.count()
            new_user = Users(
                userUniqueId=user_count + 1,
                phone_number=phone_number,
                userName=userName,
                userEmail=email,
                status=1,
                last_login=lastLogin,
                last_login_ip=last_login_ip,
                mobileInformation=mobileInformation,
                isNewUser=True,
                created_on=datetime.now()
            )
            new_user.save()

            userId=str(new_user.id)
            get_token=create_token((userId))

            # Generate JWT Token for new user
            # payload = {
            #     "sub": str(new_user.id),
            #     "phone_number": new_user.phone_number,
            #     "exp": datetime.utcnow() + timedelta(hours=1)  # Token expiration
            # }
            # token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

            return {
                "status": "1",
                "userUniqueId": str(new_user.userUniqueId),
                "isNewUser": True,
                "token": get_token
            }

    except Exception as e:
        logger.exception("Internal server error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@users_route.post("/get_all_vechicles")
async def get_all_vechicles(user_id: str = Depends(get_current_user)):
    try:
        # Validate if user exists
        user = Users.objects(id=ObjectId(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get unique vehicle types
        vehicle_types = captainData.objects().distinct('vehicleType')
        
        return {
            "status": "1",
            "vehicleTypes": vehicle_types
        }
    except Exception as e:
        logger.exception("Failed to fetch vehicle types: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
