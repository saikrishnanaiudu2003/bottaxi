from common.utils import *
from models import *

captain_route = APIRouter()
logger = logging.getLogger(__name__)

@captain_route.get("/captain_create")
async def create_captain():
    return {"captain Route"}

@captain_route.post("/login")
async def register_captain(request: Request):
    data_status = {"response": "", "status": "0"}
    
    try:
        body = await request.json()
        phone_number = body.get('phone_number')
        userName = body.get('userName')
        otp_check_id = body.get('otpCheckingId')
        email = body.get('email')
        language = body.get('language')  # Assuming 'language' is part of the request body
        city = body.get('city')  # Assuming 'city' is part of the request body
        last_login_ip= body.get('lastLoginIp')
        last_login= body.get('last_login')
        mobileInformation=body.get('mobileInformation')

        if not otp_check_id:
            data_status['response'] = "User OTP check ID is required."
            return data_status
        
        otp_record = otpChecking.objects(id=ObjectId(otp_check_id)).first()
        if not otp_record:
            data_status['response'] = "Invalid OTP check ID or OTP is already used."
            return data_status
        
        # Find an existing user with the given phone number and status = 1
        existing_user = captains.objects(captainMobileNumber=phone_number, status=1).first()

        if existing_user:
            # If the user exists, update the user details
            existing_user.captainName = userName
            existing_user.captainEmail = email
            existing_user.captainLanguage = language
            existing_user.captainCity = city
            existing_user.isNewCaptain = False  # Mark user as no longer new
            existing_user.save()  # Save the updated user

            payload = {
                "sub": str(existing_user.id),
                "phone_number": existing_user.captainMobileNumber,
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

            return {
                "response": {
                    "captainId": str(existing_user.id),
                    "captainName": existing_user.captainName,
                    "phone_number": existing_user.captainMobileNumber,
                    "status": existing_user.status,
                    "captainEmail": existing_user.captainEmail,
                    "isNewCaptain": existing_user.isNewCaptain
                },
                "token": token,
                "status": "1"  # Status for existing user
            }
        else:
            # Create a new user if the user doesn't exist
            user_count = captains.objects.count()  # Get the total count of captains
            new_user = captains(
                userUniqueId=user_count + 1,
                captainMobileNumber=phone_number,
                captainName=userName,
                captainEmail=email,
                captainLanguage=language,
                captainCity=city,
                status=1,
                last_login_ip=last_login_ip,
                last_login=last_login,
                mobileInformation=mobileInformation,
                isNewCaptain=True,
                created_on=datetime.now()
            )
            new_user.save()

            payload = {
                "sub": str(new_user.id),
                "phone_number": new_user.captainMobileNumber,
                "exp":datetime.utcnow() + timedelta(hours=1)  # Token expiration
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

            return {
                "status": "1",  # Status for new user
                "userUniqueId": str(new_user.userUniqueId),
                "isNewCaptain": True,
                "token": token
            }

    except Exception as e:
        logger.exception("Internal server error occurred: %s", e)
        data_status['response'] = "Internal Server Error"
        return data_status

@captain_route.post("/add_captain_vehicle")
async def add_captain_vehicle(
    captainId: str = Form(...),
    vehicleImage: UploadFile = File(...),
    aadharImage: UploadFile = File(...),
    drivingLicenseImage: UploadFile = File(...),
    captainImage: UploadFile = File(...),
    vechicleRegsterCardImage: UploadFile = File(...),
    vechicleImages: List[UploadFile] = File(...),
    vechicleNumberPlate: str = Form(...),
    vehicleType: str = Form(...),
    captainAdress: str = Form(...)
):
    data_status = {"response": "", "status": "0"}
    try:
        # Validate captainId
        if not captainId:
            data_status['response'] = "Captain ID is required."
            return data_status

        # Check if captain exists
        existing_captain = captains.objects(id=ObjectId(captainId), status=1).first()
        if not existing_captain:
            data_status['response'] = "Invalid Captain ID or Captain is not registered."
            return data_status

        # Save individual images
        vehicle_image_path = await save_image(vehicleImage, IMAGE_FOLDER)
        aadhar_image_path = await save_image(aadharImage, IMAGE_FOLDER)
        driving_license_image_path = await save_image(drivingLicenseImage, IMAGE_FOLDER)
        captain_image_path = await save_image(captainImage, IMAGE_FOLDER)
        vehicle_reg_card_image_path = await save_image(vechicleRegsterCardImage, IMAGE_FOLDER)

        # Save multiple vehicle images
        vechicle_images_paths = []
        for file in vechicleImages:
            vechicle_images_paths.append(await save_image(file, IMAGE_FOLDER))

        # Save data to the database
        captain_data = captainData(
            userId=existing_captain.id,
            captainId=existing_captain,
            vehicleImage=vehicle_image_path,
            aadharImage=aadhar_image_path,
            drivingLicenseImage=driving_license_image_path,
            captainImage=captain_image_path,
            vechicleRegsterCardImage=vehicle_reg_card_image_path,
            vechicleImages=vechicle_images_paths,
            vechicleNumberPlate=vechicleNumberPlate,
            vehicleType=vehicleType,
            captainAdress=captainAdress
        )
        captain_data.save()

        return {
            "response": "Captain vehicle added successfully. Please wait, our team will contact you.",
            "status": "1"
        }

    except ValueError as ve:
        logger.exception("File format error: %s", ve)
        data_status['response'] = str(ve)
        return data_status

    except ValidationError as ve:
        logger.exception("Validation error: %s", ve)
        data_status['response'] = "Validation failed for input data."
        return data_status

    except Exception as e:
        logger.exception("Error in processing request: %s", e)
        data_status['response'] = "An unexpected error occurred while processing your request."
        return data_status