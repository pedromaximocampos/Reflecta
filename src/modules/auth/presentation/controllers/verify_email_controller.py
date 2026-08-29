from src.modules.auth.application.use_cases.verify_email.iverify_email_verification import IVerifyEmailVerification
from src.presentation.http_types import HttpRequest, HttpResponse
from src.presentation.interfaces.controller_interface import IControllerInterface


class VerifyEmailController(IControllerInterface):
    def __init__(self, verify_email_use_case: IVerifyEmailVerification):
        self.verify_email_use_case = verify_email_use_case


    async def handle_request(self, request: HttpRequest) -> HttpResponse:

        code = request.query_params.get("code", None)

        if code is None:
            return HttpResponse(status_code=400, body={"error": "Verification code is required"})

        output = await self.verify_email_use_case.execute(code)

        return HttpResponse(status_code=200, body={"message": output.message})
