from common.utils import *
from routes.userfrontendapis.users import users_route
from routes.captainadminfrontapis.captains import *


__init__=APIRouter()


#################### user routes #################
__init__.include_router(users_route,prefix="/users")
#################### user routes #################


#################### captain routes #################
__init__.include_router(captain_route,prefix="/captains")
#################### captain routes #################