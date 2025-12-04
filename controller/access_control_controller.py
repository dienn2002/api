from fastapi import APIRouter
from persistences.dto.app_dto import ApprovalRequest, AccessControlRequest, CheckPlateNumber, VerifyBackup
from services.access_control_service import AccessControlService

router = APIRouter(prefix="/access-control", tags=["Access Control"])
access_service = AccessControlService()


@router.post("/check-plate-number")
async def check_plate_number(request: CheckPlateNumber):
    return await access_service.check_plate_number(request)


@router.post("/request")
async def access_request(request: AccessControlRequest):
    return await access_service.process_request(request)


@router.post("/success")
async def approval_success(request: ApprovalRequest):
    return await access_service.process_success(request)


@router.post("/verify-backup")
async def verify_backup(request: VerifyBackup):
    return await access_service.verify_backup(request)
